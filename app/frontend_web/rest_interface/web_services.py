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

from app.utils.database.database import AsyncConnectionPool
from app.utils.database.database import MappingUtilites as DBMapUtils
import app.utils.streaming.stream_processor as SP
import app.utils.streaming.http_responder as HTTP
import app.utils.crypto.authorization_key as AK
import asyncio
import json
import random
import maven_logging as ML
import maven_config as MC
import itertools
import traceback
import psycopg2.extras
import datetime
import dateutil.parser as prsr
import time

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

patient_extras = {
    '9': {'Allergies': ['Penicillins'], 'Problem List':['Sinusitis', 'Asthma']},
}

def min_zero_normal(u,s):
    ret = int(random.normalvariate(u,s))
    if ret<0:
        ret=0
    return ret

def spending():
    return {
        'Labs':min_zero_normal(100,50),
        'Medications':min_zero_normal(300,100),
        'Procedures':min_zero_normal(500,300),
        'Room':min_zero_normal(500,50),
        }


encounter = 0

def create_spend(days, prob_fall_ill, prob_stay_ill):
    state = None
    history = {}
    global encounter
    for i in range(days):
        r = random.uniform(0,1)
        oldstate = state
        state = (state and prob_stay_ill<r) or (not state and prob_fall_ill<r)
        if not oldstate and state:
            encounter += 1
        if state:
            history[i]=spending()
            history[i]['encounter']=str(encounter)
    return history

patient_spending = {
    '1': create_spend(100, .1,.5),
    '2': create_spend(100,.2,.3),
    '3': create_spend(200,.05,.8),
    '4': create_spend(100,.1,.5),
}

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

def _get_range(tup, max):
    try:
        (start, stop) = tuple(map(int,tup))
        stop += 1
    except (ValueError, TypeError):
        (start, stop) = (0, max)
    if stop > max:
        stop = max
    return (start, stop)

def restrict_context(qs, required, available):
    if not set(required).issubset(qs.keys()):
        raise HTTP.IncompleteRequest('Request is incomplete.  Required arguments are: '+', '.join(required)+".\n")
    # not implemented yet - making sure optional parameters are the right type

    if not CONTEXT_KEY in qs:
        raise HTTP.UnauthorizedRequest('User is not logged in.')
    try:
        AK.check_authorization(qs['user'][0], qs[CONTEXT_KEY][0], AUTH_LENGTH)
    except AK.UnauthorizedException as ue:
        raise HTTP.UnauthorizatedRequest(str(ue))

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

class FrontendWebService(HTTP.HTTPProcessor):

    def __init__(self, configname):
        HTTP.HTTPProcessor.__init__(self,configname)
        try:
            db_configname = self.config[CONFIG_DATABASE]
        except KeyError:
            raise MC.InvalidConfig('some real error')

        self.add_handler(['POST'], '/login', self.post_login)
        self.add_handler(['GET'], '/patients(?:/(\d+)-(\d+)?)?', self.get_patients)
        self.add_handler(['GET'], '/patient_details', self.get_patient_details)
        self.add_handler(['GET'], '/total_spend', self.get_total_spend)
        self.add_handler(['GET'], '/spending', self.get_daily_spending)
        self.add_handler(['GET'], '/spending_details', self.get_spending_details)
        self.add_handler(['GET'], '/alerts(?:/(\d+)-(\d+)?)?', self.get_alerts)
        self.add_handler(['GET'], '/orders(?:/(\d+)-(\d+)?)?', self.get_orders)
        self.db = AsyncConnectionPool(db_configname)

    def schedule(self, loop):
        HTTP.HTTPProcessor.schedule(self, loop)
        self.db.schedule(loop)


    @asyncio.coroutine
    def get_stub(self, _header, _body, _qs, _matches, _key):
        return (HTTP.OK_RESPONSE, b'', None)

    @asyncio.coroutine
    def post_login(self, _header, body, _qs, _matches, _key):
        info = json.loads(body.decode('utf-8'))
        if (not 'user' in info) or (not 'password' in info):
            return (HTTP.BAD_RESPONSE, b'', None)
        else:
            user = info['user']
            try:
                AK.check_authorization(user, info['password'], AUTH_LENGTH)
                return (HTTP.OK_RESPONSE, json.dumps({'display':'Dr. Huxtable'}), None)
            except:
                user_auth = AK.authorization_key(user,AUTH_LENGTH, LOGIN_TIMEOUT)
                return (HTTP.OK_RESPONSE,json.dumps({CONTEXT_KEY:user_auth, 'display':'Dr. Huxtable'}), None)

    patients_required_contexts = [CONTEXT_USER]
    patients_available_contexts = {CONTEXT_USER:str, 'customer_id': int, CONTEXT_ENCOUNTER: str}

    @asyncio.coroutine
    def get_patients(self, _header, _body, qs, matches, _key):


        # {1: {'id':1, 'name':'Batman', 'gender':'Male', 'DOB':'05/03/1987', 'diagnosis':'Asthma'},}
        ### TODO - Remove hardcoded user context and replace with values from production authentication module
        qs['customer_id'] = [1]
        qs['encounter'] = ['987987917']

        context = restrict_context(qs,
                                   FrontendWebService.patients_required_contexts,
                                   FrontendWebService.patients_available_contexts)
        user = context[CONTEXT_USER]
        encounter = context[CONTEXT_ENCOUNTER]


        try:
            column_map = ["encounter.csn",
                          "encounter.contact_date",
                          "patient.patname",
                          "encounter.pat_id",
                          "patient.birthdate",
                          "patient.sex"]

            columns = DBMapUtils().select_rows_from_map(column_map)
            cur = yield from self.db.execute_single("SELECT DISTINCT %s"
                                           " from patient JOIN encounter"
                                           " on (patient.pat_id = encounter.pat_id and encounter.customer_id = %s)"
                                           " WHERE encounter.visit_prov_id = '%s' AND encounter.customer_id = %s;" % (columns, context['customer_id'], context['user'], context['customer_id']))
            results = []
            for x in cur:
                if x[5][0]=='F':
                    cost = 1335
                else:
                    cost = 1200
                results.append({'id': x[3], 'name': prettify(x[2], type="name"), 'gender': prettify(x[5], type="sex"), 'DOB': str(x[4]), 'diagnosis': 'Sinusitis', 'key': AK.authorization_key((user, x[3]), AUTH_LENGTH), 'cost':cost})
                ML.DEBUG(json.dumps(results))
        except:
            raise Exception('Error in front end webservices get_patients() call to database')


        return (HTTP.OK_RESPONSE, json.dumps(results), None)

    patient_required_contexts = [CONTEXT_USER,CONTEXT_KEY,CONTEXT_PATIENTLIST]
    patient_available_contexts = {CONTEXT_USER:str,CONTEXT_KEY:str,CONTEXT_PATIENTLIST:str, CONTEXT_CUSTOMERID:int, CONTEXT_ENCOUNTER:str}

    @asyncio.coroutine
    def get_patient_details(self, _header, _body, qs, matches, _key):
        """
        This method returns Patient Details which include the data in the header of the Encounter Page
            i.e. Allergies Problem List, Last Encounter, others.
        """
        qs['customer_id'] = [1]
        qs['encounter'] = ['5|76|3140325']

        context = restrict_context(qs,
                                   FrontendWebService.patient_required_contexts,
                                   FrontendWebService.patient_available_contexts)
        user = context[CONTEXT_USER]
        patient_id = context[CONTEXT_PATIENTLIST]
        auth_key = context[CONTEXT_KEY]
        customer = context[CONTEXT_CUSTOMERID]
        #if not auth_key == _authorization_key((user, patient_id), AUTH_LENGTH):
         #   raise HTTP.IncompleteRequest('%s has not been authorized to view patient %s.' % (user, patient_id))

        try:
            column_map = ["patient.pat_id",
                          "patient.patname",
                          "patient.birthdate",
                          "patient.sex"]

            columns = DBMapUtils().select_rows_from_map(column_map)
            cur = yield from self.db.execute_single("SELECT %s"
                                           " from patient"
                                           " WHERE patient.pat_id = '%s' AND patient.customer_id = %s;" % (columns, patient_id, customer))
            x = next(cur)
            results = {'id': x[0], 'name': prettify(x[1], type="name"), 'gender': prettify(x[3], type="sex"), 'DOB': str(x[2]), 'diagnosis': 'Sinusitis', 'key': AK.authorization_key((user, x[0]), AUTH_LENGTH)}
            ML.DEBUG(json.dumps(results))
        except:
            raise Exception('Error in front end webservices get_patients() call to database')


        if patient_id in patient_extras:
            results.update(patient_extras[patient_id])
        return (HTTP.OK_RESPONSE, json.dumps(results), None)


    totals_required_contexts = [CONTEXT_USER,CONTEXT_KEY]
    totals_available_contexts = {CONTEXT_USER:str,CONTEXT_KEY:list,CONTEXT_PATIENTLIST:list}

    @asyncio.coroutine
    def get_total_spend(self, _header, _body, _qs, _matches, _key):
        ret = {'spending':1355, 'savings':16}
        return (HTTP.OK_RESPONSE, json.dumps(ret), None)


    daily_required_contexts = [CONTEXT_USER,CONTEXT_KEY]
    daily_available_contexts = {CONTEXT_USER:str,CONTEXT_KEY:list,CONTEXT_PATIENTLIST:list}

    @asyncio.coroutine
    def get_daily_spending(self, _header, _body, qs, _matches, _key):
        global patient_spending
        context = restrict_context(qs,
                                   FrontendWebService.daily_required_contexts,
                                   FrontendWebService.daily_available_contexts)
        user = context[CONTEXT_USER]
        patient_dict = {}
        if CONTEXT_PATIENTLIST in context:
            patient_ids = context[CONTEXT_PATIENTLIST]
            auth_keys = dict(zip(patient_ids,context[CONTEXT_KEY]))
            
            for patient_id in set(patient_ids).intersection(patient_spending.keys()):
                try:
                    if AK.check_authorization((user, patient_id), auth_keys[patient_id], AUTH_LENGTH):
                        patient_dict[patient_id]=dict([(k,sum(map(lambda x: x if type(x) is int else 0,
                                                                  v.values())))
                                                       for k,v in patient_spending[patient_id].items()])
                except TypeError:
                    pass

        return (HTTP.OK_RESPONSE, json.dumps(patient_dict), None)

    spending_required_contexts = [CONTEXT_USER,CONTEXT_PATIENTLIST,CONTEXT_DATE]
    spending_available_contexts = {CONTEXT_USER:str,CONTEXT_PATIENTLIST:str,CONTEXT_DATE:int}

    @asyncio.coroutine
    def get_spending_details(self, _header, _body, qs, _matches, _key):
        qs['customer_id'] = [1]
        qs['encounter'] = ['987987917']

        global patient_spending
        context = restrict_context(qs,
                                   FrontendWebService.spending_required_contexts,
                                   FrontendWebService.spending_available_contexts)
        user = context[CONTEXT_USER]
        patient_id = context[CONTEXT_PATIENTLIST]
        date = context[CONTEXT_DATE]
        print(patient_spending[patient_id])
        print(patient_spending[patient_id][date])
        print(date)
        spend = patient_spending.get(patient_id,{}).get(date,{})
        return (HTTP.OK_RESPONSE, json.dumps(spend), None)

    #self.add_handler(['GET'], '/alerts(?:/(\d+)-(\d+)?)?', self.get_stub)

    alerts_required_contexts = [CONTEXT_USER]
    alerts_available_contexts = {CONTEXT_USER:str, CONTEXT_PATIENTLIST:list, CONTEXT_CUSTOMERID:int, CONTEXT_ENCOUNTER:str}

    @asyncio.coroutine
    def get_alerts(self, _header, _body, qs, _matches, _key):

        qs['customer_id'] = [1]
        qs['encounter'] = ['987987917']

        context = restrict_context(qs,
                                   FrontendWebService.alerts_required_contexts,
                                   FrontendWebService.alerts_available_contexts)
        user = context[CONTEXT_USER]
        patient = context[CONTEXT_PATIENTLIST][0]
        customer = context[CONTEXT_CUSTOMERID]

        try:
            column_map = ["alerts.alert_id",
                          "alerts.pat_id",
                          "alerts.encounter_date",
                          "alerts.alert_date",
                          "alerts.alert_title",
                          "alerts.alert_msg",
                          "alerts.action",
                          "alerts.saving"]

            columns = DBMapUtils().select_rows_from_map(column_map)
            cur = yield from self.db.execute_single("SELECT %s"
                                                    " from alerts"
                                                    " WHERE alerts.pat_id = '%s' AND alerts.customer_id = %s;" % (columns, patient, customer))
            results = []
            for x in cur:
                results.append({'id': x[0], 'patient': x[1], 'name':x[4], 'cost': x[7], 'html': x[5], 'date': str(x[2])})
                ML.DEBUG(json.dumps(results))
        except:
            raise Exception('Error in front end webservices get_patients() call to database')

        #auth_keys = dict(zip(patient_ids,context[CONTEXT_KEY]))

        return (HTTP.OK_RESPONSE, json.dumps(results), None)


    #self.add_handler(['GET'], '/alert_details', self.get_stub)
    def get_alert_details(self, _header, _body, qs, _matches, _key):
        return (HTTP.OK_RESPONSE, b'', None)

    orders_required_contexts = [CONTEXT_USER, CONTEXT_PATIENTLIST]
    orders_available_contexts = {CONTEXT_USER:str, CONTEXT_PATIENTLIST:list, CONTEXT_CUSTOMERID:int, CONTEXT_ENCOUNTER:str}

    #self.add_handler(['GET'], '/orders(?:/(\d+)-(\d+)?)?', self.get_stub)
    @asyncio.coroutine
    def get_orders(self, _header, _body, qs, _matches, _key):
        ### TODO - Remove hardcoded user context and replace with values from production authentication module
        qs['customer_id'] = [1]
        qs['encounter'] = ['9|76|3140328']

        context = restrict_context(qs,
                                   FrontendWebService.orders_required_contexts,
                                   FrontendWebService.orders_available_contexts)
        user = context[CONTEXT_USER]
        patient_ids = context[CONTEXT_PATIENTLIST]
        #encounter = context[CONTEXT_ENCOUNTER]
        #auth_keys = dict(zip(patient_ids,context[CONTEXT_KEY]))

        order_dict = {}

        try:
            column_map = ["mavenorder.order_name",
                          "mavenorder.datetime",
                          "mavenorder.active",
                          "mavenorder.order_cost"]

            columns = DBMapUtils().select_rows_from_map(column_map)
            cur = yield from self.db.execute_single("SELECT %s"
                                           " from mavenorder"
                                           " WHERE mavenorder.encounter_id = '%s' AND mavenorder.customer_id = %s;" % (columns, context['encounter'], context['customer_id']))
            results = []
            for x in cur:
                results.append({'name': x[0], 'date': str(x[1]), 'result': "Active", 'cost': int(x[3])})
                ML.DEBUG(x)

        except:
            raise Exception("Error querying encounter orders from the database")


        return (HTTP.OK_RESPONSE, json.dumps(results), None)


    #self.add_handler(['GET'], '/order_details', self.get_stub)
    def get_order_details(self, _header, _body, qs, _matches, _key):
        return (HTTP.OK_RESPONSE, b'', None)



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
                AsyncConnectionPool.CONFIG_CONNECTION_STRING:
                ("dbname=%s user=%s password=%s host=%s port=%s" % ('maven', 'maven', 'temporary', MC.dbhost, '5432')),
                AsyncConnectionPool.CONFIG_MIN_CONNECTIONS: 4,
                AsyncConnectionPool.CONFIG_MAX_CONNECTIONS: 8
            }
        }
    hp = FrontendWebService('httpserver')
    event_loop = asyncio.get_event_loop()
    hp.schedule(event_loop)
    event_loop.run_forever()
