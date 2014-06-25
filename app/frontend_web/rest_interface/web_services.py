#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
__author__ = 'Tom DuBois'
#************************
#DESCRIPTION:
# This file contains the core web services to deliver json objects to the
# frontend website
#************************
#*************************************************************************

import json
from collections import defaultdict
import utils.database.web_persistence as WP
import utils.streaming.stream_processor as SP
import utils.streaming.http_responder as HTTP
import utils.streaming.http_helper as HH
import asyncio
import bcrypt
import utils.crypto.authorization_key as AK
import maven_logging as ML
import maven_config as MC
import re

CONFIG_PERSISTENCE = 'persistence'

CONTEXT_USER = 'user'
CONTEXT_PROVIDER = 'provider'
CONTEXT_DATE = 'date'
CONTEXT_DATERANGE = 'daterange'
CONTEXT_PATIENTLIST = 'patients'
CONTEXT_DEPARTMENT = 'department'
CONTEXT_ORDERTYPE = 'ordertype'
CONTEXT_KEY = 'userAuth'
CONTEXT_ENCOUNTER = 'encounter'
CONTEXT_CUSTOMERID = 'customer_id'
CONTEXT_PROVIDER = 'provider'

LOGIN_TIMEOUT = 60 * 60  # 1 hour
AUTH_LENGTH = 44  # 44 base 64 encoded bits gives the entire 256 bites of SHA2 hash


class LoginError(Exception):
    pass


class FrontendWebService(HTTP.HTTPProcessor):
    def __init__(self, configname):
        HTTP.HTTPProcessor.__init__(self, configname)
        try:
            persistence_name = self.config[CONFIG_PERSISTENCE]
        except KeyError:
            raise MC.InvalidConfig('some real error')

        self.stylesheet = 'original'
        self.costbdtype = 'donut'  # this assignment isn't used yet
        self.add_handler(['POST'], '/login', self.post_login)  # REAL
        self.add_handler(['GET'], '/patients(?:/(\d+)-(\d+)?)?', self.get_patients)  # REAL
        self.add_handler(['GET'], '/patient_details', self.get_patient_details)  # REAL
        self.add_handler(['GET'], '/total_spend', self.get_total_spend)  # REAL
        self.add_handler(['GET'], '/spending', self.get_daily_spending)  # REAL
        self.add_handler(['GET'], '/alerts(?:/(\d+)-(\d+)?)?', self.get_alerts)  # REAL
        self.add_handler(['GET'], '/orders(?:/(\d+)-(\d+)?)?', self.get_orders)  # REAL
        self.add_handler(['GET'], '/autocomplete', self.get_autocomplete)  # FAKE
        self.add_handler(['GET'], '/hist_spending', self.get_hist_spend)  # REAL
        self.helper = HH.HTTPHelper([CONTEXT_USER, CONTEXT_PROVIDER], CONTEXT_KEY, AUTH_LENGTH)
        self.persistence_interface = WP.WebPersistence(persistence_name)

    def schedule(self, loop):
        HTTP.HTTPProcessor.schedule(self, loop)
        self.persistence_interface.schedule(loop)

    @asyncio.coroutine
    def get_autocomplete(self, _header, _body, qs, _matches, _key):
        return HTTP.OK_RESPONSE, json.dumps(['Maven']), None

    @asyncio.coroutine
    def hash_new_password(self, user, newpassword):
        if len(newpassword) < 8 or not re.search("[0-9]",newpassword) or not re.search("[a-z]",newpassword) or not re.search("[A-Z]",newpassword):
            raise LoginError('expiredPassword')
        salt = bcrypt.gensalt(4)
        ret = bcrypt.hashpw(bytes(newpassword, 'utf-8'), salt)
        try:
            yield from self.persistence_interface.update_password(user, ret)
        except:
            import traceback
            traceback.print_exc()
            raise LoginError('expiredPassword')

    @asyncio.coroutine
    def post_login(self, header, body, _qs, _matches, _key):
        info = json.loads(body.decode('utf-8'))

        user_and_pw = set((CONTEXT_USER, 'password')).issubset(info)
        prov_and_auth = set(('provider', 'customer', 'userAuth')).issubset(info)
        if not user_and_pw and not prov_and_auth:
            return HTTP.BAD_RESPONSE, b'', None

        desired = {k: k for k in [
                WP.Results.userid,
                WP.Results.customerid,
                WP.Results.provid,
                WP.Results.displayname,
                WP.Results.password,
                WP.Results.passexpired,
                WP.Results.userstate,
                #WP.Results.failedlogins,
                WP.Results.recentkeys,
                ]}
        attempted=None
        try:
            method = 'failed'
            user_info = {}
            #if header.get_headers().get('VERIFIED','SUCCESS') == 'SUCCESS': 
            if user_and_pw:
                attempted = info['user']
                try:
                    user_info = yield from self.persistence_interface.pre_login(desired, username=attempted)
                except IndexError:
                    raise LoginError('badLogin')
                passhash = user_info[WP.Results.password].tobytes()
                if not passhash or bcrypt.hashpw(bytes(info['password'], 'utf-8'), passhash[:29]) != passhash:
                    raise LoginError('badLogin')
                if user_info[WP.Results.passexpired] or 'newpassword' in info:
                    yield from self.hash_new_password(user_info[WP.Results.userid], info.get('newpassword',''))
                method = 'local'
            else:
                attempted = [info['provider'], info['customer']]
                try:  # this means that the password was a pre-authenticated link
                    AK.check_authorization(attempted, info['userAuth'], AUTH_LENGTH)
                except AK.UnauthorizedException:
                    raise LoginError('badLogin')
                user_info = yield from self.persistence_interface.pre_login(desired, 
                                                                            provider=attempted,
                                                                            keycheck='1m')
                method = 'forward'
                # was this auth key used recently
                if info['userAuth'] in user_info[WP.Results.recentkeys]:
                    raise LoginError('reusedLogin')

            # make sure this user exists and is active
            if not user_info[WP.Results.userstate] == 'active':
                raise LoginError('disabledUser')

                # at the point, the user has succeeded to login
            user = str(user_info[WP.Results.userid])
            provider = user_info[WP.Results.provid]
            user_auth = AK.authorization_key([user, provider], AUTH_LENGTH, LOGIN_TIMEOUT)
            if not self.stylesheet == 'original':
                self.stylesheet = 'original'

            ret = {CONTEXT_USER: user_info[WP.Results.userid], 'display': user_info[WP.Results.displayname],
                   'stylesheet': self.stylesheet, 'customer_id': user_info[WP.Results.customerid],
                   CONTEXT_PROVIDER: provider,
                   CONTEXT_USER: user,
                   'widgets': [
                    ['#fixed-topA-1-1', 'topBanner', 'topBanner.html'],
                    ['#fixed-topB-1-1', 'patientInfo'],
                    ['#fixed-topB-1-1', 'patientSearch'],
                    ['#rowA-1-1', 'patientList'],
                    ['#rowB-1-1', 'encounterSummary'],
                    ['#rowC-1-1', 'orderList'],
                    ['#rowD-1-1', 'costtable', 'costbreakdown-table.html'],
                    #['#rowD-1-1','costdonut','costbreakdown-donut.html'],
                    ['#rowE-1-1', 'spend_histogram'],
                    ['#floating-right', 'alertList', 'alertScroll.html'],
                    ], CONTEXT_KEY: user_auth}
            
            return HTTP.OK_RESPONSE, json.dumps(ret), None
        except LoginError as err:
            return HTTP.UNAUTHORIZED_RESPONSE, json.dumps({'loginTemplate': err.args[0]+".html"}), None
        finally:
            yield from self.persistence_interface.record_login(attempted,
                                                               method, header.get_headers().get('X-Real-IP'),
                                                               info['userAuth'] if method == 'forward' else None)

    patients_required_contexts = [CONTEXT_PROVIDER, CONTEXT_CUSTOMERID]
    patients_available_contexts = {CONTEXT_PROVIDER: str, CONTEXT_CUSTOMERID: int}

    ################ AK.authorization_key((user, x[1]), AUTH_LENGTH), 

    @asyncio.coroutine
    def get_patients(self, _header, _body, qs, matches, _key):
        context = self.helper.restrict_context(qs,
                                               FrontendWebService.patients_required_contexts,
                                               FrontendWebService.patients_available_contexts)
        provider = context[CONTEXT_PROVIDER]
        customerid = context[CONTEXT_CUSTOMERID]
        desired = {
            WP.Results.patientname: 'name',
            WP.Results.patientid: 'id',
            WP.Results.sex: 'gender',
            WP.Results.birthdate: 'DOB',
            WP.Results.diagnosis: 'diagnosis',
            WP.Results.cost: 'cost',
        }
        results = yield from self.persistence_interface.patient_info(desired, provider, customerid,
                                                                     limit=self.helper.limit_clause(matches))

        return HTTP.OK_RESPONSE, json.dumps(results), None

    patient_required_contexts = [CONTEXT_PROVIDER, CONTEXT_KEY, CONTEXT_PATIENTLIST, CONTEXT_CUSTOMERID]
    patient_available_contexts = {CONTEXT_PROVIDER: str, CONTEXT_KEY: str, CONTEXT_PATIENTLIST: str,
                                  CONTEXT_CUSTOMERID: int, CONTEXT_ENCOUNTER: str}

    @asyncio.coroutine
    def get_patient_details(self, _header, _body, qs, matches, _key):
        """
        This method returns Patient Details which include the data in the header of the Encounter Page
            i.e. Allergies Problem List, Last Encounter, others.
        """
        context = self.helper.restrict_context(qs,
                                               FrontendWebService.patient_required_contexts,
                                               FrontendWebService.patient_available_contexts)
        provider = context[CONTEXT_PROVIDER]
        patientid = context[CONTEXT_PATIENTLIST]
        customerid = context[CONTEXT_CUSTOMERID]
        #if not auth_key == _authorization_key((provider, patient_id), AUTH_LENGTH):
        #   raise HTTP.IncompleteRequest('%s has not been authorized to view patient %s.' % (provider, patient_id))

        desired = {
            WP.Results.patientname: 'name',
            WP.Results.patientid: 'id',
            WP.Results.sex: 'gender',
            WP.Results.birthdate: 'DOB',
            WP.Results.diagnosis: 'diagnosis',
            WP.Results.cost: 'cost',
            WP.Results.encounter_list: 'encounters',
            WP.Results.allergies: 'Allergies',
            WP.Results.problems: 'ProblemList',
            WP.Results.admission: 'admitdate',
            WP.Results.lengthofstay: 'LOS',
        }
        results = yield from self.persistence_interface.patient_info(desired, provider, customerid,
                                                                     limit=self.helper.limit_clause(matches))

        return HTTP.OK_RESPONSE, json.dumps(results[0]), None

    totals_required_contexts = [CONTEXT_PROVIDER, CONTEXT_KEY, CONTEXT_CUSTOMERID]
    totals_available_contexts = {CONTEXT_PROVIDER: str, CONTEXT_KEY: list,
                                 CONTEXT_PATIENTLIST: list, CONTEXT_ENCOUNTER: str,
                                 CONTEXT_CUSTOMERID: int}

    @asyncio.coroutine
    def get_total_spend(self, _header, _body, qs, _matches, _key):
        context = self.helper.restrict_context(qs,
                                               FrontendWebService.daily_required_contexts,
                                               FrontendWebService.daily_available_contexts)
        provider = context[CONTEXT_PROVIDER]
        patient_ids = context.get(CONTEXT_PATIENTLIST, None)
        customer = context[CONTEXT_CUSTOMERID]
        encounter = context.get(CONTEXT_ENCOUNTER, None)
        #auth_keys = dict(zip(patient_ids,context[CONTEXT_KEY]))

        desired = {
            WP.Results.spending: 'spending',
            WP.Results.savings: 'savings',
        }

        results = yield from self.persistence_interface.total_spend(desired, provider, customer,
                                                                    patients=patient_ids, encounter=encounter)

        return HTTP.OK_RESPONSE, json.dumps(results), None

    daily_required_contexts = [CONTEXT_PROVIDER, CONTEXT_KEY, CONTEXT_CUSTOMERID]
    daily_available_contexts = {CONTEXT_PROVIDER: str, CONTEXT_KEY: list,
                                CONTEXT_PATIENTLIST: list, CONTEXT_CUSTOMERID: int,
                                CONTEXT_ENCOUNTER: str}

    @asyncio.coroutine
    def get_daily_spending(self, _header, _body, qs, _matches, _key):
        context = self.helper.restrict_context(qs,
                                               FrontendWebService.daily_required_contexts,
                                               FrontendWebService.daily_available_contexts)
        provider = context[CONTEXT_PROVIDER]
        customer = context[CONTEXT_CUSTOMERID]
        patient_dict = defaultdict(lambda: defaultdict(int))
        encounter = context.get(CONTEXT_ENCOUNTER, None)
        patient_ids = context.get(CONTEXT_PATIENTLIST, None)
        #auth_keys = dict(zip(patient_ids,context[CONTEXT_KEY]))

        desired = {x: x for x in [WP.Results.date, WP.Results.ordertype, WP.Results.spending]}
        #if AK.check_authorization((provider, patient_id), auth_keys[patient_id], AUTH_LENGTH):
        results = yield from self.persistence_interface.daily_spend(desired, provider, customer,
                                                                    patients=patient_ids, encounter=encounter)

        for row in results:
            patient_dict[row[WP.Results.date]][row[WP.Results.ordertype]] += row[WP.Results.spending]

        return HTTP.OK_RESPONSE, json.dumps(patient_dict), None

    alerts_required_contexts = [CONTEXT_PROVIDER, CONTEXT_CUSTOMERID]
    alerts_available_contexts = {CONTEXT_PROVIDER: str, CONTEXT_PATIENTLIST: list,
                                 CONTEXT_CUSTOMERID: int, CONTEXT_ENCOUNTER: str}

    @asyncio.coroutine
    def get_alerts(self, _header, _body, qs, matches, _key):

        context = self.helper.restrict_context(qs,
                                               FrontendWebService.alerts_required_contexts,
                                               FrontendWebService.alerts_available_contexts)
        provider = context[CONTEXT_PROVIDER]
        patients = context.get(CONTEXT_PATIENTLIST, None)
        customer = context[CONTEXT_CUSTOMERID]
        limit = self.helper.limit_clause(matches)

        desired = {
            WP.Results.alertid: 'id',
            WP.Results.patientid: 'patient',
            WP.Results.datetime: 'date',
            WP.Results.title: 'name',
            WP.Results.description: 'html',
            WP.Results.savings: 'cost',
            WP.Results.alerttype: 'alerttype',
            WP.Results.ruleid: 'ruleid',
        }

        results = yield from self.persistence_interface.alerts(desired, provider, customer,
                                                               patients=patients,
                                                               limit=limit)

        return HTTP.OK_RESPONSE, json.dumps(results), None

    orders_required_contexts = [CONTEXT_PROVIDER, CONTEXT_CUSTOMERID]
    orders_available_contexts = {CONTEXT_PROVIDER: str, CONTEXT_PATIENTLIST: list,
                                 CONTEXT_CUSTOMERID: int, CONTEXT_ENCOUNTER: str,
                                 CONTEXT_ORDERTYPE: str}

    @asyncio.coroutine
    def get_orders(self, _header, _body, qs, matches, _key):
        context = self.helper.restrict_context(qs,
                                               FrontendWebService.orders_required_contexts,
                                               FrontendWebService.orders_available_contexts)
        ordertype = context.get(CONTEXT_ORDERTYPE, None)
        if ordertype:
            ordertypes = [ordertype]
        else:
            ordertypes = []
        patient_ids = context.get(CONTEXT_PATIENTLIST, None)
        if not patient_ids:
            return HTTP.OK_RESPONSE, b'', None

        encounter = context.get(CONTEXT_ENCOUNTER, None)
        customer = context[CONTEXT_CUSTOMERID]
        limit = self.helper.limit_clause(matches)
        if not limit:
            limit = 'LIMIT 10'
        #auth_keys = dict(zip(patient_ids,context[CONTEXT_KEY]))

        desired = {
            WP.Results.ordername: 'name',
            WP.Results.datetime: 'date',
            WP.Results.active: 'result',
            WP.Results.cost: 'cost',
            WP.Results.ordertype: CONTEXT_ORDERTYPE,
            WP.Results.orderid: 'id',
        }

        results = yield from self.persistence_interface.orders(desired, customer, encounter,
                                                               ordertypes=ordertypes, limit=limit)

        return HTTP.OK_RESPONSE, json.dumps(results), None

    hist_spend_required_contexts = [CONTEXT_PROVIDER, CONTEXT_CUSTOMERID]
    hist_spend_available_contexts = {CONTEXT_PROVIDER: str, CONTEXT_PATIENTLIST: list,
                                     CONTEXT_CUSTOMERID: int, CONTEXT_ENCOUNTER: str}

    @asyncio.coroutine
    def get_hist_spend(self, _header, _body, qs, matches, _key):
        context = self.helper.restrict_context(qs,
                                               FrontendWebService.hist_spend_required_contexts,
                                               FrontendWebService.hist_spend_available_contexts)

        desired = {
            WP.Results.spending: "spending",
            WP.Results.startdate: "admission",
            WP.Results.enddate: "discharge",
            WP.Results.diagnosis: "diagnosis",
        }
        results = yield from self.persistence_interface.per_encounter(desired,
                                                                      context.get(CONTEXT_PROVIDER),
                                                                      context.get(CONTEXT_CUSTOMERID),
                                                                      patients=context.get(CONTEXT_PATIENTLIST, None),
                                                                      encounter=context.get(CONTEXT_ENCOUNTER, None),
                                                                      startDate=None, endDate=None)

        return HTTP.OK_RESPONSE, json.dumps(results), None


if __name__ == '__main__':
    from utils.database.database import AsyncConnectionPool

    MC.MavenConfig = \
        {
            "httpserver":
                {
                    SP.CONFIG_HOST: 'localhost',
                    SP.CONFIG_PORT: 8087,
                    CONFIG_PERSISTENCE: "persistence layer",
                },
            'persistence layer': {WP.CONFIG_DATABASE: 'webservices conn pool', },
            'webservices conn pool': {
                AsyncConnectionPool.CONFIG_CONNECTION_STRING: MC.dbconnection,
                AsyncConnectionPool.CONFIG_MIN_CONNECTIONS: 4,
                AsyncConnectionPool.CONFIG_MAX_CONNECTIONS: 8
            }
        }
    hp = FrontendWebService('httpserver')
    event_loop = asyncio.get_event_loop()
    hp.schedule(event_loop)
    event_loop.run_forever()
