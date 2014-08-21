# *************************************************************************
# Copyright (c) 2014 - Maven Medical
#
# ************************
# AUTHOR:
__author__ = 'Tom DuBois'
# ************************
# DESCRIPTION:
# This file contains the core web services to deliver json objects to the
# frontend website
# ************************
# *************************************************************************

import json
from collections import defaultdict
import utils.database.web_persistence as WP
import utils.streaming.stream_processor as SP
import utils.streaming.http_responder as HTTP
import utils.streaming.http_helper as HH
import asyncio
import bcrypt
import utils.crypto.authorization_key as AK
import maven_config as MC
from utils.enums import USER_ROLES
from functools import partial, wraps
import re

CONFIG_PERSISTENCE = 'persistence'


class CONTEXT():
    USER = 'user'
    PROVIDER = 'provider'
    ROLES = 'roles'
    DATE = 'date'
    DATERANGE = 'daterange'
    PATIENTLIST = 'patients'
    DEPARTMENT = 'department'
    ORDERTYPE = 'ordertype'
    ORDERID = 'order_id'
    ALERTID = 'alert_id'
    RULEID = 'rule_id'
    KEY = 'userAuth'
    ENCOUNTER = 'encounter'
    CUSTOMERID = 'customer_id'
    DIAGNOSIS = 'diagnosis'
    PATIENTNAME = 'patientname'
    STARTDATE = 'startdate'
    ENDDATE = 'enddate'
    CATEGORY = 'category'
    CATEGORIES = 'categories'
    OFFICIALNAME = 'official_name'
    DISPLAYNAME = 'display_name'
    ACTION = 'action'
    ACTIONCOMMENT = 'action_comment'

LOGIN_TIMEOUT = 60 * 60  # 1 hour
AUTH_LENGTH = 44  # 44 base 64 encoded bits gives the entire 256 bites of SHA2 hash


class LoginError(Exception):
    pass

date = str
_handlers = []


def http_service(methods, url, required, available, roles):
    """ decorator for http handlers
    :param methods: the http methods to handle
    :param url: the url to handle
    :param required: a list of keys required to be in the query string
    :param available: a list of keys (and their types) to be extracted
                      from the query string and put into the context
    :param roles: a list of user roles, at least one of which is required
                  to use this service
    """
    roles = roles and {r.value for r in roles}

    def decorator(func):
        cofunc = asyncio.coroutine(func)

        @wraps(func)
        def worker(self, header, body, qs, matches, key):
            # the UI sends a list 'roles' as 'roles[]', so we adjust that here
            if roles and not roles.intersection(qs.get(CONTEXT.ROLES + '[]', set())):
                return HTTP.UNAUTHORIZED_RESPONSE, b'', None
            context = qs
            if required or available:
                context = self.helper.restrict_context(qs, required, available)
            res = yield from cofunc(self, header, body, context, matches, key)
            return res

        _handlers.append([methods, url, asyncio.coroutine(worker)])
        return None
    return decorator


class FrontendWebService(HTTP.HTTPProcessor):
    def __init__(self, configname):
        HTTP.HTTPProcessor.__init__(self, configname)
        try:
            persistence_name = self.config[CONFIG_PERSISTENCE]
        except KeyError:
            raise MC.InvalidConfig('No persistence layout specified for the web service')

        self.stylesheet = 'demo'
        for handler in _handlers:
            self.add_handler(handler[0], handler[1], partial(handler[2], self))

        self.helper = HH.HTTPHelper([CONTEXT.USER, CONTEXT.PROVIDER, CONTEXT.CUSTOMERID,
                                     CONTEXT.ROLES], CONTEXT.KEY, AUTH_LENGTH)
        self.persistence_interface = WP.WebPersistence(persistence_name)

    def schedule(self, loop):
        HTTP.HTTPProcessor.schedule(self, loop)
        self.persistence_interface.schedule(loop)

    @http_service(['GET'], '/autocomplete_patient',
                  [CONTEXT.PATIENTNAME, CONTEXT.PROVIDER, CONTEXT.CUSTOMERID],
                  {CONTEXT.PATIENTNAME: str, CONTEXT.PROVIDER: str,
                   CONTEXT.CUSTOMERID: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_autocomplete_patient(self, _header, _body, context, matches, _key):
        provider = context[CONTEXT.PROVIDER]
        patientname = context[CONTEXT.PATIENTNAME]
        customerid = context[CONTEXT.CUSTOMERID]
        desired = {
            WP.Results.patientname: 'label',
            WP.Results.patientid: 'value',
        }
        results = yield from self.persistence_interface.patient_info(desired, provider, customerid,
                                                                     limit=self.helper.limit_clause(matches),
                                                                     patient_name=patientname)

        return HTTP.OK_RESPONSE, json.dumps(results), None

        # return HTTP.OK_RESPONSE, json.dumps(['Maven']), None

    @http_service(['GET'], '/autocomplete_diagnosis',
                  [CONTEXT.DIAGNOSIS, CONTEXT.PROVIDER, CONTEXT.CUSTOMERID],
                  {CONTEXT.DIAGNOSIS: str, CONTEXT.PROVIDER: str,
                   CONTEXT.CUSTOMERID: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_autocomplete_diagnosis(self, _header, _body, context, matches, _key):
        # context = self.helper.restrict_context(qs,
        #                                        FrontendWebService.diagnosis_required_contexts,
        #                                        FrontendWebService.diagnosis_available_contexts)
        # provider = context[CONTEXT.PROVIDER]
        # diagnosis = context[CONTEXT.DIAGNOSIS]
        # customerid = context[CONTEXT.CUSTOMERID]
        # desired = {
        #    WP.Results.diagnosis: 'diagnosis',
        # }
        """ NOT READY YET:
        results = yield from self.persistence_interface.diagnosis_info(desired, provider,
                                                                       customerid,
                                                                       diagnosis=diagnosis,
                                                                       limit=self.helper.limit_clause(matches),)
        """
        # return HTTP.OK_RESPONSE, json.dumps(results), None
        return HTTP.OK_RESPONSE, json.dumps(['Alzheimer\'s', 'Diabetes']), None

    @asyncio.coroutine
    def hash_new_password(self, user, newpassword):
        if (len(newpassword) < 8
                or not re.search("[0-9]", newpassword)
                or not re.search("[a-z]", newpassword)
                or not re.search("[A-Z]", newpassword)):
            raise LoginError('expiredPassword')
        salt = bcrypt.gensalt(4)
        ret = bcrypt.hashpw(bytes(newpassword, 'utf-8'), salt)
        try:
            yield from self.persistence_interface.update_password(user, ret)
        except:
            import traceback
            traceback.print_exc()
            raise LoginError('expiredPassword')

    @http_service(['GET'], '/rate_alert',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID, CONTEXT.ALERTID, CONTEXT.ACTION,
                   CONTEXT.RULEID, CONTEXT.CATEGORY],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int, CONTEXT.ALERTID: int,
                   CONTEXT.ACTION: str, CONTEXT.RULEID: str, CONTEXT.CATEGORY: str},
                  {USER_ROLES.provider})
    def rate_alert(self, _header, _body, context, _matches, _key):
        userid = context[CONTEXT.USER]
        customer = context[CONTEXT.CUSTOMERID]
        alertid = context[CONTEXT.ALERTID]
        action = context[CONTEXT.ACTION]
        category = context[CONTEXT.CATEGORY]
        ruleid = context[CONTEXT.RULEID]
        if ruleid == "null":
            ruleid = "0"

        desired = {
            WP.Results.action: 'action',
        }

        update = 0
        result = yield from self.persistence_interface.alert_settings(desired, userid, customer,
                                                                      alertid, ruleid, category)
        if result:
            # record exists so update, don't add
            update = 1

        result = yield from self.persistence_interface.rate_alert(customer, userid, category,
                                                                  "", alertid, ruleid, "", action,
                                                                  update=update)

        # return HTTP.OK_RESPONSE, json.dumps(['ALERT LIKED']), None
        if result:
            return HTTP.OK_RESPONSE, json.dumps(['TRUE']), None
        else:
            return HTTP.OK_RESPONSE, json.dumps(['FALSE']), None

    @http_service(['GET'], '/critique_alert',
                  [CONTEXT.CUSTOMERID, CONTEXT.RULEID, CONTEXT.USER,
                   CONTEXT.CATEGORY, CONTEXT.ACTIONCOMMENT, CONTEXT.ALERTID],
                  {CONTEXT.CUSTOMERID: int, CONTEXT.RULEID: int, CONTEXT.CATEGORY: str,
                   CONTEXT.ACTIONCOMMENT: str, CONTEXT.USER: str, CONTEXT.ALERTID: int},
                  {USER_ROLES.provider})
    def critique_alert(self, _header, _body, context, _matches, _key):
        userid = context[CONTEXT.USER]
        customerid = context[CONTEXT.CUSTOMERID]
        alertid = context[CONTEXT.ALERTID]
        actioncomment = context[CONTEXT.ACTIONCOMMENT]
        category = context[CONTEXT.CATEGORY]
        ruleid = context[CONTEXT.RULEID]
        if ruleid == "null":
            ruleid = "0"

        result = yield from self.persistence_interface.update_alert_setting(userid, customerid,
                                                                            alertid, ruleid,
                                                                            category, actioncomment)
        if result:
            return HTTP.OK_RESPONSE, json.dumps(['TRUE']), None
        else:
            return HTTP.OK_RESPONSE, json.dumps(['FALSE']), None

    @http_service(['GET'], '/save_user_settings',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID, CONTEXT.OFFICIALNAME, CONTEXT.DISPLAYNAME],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int,
                   CONTEXT.OFFICIALNAME: str, CONTEXT.DISPLAYNAME: str},
                  None)
    def save_user_settings(self, _header, _body, context, _matches, _key):
        userid = context[CONTEXT.USER]
        officialname = context[CONTEXT.OFFICIALNAME]
        displayname = context[CONTEXT.DISPLAYNAME]

        result = yield from self.persistence_interface.update_user_settings(userid, officialname,
                                                                            displayname)
        if result:
            return HTTP.OK_RESPONSE, json.dumps(['TRUE']), None
        else:
            return HTTP.OK_RESPONSE, json.dumps(['FALSE']), None

    @http_service(['POST'], '/login', None, None, None)
    def post_login(self, header, body, _context, _matches, _key):
        info = json.loads(body.decode('utf-8'))

        user_and_pw = set((CONTEXT.USER, 'password')).issubset(info)
        prov_and_auth = set(('provider', 'customer', 'userAuth')).issubset(info)
        if not user_and_pw and not prov_and_auth:
            return HTTP.BAD_RESPONSE, b'', None

        desired = {k: k for k in [
            WP.Results.userid,
            WP.Results.customerid,
            WP.Results.provid,
            WP.Results.displayname,
            WP.Results.officialname,
            WP.Results.password,
            WP.Results.passexpired,
            WP.Results.userstate,
            # WP.Results.failedlogins,
            WP.Results.recentkeys,
            WP.Results.roles
        ]}
        attempted = None
        try:
            method = 'failed'
            user_info = {}
            # if header.get_headers().get('VERIFIED','SUCCESS') == 'SUCCESS':
            if user_and_pw:
                attempted = info['user']
                try:
                    user_info = yield from self.persistence_interface.pre_login(desired,
                                                                                username=attempted)
                except IndexError:
                    raise LoginError('badLogin')
                passhash = user_info[WP.Results.password].tobytes()
                if (not passhash or
                        bcrypt.hashpw(bytes(info['password'], 'utf-8'),
                                      passhash[:29]) != passhash):
                    raise LoginError('badLogin')
                if user_info[WP.Results.passexpired] or 'newpassword' in info:
                    yield from self.hash_new_password(user_info[WP.Results.userid],
                                                      info.get('newpassword', ''))
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
            customer = str(user_info[WP.Results.customerid])
            roles = user_info[WP.Results.roles]
            user_auth = AK.authorization_key([[user], [provider], [customer], sorted(roles)],
                                             AUTH_LENGTH, LOGIN_TIMEOUT)
            if not self.stylesheet == 'original':
                self.stylesheet = 'demo'

            desired_layout = {
                WP.Results.widget: 'widget',
                WP.Results.template: 'template',
                WP.Results.element: 'element',
                WP.Results.priority: 'priority'
            }
            widgets = yield from self.persistence_interface.layout_info(desired_layout, user_info[WP.Results.userid])

            ret = {CONTEXT.USER: user_info[WP.Results.userid],
                   'display': user_info[WP.Results.displayname],
                   'stylesheet': self.stylesheet, 'customer_id': customer,
                   'official_name': user_info[WP.Results.officialname],
                   CONTEXT.PROVIDER: provider,
                   CONTEXT.USER: user,
                   CONTEXT.ROLES: roles,
                   'widgets': widgets, CONTEXT.KEY: user_auth}

            return HTTP.OK_RESPONSE, json.dumps(ret), None
        except LoginError as err:
            return HTTP.UNAUTHORIZED_RESPONSE, json.dumps({'loginTemplate':
                                                           err.args[0] + ".html"}), None
        finally:
            yield from self.persistence_interface.record_login(attempted,
                                                               method,
                                                               header.get_headers().get('X-Real-IP'),
                                                               info['userAuth'] if method == 'forward' else None)

    @http_service(['GET'], '/patients(?:(\d+)-(\d+)?)?',
                  [CONTEXT.PROVIDER, CONTEXT.CUSTOMERID],
                  {CONTEXT.PROVIDER: str, CONTEXT.CUSTOMERID: int,
                   CONTEXT.STARTDATE: date, CONTEXT.ENDDATE: date},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_patients(self, _header, _body, context, matches, _key):
        provider = context[CONTEXT.PROVIDER]
        customerid = context[CONTEXT.CUSTOMERID]
        startdate = self.helper.get_date(context, CONTEXT.STARTDATE)
        enddate = self.helper.get_date(context, CONTEXT.ENDDATE)
        desired = {
            WP.Results.patientname: 'name',
            WP.Results.patientid: 'id',
            WP.Results.sex: 'gender',
            WP.Results.birthdate: 'DOB',
            WP.Results.diagnosis: 'diagnosis',
            WP.Results.cost: 'cost',
        }
        results = yield from self.persistence_interface.patient_info(desired, provider, customerid,
                                                                     startdate=startdate,
                                                                     enddate=enddate,
                                                                     limit=self.helper.limit_clause(matches))
        return HTTP.OK_RESPONSE, json.dumps(results), None

    @http_service(['GET'], '/patient_details',
                  [CONTEXT.PROVIDER, CONTEXT.KEY, CONTEXT.PATIENTLIST, CONTEXT.CUSTOMERID],
                  {CONTEXT.PROVIDER: str, CONTEXT.KEY: str, CONTEXT.PATIENTLIST: str,
                   CONTEXT.CUSTOMERID: int, CONTEXT.ENCOUNTER: str,
                   CONTEXT.STARTDATE: date, CONTEXT.ENDDATE: date},
                  {USER_ROLES.provider})
    def get_patient_details(self, _header, _body, context, matches, _key):
        """
        This method returns Patient Details which include the data in the header of
        the Encounter Page - i.e. Allergies Problem List, Last Encounter, others.
        """
        provider = context[CONTEXT.PROVIDER]
        patientid = context[CONTEXT.PATIENTLIST]
        customerid = context[CONTEXT.CUSTOMERID]
        startdate = self.helper.get_date(context, CONTEXT.STARTDATE)
        enddate = self.helper.get_date(context, CONTEXT.ENDDATE)
        # if not auth_key == _authorization_key((provider, patient_id), AUTH_LENGTH):
        #   raise HTTP.IncompleteRequest('%s has not been authorized to view patient %s.'
        #                                % (provider, patient_id))

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
                                                                     patients=patientid,
                                                                     startdate=startdate,
                                                                     enddate=enddate,
                                                                     limit=self.helper.limit_clause(matches))

        return HTTP.OK_RESPONSE, json.dumps(results[0]), None

    @http_service(['GET'], '/total_spend',
                  [CONTEXT.PROVIDER, CONTEXT.KEY, CONTEXT.CUSTOMERID],
                  {CONTEXT.PROVIDER: str, CONTEXT.KEY: list, CONTEXT.PATIENTLIST: list,
                   CONTEXT.ENCOUNTER: str, CONTEXT.CUSTOMERID: int,
                   CONTEXT.STARTDATE: date, CONTEXT.ENDDATE: date},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_total_spend(self, _header, _body, context, _matches, _key):
        provider = context[CONTEXT.PROVIDER]
        patient_ids = context.get(CONTEXT.PATIENTLIST, None)
        customer = context[CONTEXT.CUSTOMERID]
        encounter = context.get(CONTEXT.ENCOUNTER, None)
        startdate = self.helper.get_date(context, CONTEXT.STARTDATE)
        enddate = self.helper.get_date(context, CONTEXT.ENDDATE)
        # auth_keys = dict(zip(patient_ids, context[CONTEXT.KEY]))

        desired = {
            WP.Results.spending: 'spending',
            WP.Results.savings: 'savings',
        }

        if patient_ids or encounter:
            provider = None

        results = yield from self.persistence_interface.total_spend(desired, customer,
                                                                    provider=provider,
                                                                    startdate=startdate,
                                                                    enddate=enddate,
                                                                    patients=patient_ids,
                                                                    encounter=encounter)

        return HTTP.OK_RESPONSE, json.dumps(results), None

    @http_service(['GET'], '/spending',
                  [CONTEXT.PROVIDER, CONTEXT.KEY, CONTEXT.CUSTOMERID],
                  {CONTEXT.PROVIDER: str, CONTEXT.KEY: list, CONTEXT.PATIENTLIST: list,
                   CONTEXT.CUSTOMERID: int, CONTEXT.ENCOUNTER: str,
                   CONTEXT.STARTDATE: date, CONTEXT.ENDDATE: date},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_daily_spending(self, _header, _body, context, _matches, _key):
        provider = context[CONTEXT.PROVIDER]
        customer = context[CONTEXT.CUSTOMERID]
        ret = defaultdict(lambda: defaultdict(int))
        encounter = context.get(CONTEXT.ENCOUNTER, None)
        patient_ids = context.get(CONTEXT.PATIENTLIST, None)
        startdate = self.helper.get_date(context, CONTEXT.STARTDATE)
        enddate = self.helper.get_date(context, CONTEXT.ENDDATE)
        # auth_keys = dict(zip(patient_ids, context[CONTEXT.KEY]))

        desired = {x: x for x in [WP.Results.date, WP.Results.ordertype, WP.Results.spending]}
        # if AK.check_authorization((provider, patient_id), auth_keys[patient_id], AUTH_LENGTH):
        results = yield from self.persistence_interface.daily_spend(desired, provider, customer,
                                                                    startdate=startdate,
                                                                    enddate=enddate,
                                                                    patients=patient_ids,
                                                                    encounter=encounter)

        for row in results:
            if WP.Results.spending is int:
                ret[row[WP.Results.date]][row[WP.Results.ordertype]] += row[WP.Results.spending]
            else:
                ret[row[WP.Results.date]][row[WP.Results.ordertype]] = row[WP.Results.spending]

        return HTTP.OK_RESPONSE, json.dumps(ret), None

    @http_service(['GET'], '/alerts(?:(\d+)-(\d+)?)?',
                  [CONTEXT.PROVIDER, CONTEXT.CUSTOMERID],
                  {CONTEXT.PROVIDER: str, CONTEXT.PATIENTLIST: list, CONTEXT.CUSTOMERID: int,
                   CONTEXT.ENCOUNTER: str, CONTEXT.STARTDATE: date, CONTEXT.ENDDATE: date,
                   CONTEXT.ORDERID: str, CONTEXT.CATEGORIES: list},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_alerts(self, _header, _body, context, matches, _key):
        provider = context[CONTEXT.PROVIDER]
        patients = context.get(CONTEXT.PATIENTLIST, None)
        customer = context[CONTEXT.CUSTOMERID]
        orderid = context.get(CONTEXT.ORDERID, None)
        categories = context.get(CONTEXT.CATEGORIES, None)

        startdate = self.helper.get_date(context, CONTEXT.STARTDATE)
        enddate = self.helper.get_date(context, CONTEXT.ENDDATE)
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
            WP.Results.likes: 'likes',
            WP.Results.dislikes: 'dislikes'
        }

        results = yield from self.persistence_interface.alerts(desired, provider, customer,
                                                               patients=patients,
                                                               startdate=startdate,
                                                               enddate=enddate,
                                                               limit=limit, orderid=orderid,
                                                               categories=categories)

        return HTTP.OK_RESPONSE, json.dumps(results), None

    @http_service(['GET'], '/orders(?:(\d+)-(\d+)?)?',
                  [CONTEXT.PROVIDER, CONTEXT.CUSTOMERID],
                  {CONTEXT.PROVIDER: str, CONTEXT.PATIENTLIST: list, CONTEXT.CUSTOMERID: int,
                   CONTEXT.ENCOUNTER: str, CONTEXT.ORDERTYPE: str,
                   CONTEXT.STARTDATE: date, CONTEXT.ENDDATE: date},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_orders(self, _header, _body, context, matches, _key):
        ordertype = context.get(CONTEXT.ORDERTYPE, None)
        if ordertype:
            ordertypes = [ordertype]
        else:
            ordertypes = []
        patient_ids = context.get(CONTEXT.PATIENTLIST, None)

        encounter = context.get(CONTEXT.ENCOUNTER, None)
        customer = context[CONTEXT.CUSTOMERID]
        startdate = self.helper.get_date(context, CONTEXT.STARTDATE)
        enddate = self.helper.get_date(context, CONTEXT.ENDDATE)
        limit = self.helper.limit_clause(matches)
        if not limit:
            limit = 'LIMIT 10'
        # auth_keys = dict(zip(patient_ids, context[CONTEXT.KEY]))

        desired = {
            WP.Results.ordername: 'name',
            WP.Results.datetime: 'date',
            WP.Results.active: 'result',
            WP.Results.cost: 'cost',
            WP.Results.ordertype: CONTEXT.ORDERTYPE,
            WP.Results.orderid: 'id',
        }

        results = yield from self.persistence_interface.orders(desired, customer,
                                                               encounter=encounter,
                                                               patientid=patient_ids,
                                                               startdate=startdate,
                                                               enddate=enddate,
                                                               ordertypes=ordertypes, limit=limit)

        return HTTP.OK_RESPONSE, json.dumps(results), None

    @http_service(['GET'], '/hist_spending',
                  [CONTEXT.PROVIDER, CONTEXT.CUSTOMERID],
                  {CONTEXT.PROVIDER: str, CONTEXT.PATIENTLIST: list, CONTEXT.CUSTOMERID: int},
                  {USER_ROLES.supervisor, USER_ROLES.provider})
    def get_hist_spend(self, _header, _body, context, matches, _key):
        desired = {
            WP.Results.patientid: "patientid",
            WP.Results.patientname: "patientname",
            WP.Results.encounterid: "encounterid",
            WP.Results.spending: "spending",
            WP.Results.startdate: "admission",
            WP.Results.enddate: "discharge",
            WP.Results.diagnosis: "diagnosis",
        }
        results = yield from self.persistence_interface.per_encounter(desired,
                                                                      context.get(CONTEXT.PROVIDER),
                                                                      context.get(CONTEXT.CUSTOMERID),
                                                                      patients=context.get(CONTEXT.PATIENTLIST, None))

        return HTTP.OK_RESPONSE, json.dumps(results), None


def run():
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
            'webservices conn pool':
                {
                    AsyncConnectionPool.CONFIG_CONNECTION_STRING: MC.dbconnection,
                    AsyncConnectionPool.CONFIG_MIN_CONNECTIONS: 4,
                    AsyncConnectionPool.CONFIG_MAX_CONNECTIONS: 8
                }
        }
    hp = FrontendWebService('httpserver')
    event_loop = asyncio.get_event_loop()
    hp.schedule(event_loop)
    event_loop.run_forever()

if __name__ == '__main__':
    run()
