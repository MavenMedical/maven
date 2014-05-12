#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
__author__='Tom DuBois'
#************************
#DESCRIPTION:
# This file contains the core web services to deliver json objects to the
# frontend website
#************************
#*************************************************************************

import json
import random
import itertools
import datetime
from collections import defaultdict
from utils.database.database import AsyncConnectionPool
from utils.database.database import MappingUtilites as DBMapUtils
import utils.streaming.stream_processor as SP
import utils.streaming.http_responder as HTTP
import asyncio
import dateutil.parser as prsr
import utils.crypto.authorization_key as AK
import maven_logging as ML
import maven_config as MC


CONFIG_DATABASE = 'database'

CONTEXT_USER = 'user'
CONTEXT_PROVIDER = 'provider'
CONTEXT_DATE = 'date'
CONTEXT_DATERANGE = 'daterange'
CONTEXT_PATIENTLIST = 'patients'
CONTEXT_DEPARTMENT = 'department'
CONTEXT_CATEGORY = 'category'
CONTEXT_KEY = 'userAuth'
CONTEXT_ENCOUNTER = 'encounter'
CONTEXT_CUSTOMERID = 'customer_id'

LOGIN_TIMEOUT = 60 * 60 # 1 hour
AUTH_LENGTH = 44 # 44 base 64 encoded bits gives the entire 256 bites of SHA2 hash

def prettify(s, type=None):
    if type == "name":
        name = s.split(",")
        return (str.title(name[0]) + ", " + str.title(name[1]))

    elif type == "sex":
        return str.title(s)
    
    elif type == "date":
        print(s)
        #prsr = dateutil.parser()
        d = prsr.parse(s)
        return (d.strftime("%A, %B %d, %Y"))


def copy_and_append(m, kv):
    return dict(itertools.chain(m.items(),[kv]))

def restrict_context(qs, required, available):
    if not set(required).issubset(qs.keys()):
        raise HTTP.IncompleteRequest('Request is incomplete.  Required arguments are: '+', '.join(required)+".\n")
    # not implemented yet - making sure optional parameters are the right type

    if not CONTEXT_KEY in qs:
        raise HTTP.UnauthorizedRequest('User is not logged in.')
    try:
        AK.check_authorization(qs[CONTEXT_USER][0], qs[CONTEXT_KEY][0], AUTH_LENGTH)
    except AK.UnauthorizedException as ue:
        raise HTTP.UnauthorizedRequest(str(ue))

    context = {}
    for k, v in qs.items():
        if k in available:
            if available[k] is list:
                context[k]=v
            else:
                if len(v) is 1:
                    try:
                        context[k] = available[k](v[0])
                    except ValueError:
                        raise HTTP.IncompleteRequest('Request has parameter %s which is of the wrong type.' % k)
                else:
                    raise HTTP.IncompleteRequest('Request requires exactly one instance of parameter %s.' % k)
    return context

def limit_clause(matches):
    if len(matches)==2 and all(matches):
        return " LIMIT %d OFFSET %d" % (matches[1]-matches[0], matches[0])
    else:
        return ""

class FrontendWebService(HTTP.HTTPProcessor):

    def __init__(self, configname):
        HTTP.HTTPProcessor.__init__(self,configname)
        try:
            db_configname = self.config[CONFIG_DATABASE]
        except KeyError:
            raise MC.InvalidConfig('some real error')

        self.stylesheet='original'
        self.costbdtype = 'donut'  # this assignment isn't used yet
        self.add_handler(['POST'], '/login', self.post_login)  # FAKE
        self.add_handler(['GET'], '/patients(?:/(\d+)-(\d+)?)?', self.get_patients)  # REAL
        self.add_handler(['GET'], '/patient_details', self.get_patient_details)  # REAL
        self.add_handler(['GET'], '/total_spend', self.get_total_spend)  # FAKE
        self.add_handler(['GET'], '/spending', self.get_daily_spending)  # FAKE
        self.add_handler(['GET'], '/alerts(?:/(\d+)-(\d+)?)?', self.get_alerts)  # REAL
        self.add_handler(['GET'], '/orders(?:/(\d+)-(\d+)?)?', self.get_orders)  # REAL
        self.add_handler(['GET'], '/autocomplete', self.get_autocomplete)  # FAKE
        self.db = AsyncConnectionPool(db_configname)

    def schedule(self, loop):
        HTTP.HTTPProcessor.schedule(self, loop)
        self.db.schedule(loop)

    @asyncio.coroutine
    def get_stub(self, _header, _body, _qs, _matches, _key):
        return (HTTP.OK_RESPONSE, b'', None)

    @asyncio.coroutine
    def get_autocomplete(self, _header, _body, qs, _matches, _key):
        return (HTTP.OK_RESPONSE, json.dumps(['Maven']),None)

    @asyncio.coroutine
    def post_login(self, header, body, _qs, _matches, _key):
        info = json.loads(body.decode('utf-8'))
        if (not 'user' in info) or (not 'password' in info):
            return (HTTP.BAD_RESPONSE, b'', None)
        else:
            user = info['user']
            if not self.stylesheet == 'original':
                self.stylesheet = 'original'
                self.costbdtype = 'donut'
                self.layout = 'a'
            else:
                self.stylesheet = 'alternate'
                self.costbdtype = 'list'
                self.layout = 'a'

            ret = {'display':'Dr. Huxtable', 'stylesheet':self.stylesheet, 'costbdtype':self.costbdtype, 'customer_id':1, 'layout':self.layout}

            try:
                AK.check_authorization(user, info['password'], AUTH_LENGTH)
                return (HTTP.OK_RESPONSE, json.dumps(ret), None)
            except:
                # allow bogus password authentication if there is no optional SSL (test environment) 
                # or if the user has a proper client SSL cert
                if header.get_headers().get('VERIFIED','SUCCESS') == 'SUCCESS': 
                    user_auth = AK.authorization_key(user,AUTH_LENGTH, LOGIN_TIMEOUT)
                    ret[CONTEXT_KEY]=user_auth
                    return (HTTP.OK_RESPONSE,json.dumps(ret), None)
                else:
                    raise HTTP.UnauthorizedRequest('User is not logged in.')

    @asyncio.coroutine
    def _get_patient_info(self, customerid, user, pat_id=None, limit="", encounter_list=None):
        try:
            column_map = [
                "max(patient.patname)",
                "encounter.pat_id",
                "max(patient.birthdate)",
                "max(patient.sex)",
                "max(encounter.contact_date) as contact_date",
                "array_agg(encounter.csn || ' ' || encounter.contact_date)" if encounter_list else None,
                ]
            columns = DBMapUtils().select_rows_from_map(column_map)
            cmd = []
            cmdargs=[]
            cmd.append("SELECT")
            cmd.append(columns)
            cmd.append("FROM patient JOIN encounter")
            cmd.append("ON (patient.pat_id = encounter.pat_id AND encounter.customer_id = patient.customer_id)")
            cmd.append("WHERE encounter.customer_id = %s")
            cmdargs.append(customerid)
            cmd.append("AND encounter.visit_prov_id = %s")
            cmdargs.append(user)
            if pat_id:
                cmd.append("AND encounter.pat_id = %s")
                cmdargs.append(pat_id)
            cmd.append("GROUP BY encounter.pat_id")
            cmd.append("ORDER BY contact_date")
            if limit:
                cmd.append(limit)

            cur = yield from self.db.execute_single(' '.join(cmd)+';',cmdargs)

            results = []
            for x in cur:
                results.append({
                    'id': x[1], 
                    'patientName': prettify(x[0], type="name"), 
                    'gender': prettify(x[3], type="sex"), 
                    'DOB': str(x[2]), 
                    'diagnosis': 'NOT VALID YET', 
                    'key': AK.authorization_key((user, x[1]), AUTH_LENGTH), 
                    'cost':-1,
                    'encounters': list(map(lambda v: v.split(' '), x[5])) if encounter_list else None,
                    })
                ML.DEBUG(json.dumps(results))
        except:
            raise Exception('Error in front end webservices get_patients() call to database')
        return results

    patients_required_contexts = [CONTEXT_USER, CONTEXT_CUSTOMERID]
    patients_available_contexts = {CONTEXT_USER:str, CONTEXT_CUSTOMERID: int}

    @asyncio.coroutine
    def get_patients(self, _header, _body, qs, matches, _key):
        context = restrict_context(qs,
                                   FrontendWebService.patients_required_contexts,
                                   FrontendWebService.patients_available_contexts)
        user = context[CONTEXT_USER]
        customerid = context[CONTEXT_CUSTOMERID]
        results = yield from self._get_patient_info(customerid, user, pat_id=None, 
                                                    limit = limit_clause(matches), encounter_list=None)

        return (HTTP.OK_RESPONSE, json.dumps(results), None)

    patient_required_contexts = [CONTEXT_USER,CONTEXT_KEY,CONTEXT_PATIENTLIST,CONTEXT_CUSTOMERID]
    patient_available_contexts = {CONTEXT_USER:str,CONTEXT_KEY:str,CONTEXT_PATIENTLIST:str, 
                                  CONTEXT_CUSTOMERID:int, CONTEXT_ENCOUNTER:str}

    @asyncio.coroutine
    def get_patient_details(self, _header, _body, qs, matches, _key):
        """
        This method returns Patient Details which include the data in the header of the Encounter Page
            i.e. Allergies Problem List, Last Encounter, others.
        """
        context = restrict_context(qs,
                                   FrontendWebService.patient_required_contexts,
                                   FrontendWebService.patient_available_contexts)
        user = context[CONTEXT_USER]
        patient_id = context[CONTEXT_PATIENTLIST]
        auth_key = context[CONTEXT_KEY]
        customerid = context[CONTEXT_CUSTOMERID]
        #if not auth_key == _authorization_key((user, patient_id), AUTH_LENGTH):
         #   raise HTTP.IncompleteRequest('%s has not been authorized to view patient %s.' % (user, patient_id))

        results = yield from self._get_patient_info(customerid, user, pat_id=patient_id, encounter_list=True)
        results = results[0]

        results.update({'Allergies': ['NOT VALID'], 'Problem List':['NOTVALID', 'NOTVALID']},)
        return (HTTP.OK_RESPONSE, json.dumps(results), None)


    totals_required_contexts = [CONTEXT_USER,CONTEXT_KEY,CONTEXT_CUSTOMERID]
    totals_available_contexts = {CONTEXT_USER:str,CONTEXT_KEY:list,
                                 CONTEXT_PATIENTLIST:list, CONTEXT_ENCOUNTER:str,
                                 CONTEXT_CUSTOMERID: int}

    @asyncio.coroutine
    def get_total_spend(self, _header, _body, qs, _matches, _key):
        context = restrict_context(qs,
                                   FrontendWebService.daily_required_contexts,
                                   FrontendWebService.daily_available_contexts)
        user = context[CONTEXT_USER]
        patient_ids = context.get(CONTEXT_PATIENTLIST, None)
        customer = context[CONTEXT_CUSTOMERID]
        encounter = context.get(CONTEXT_ENCOUNTER, None)
        #auth_keys = dict(zip(patient_ids,context[CONTEXT_KEY]))
        
        column_map = [
            "sum(order_cost)",
            ]
        columns = DBMapUtils().select_rows_from_map(column_map)

        #if AK.check_authorization((user, patient_id), auth_keys[patient_id], AUTH_LENGTH):
        cmd = []
        cmdargs=[]
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM mavenorder JOIN encounter")
        cmd.append("ON mavenorder.encounter_id = encounter.csn")
        cmd.append("WHERE encounter.visit_prov_id = %s")
        cmdargs.append(user)
        cmd.append("AND mavenorder.customer_id = %s")
        cmdargs.append(customer)
        if patient_ids:
            cmd.append("AND encounter.pat_id in %s")
            cmdargs.append(tuple(patient_ids))
        if encounter:
            cmd.append("AND encounter.csn = %s")
            cmdargs.append(encounter)
        
        cur = yield from self.db.execute_single(' '.join(cmd)+';',cmdargs)
        try:
            x = next(cur)
            spend = int(x[0])
        except StopIteration:
            spend=0

        ret = {'spending':spend, 'savings':-16}
        return (HTTP.OK_RESPONSE, json.dumps(ret), None)


    daily_required_contexts = [CONTEXT_USER, CONTEXT_KEY, CONTEXT_CUSTOMERID]
    daily_available_contexts = {CONTEXT_USER: str, CONTEXT_KEY: list, 
                                CONTEXT_PATIENTLIST: list, CONTEXT_CUSTOMERID: int,
                                CONTEXT_ENCOUNTER: str}

#select count(orderid), max(order_name), date_trunc('day',datetime) as dt, order_type, sum(order_cost) from mavenorder join encounter on mavenorder.encounter_id=encounter.csn where encounter.visit_prov_id='JHU1093124' group by dt, order_type, proc_code;
    @asyncio.coroutine
    def get_daily_spending(self, _header, _body, qs, _matches, _key):
        context = restrict_context(qs,
                                   FrontendWebService.daily_required_contexts,
                                   FrontendWebService.daily_available_contexts)
        user = context[CONTEXT_USER]
        customer = context[CONTEXT_CUSTOMERID]
        patient_dict = defaultdict(lambda: defaultdict(int))
        encounter = context.get(CONTEXT_ENCOUNTER, None)
        patient_ids = context.get(CONTEXT_PATIENTLIST,None)
        #auth_keys = dict(zip(patient_ids,context[CONTEXT_KEY]))
        
        column_map = [
            "to_char(datetime,'Mon/DD/YYYY') as dt",
            "order_type",
            "sum(order_cost)",
            ]
        columns = DBMapUtils().select_rows_from_map(column_map)
        

        #if AK.check_authorization((user, patient_id), auth_keys[patient_id], AUTH_LENGTH):
        cmd = []
        cmdargs=[]
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM mavenorder JOIN encounter")
        cmd.append("ON mavenorder.encounter_id = encounter.csn")
        cmd.append("WHERE encounter.visit_prov_id = %s")
        cmdargs.append(user)
        cmd.append("AND mavenorder.customer_id = %s")
        cmdargs.append(customer)
        if patient_ids:
            cmd.append("AND encounter.pat_id in %s")
            cmdargs.append(tuple(patient_ids))
        if encounter:
            cmd.append("AND encounter.csn = %s")
            cmdargs.append(encounter)
        cmd.append("GROUP BY dt, order_type")

        cur = yield from self.db.execute_single(' '.join(cmd)+';',cmdargs)
        for x in cur:
            patient_dict[x[0]][x[1]] += int(x[2])

        return (HTTP.OK_RESPONSE, json.dumps(patient_dict), None)

    #self.add_handler(['GET'], '/alerts(?:/(\d+)-(\d+)?)?', self.get_stub)

    alerts_required_contexts = [CONTEXT_USER, CONTEXT_CUSTOMERID]
    alerts_available_contexts = {CONTEXT_USER:str, CONTEXT_PATIENTLIST:list, 
                                 CONTEXT_CUSTOMERID:int, CONTEXT_ENCOUNTER:str}

    @asyncio.coroutine
    def get_alerts(self, _header, _body, qs, matches, _key):

        context = restrict_context(qs,
                                   FrontendWebService.alerts_required_contexts,
                                   FrontendWebService.alerts_available_contexts)
        user = context[CONTEXT_USER]
        patients = context.get(CONTEXT_PATIENTLIST,None)
        customer = context[CONTEXT_CUSTOMERID]
        limit = limit_clause(matches)

        column_map = ["alerts.alert_id",
                      "alerts.pat_id",
                      "alerts.encounter_date",
                      "alerts.alert_date",
                      "alerts.alert_title",
                      "alerts.alert_msg",
                      "alerts.action",
                      "alerts.saving"]

        columns = DBMapUtils().select_rows_from_map(column_map)
        cmd=[]
        cmdargs=[]
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM alerts")
        cmd.append("Where alerts.prov_id = %s and alerts.customer_id = %s")
        cmdargs.append(user)
        cmdargs.append(customer)
        if patients:
            cmd.append("AND alerts.pat_id in %s")
            cmdargs.append(tuple(patients))
        cmd.append("ORDER BY alerts.alert_date desc")
        if limit:
            cmd.append(limit)

        cur = yield from self.db.execute_single(' '.join(cmd)+';',cmdargs)
                
        results = []
        for x in cur:
            results.append({'id': x[0], 'patient': x[1], 'name':x[4], 'cost': x[7], 'html': x[5], 'date': str(x[2])})
            ML.DEBUG(json.dumps(results))

        #auth_keys = dict(zip(patient_ids,context[CONTEXT_KEY]))

        return (HTTP.OK_RESPONSE, json.dumps(results), None)


    orders_required_contexts = [CONTEXT_USER, CONTEXT_PATIENTLIST, CONTEXT_ENCOUNTER, CONTEXT_CUSTOMERID]
    orders_available_contexts = {CONTEXT_USER:str, CONTEXT_PATIENTLIST:list, 
                                 CONTEXT_CUSTOMERID:int, CONTEXT_ENCOUNTER:str}

    #self.add_handler(['GET'], '/orders(?:/(\d+)-(\d+)?)?', self.get_stub)
    @asyncio.coroutine
    def get_orders(self, _header, _body, qs, matches, _key):
        context = restrict_context(qs,
                                   FrontendWebService.orders_required_contexts,
                                   FrontendWebService.orders_available_contexts)
        user = context[CONTEXT_USER]
        patient_ids = context[CONTEXT_PATIENTLIST]
        encounter = context[CONTEXT_ENCOUNTER]
        customer = context[CONTEXT_CUSTOMERID]
        limit = limit_clause(matches)
        #auth_keys = dict(zip(patient_ids,context[CONTEXT_KEY]))

        order_dict = {}

        column_map = ["mavenorder.order_name",
                      "mavenorder.datetime",
                      "mavenorder.active",
                      "mavenorder.order_cost"]
        # need the category of the order to use it for the UI icon and order chart
        
        columns = DBMapUtils().select_rows_from_map(column_map)
        cmd=[]
        cmdargs =[]
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM mavenorder")
        cmd.append("WHERE mavenorder.encounter_id = %s AND mavenorder.customer_id = %s")
        cmdargs.append(encounter)
        cmdargs.append(customer)
        cmd.append("ORDER BY mavenorder.datetime desc")
        if limit:
            cmd.append(limit)

        cur = yield from self.db.execute_single(' '.join(cmd)+';',cmdargs)
        results = []
        y = 0
        for x in cur:
            results.append({'id': y, 'name': x[0], 'date': str(x[1]), 'result': "Active", 'cost': int(x[3]), 'category': 'med'})
            y += 1
            ML.DEBUG(x)

        return (HTTP.OK_RESPONSE, json.dumps(results), None)


if __name__ == '__main__':
    ML.DEBUG = ML.stdout_log
    MC.MavenConfig = \
        {
            "httpserver":
                {
                    SP.CONFIG_HOST: 'localhost',
                    SP.CONFIG_PORT: 8087,
                    CONFIG_DATABASE: "webservices conn pool",
                },
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
