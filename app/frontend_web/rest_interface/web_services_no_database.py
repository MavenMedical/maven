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
import asyncio
import json
import random
import pickle;
import maven_logging as ML
import maven_config as MC
from Crypto.Hash import SHA256
import base64
import itertools
import traceback
import psycopg2.extras

CONFIG_DATABASE = 'database'

CONTEXT_USER = 'user'
CONTEXT_PROVIDER = 'provider'
CONTEXT_DATE = 'date'
CONTEXT_DATERANGE = 'daterange'
CONTEXT_PATIENTLIST = 'patients'
CONTEXT_DEPARTMENT = 'department'
CONTEXT_CATEGORY = 'category'
CONTEXT_KEY = 'key'
CONTEXT_ENCOUNTER = 'encounter'


# When the user creates a list of something, every element in that list is checked to make 
# sure the user is authorized to see it.  If we later get details on that object,
# we do not want an extra database query or join just to verify the authorization.
# With the initial list, we will provide a key which will act as proof of authorization.
# This key will be a hash of a secret shared by all of our servers (possibly related to our site's
# private ssl cert), the userid, and the primary key of the returned object.
# When asking for details, if we can recreate the hash (and the user is authenticated), the user's 
# authorization is confirmed.  
# For now this is random, so it will not work between servers and is intentionally broken.
_TEMPORARY_SECRET = SHA256.new()
_TEMPORARY_SECRET.update(b'123')  #"""bytes([random.randint(0,255) for _ in range(128)]))

def _authorization_key(data):
    global _TEMPORARY_SECRET
    sha = _TEMPORARY_SECRET.copy()
    sha.update(pickle.dumps(data))
    return base64.b64encode(sha.digest())[:32].decode().replace('/','_').replace('+','-')
    

patients_list = {
    '1': {'id':'1', 'name':'Batman', 'gender':'Male', 'DOB':'05/03/1987', 'diagnosis':'Asthma'},
    '2': {'id':'2', 'name':'Wonder Woman', 'gender':'Female', 'DOB':'03/06/1986', 'diagnosis':'Coccidiosis'},
    '3': {'id':'3', 'name':'Superman', 'gender':'Male', 'DOB':'08/03/1999',  'diagnosis':'Food poisoning'},
    '4': {'id':'4', 'name':'Storm', 'gender':'Female', 'DOB':'11/07/1935', 'diagnosis':'Giardiasis'},
} 

patient_extras = {
    '1': {'Allergies': ['Penicillins','Nuts','Cats'], 'Problem List':['Asthma','Cholera']},
}

order_list = {
    '1': [{'title':'Echocardiogram', 'order':'Followup ECG', 'reason':'Mitral regurgitation', 'evidence':'Don\'t test', 'date':'1/1/2014', 'result':'','cost':1200 , 'ecost': 0},
        {'title':'Immunoglobulin','order':'place holder', 'reason':'klsdf jlkwec', 'evidence':'jmdljxs', 'date':'1/24/2014', 'result':'','cost':130 , 'ecost': 0},
        ],
}

alert_types = {
    1: {'name':'Avoid NSAIDS', 'cost':168, 'html':'<b>Avoid nonsteroidal anti-inflammatory drugs (NSAIDS)</b> in individuals with hypertension or heart failure or CKD of all causes, including diabetes.'},
    2: {'name':'Placeholder', 'cost':0, 'html':'Placeholder alert to be replaced by something real.  Consult <a href="www.google.com">google</a> for more information.'},
    3: {'name':'Placeholder', 'cost':0, 'html':'Placeholder alert to be replaced by something real.  Consult <a href="www.google.com">google</a> for more information.'},
    4: {'name':'Placeholder', 'cost':0, 'html':'Placeholder alert to be replaced by something real.  Consult <a href="www.google.com">google</a> for more information.'},
    5: {'name':'Placeholder', 'cost':0, 'html':'Placeholder alert to be replaced by something real.  Consult <a href="www.google.com">google</a> for more information.'},
}

alert_list = [
    {'id':1, 'patient':'1', 'type':1, 'date':'12/15/2013', 'action':''},
    {'id':2, 'patient':'1', 'type':2, 'date':'12/16/2013', 'action':''},
    {'id':3, 'patient':'2', 'type':1, 'date':'12/17/2013', 'action':''},
    {'id':4, 'patient':'2', 'type':3, 'date':'12/18/2013', 'action':''},
    {'id':5, 'patient':'3', 'type':2, 'date':'12/19/2013', 'action':''},
    {'id':6, 'patient':'3', 'type':3, 'date':'12/20/2013', 'action':''},
    {'id':7, 'patient':'4', 'type':4, 'date':'12/21/2013', 'action':''},
]

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

        self.add_handler(['GET'], '/patients(?:/(\d+)-(\d+)?)?', self.get_patients)
        self.add_handler(['GET'], '/patient_details', self.get_patient_details)
        self.add_handler(['GET'], '/total_spend', self.get_total_spend)
        self.add_handler(['GET'], '/spending', self.get_daily_spending)
        self.add_handler(['GET'], '/spending_details', self.get_spending_details)
        self.db = AsyncConnectionPool(db_configname)


        self.add_handler(['GET'], '/alerts(?:/(\d+)-(\d+)?)?', self.get_alerts)
#        self.add_handler(['GET'], '/alert_details', self.get_alert_details)
        self.add_handler(['GET'], '/orders(?:/(\d+)-(\d+)?)?', self.get_orders)
#        self.add_handler(['GET'], '/order_details', self.get_order_details)

    def schedule(self, loop):
        HTTP.HTTPProcessor.schedule(self, loop)
        self.db.schedule(loop)


    @asyncio.coroutine
    def get_stub(self, _header, _body, _qs, _matches, _key):
        return (HTTP.OK_RESPONSE, b'', None)

    patients_required_contexts = [CONTEXT_USER]
    patients_available_contexts = {CONTEXT_USER:str, 'customer_id': int, CONTEXT_ENCOUNTER: str}

    @asyncio.coroutine
    def get_patients(self, _header, _body, qs, matches, _key):


        # {1: {'id':1, 'name':'Batman', 'gender':'Male', 'DOB':'05/03/1987', 'diagnosis':'Asthma'},}
        #Need to return LIST OF MAP OBJECTS [id, key, diagnosis, name, gender, DOB]
        ### TODO - SQL query
        # SELECT FROM encounter join patient
        # WHERE visit_prov_id = user
        # (potential) GROUP
        ### TODO - Remove hardcoded user context and replace with values from production authentication module
        qs['user'] = ['JHU1093124']
        qs['customer_id'] = [1]
        qs['encounter'] = ['987987917']

        context = restrict_context(qs,
                                   FrontendWebService.patients_required_contexts,
                                   FrontendWebService.patients_available_contexts)
        user = context[CONTEXT_USER]
        encounter = context[CONTEXT_ENCOUNTER]
        (start, stop) = _get_range(matches, len(patients_list))


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
                results.append({'id': x[0], 'name': x[2], 'gender': x[5], 'DOB': str(x[4]), 'diagnosis': 'Sinusitis', 'key': _authorization_key((user, x[0]))})
                ML.DEBUG(json.dumps(results))
        except:
            raise Exception('Error in front end webservices get_patients() call to database')


        ### TODO - SQL query
        # SELECT FROM encounterdx join encounter
        # WHERE visit_prov_id = user
        # (potential) GROUP
        ###
        global patients_list



        #patient_cursor = yield from self.db.execute_single('select patname, sex, birth_month from patient')
        #print("patient cursor ")

        #pat =[]
        #for r in patient_cursor:
        #    pat.append(r)
        #    print(r)

        patient_list = [copy_and_append(v, (CONTEXT_KEY,_authorization_key((user, v['id'])))) 
                        for v in patients_list.values()][start:stop]
        ML.DEBUG(json.dumps(patient_list))

        return (HTTP.OK_RESPONSE, json.dumps(patient_list), None)

    patient_required_contexts = [CONTEXT_USER,CONTEXT_KEY,CONTEXT_PATIENTLIST]
    patient_available_contexts = {CONTEXT_USER:str,CONTEXT_KEY:str,CONTEXT_PATIENTLIST:str}

    @asyncio.coroutine
    def get_patient_details(self, _header, _body, qs, matches, _key):
        """
        This method returns Patient Details which include the data in the header of the Encounter Page
            i.e. Allergies Problem List, Last Encounter, others.
        """
        global patients_list
        context = restrict_context(qs, 
                                   FrontendWebService.patient_required_contexts,
                                   FrontendWebService.patient_available_contexts)
        user = context[CONTEXT_USER]
        patient_id = context[CONTEXT_PATIENTLIST]
        auth_key = context[CONTEXT_KEY]
        if not auth_key == _authorization_key((user, patient_id)):
            raise HTTP.IncompleteRequest('%s has not been authorized to view patient %d.' % (user, patient_id))
        patient_dict = dict(patients_list[patient_id])
        if patient_id in patient_extras:
            patient_dict.update(patient_extras[patient_id])
        return (HTTP.OK_RESPONSE, json.dumps(patient_dict), None)


    totals_required_contexts = [CONTEXT_USER,CONTEXT_KEY,CONTEXT_PATIENTLIST]
    totals_available_contexts = {CONTEXT_USER:str,CONTEXT_KEY:list,CONTEXT_PATIENTLIST:list}

    @asyncio.coroutine
    def get_total_spend(self, _header, _body, _qs, _matches, _key):
        ret = {'spending':85100, 'savings':1000}
        return (HTTP.OK_RESPONSE, json.dumps(ret), None)


    daily_required_contexts = [CONTEXT_USER,CONTEXT_KEY,CONTEXT_PATIENTLIST]
    daily_available_contexts = {CONTEXT_USER:str,CONTEXT_KEY:list,CONTEXT_PATIENTLIST:list}

    @asyncio.coroutine
    def get_daily_spending(self, _header, _body, qs, _matches, _key):
        global patient_spending
        context = restrict_context(qs, 
                                   FrontendWebService.daily_required_contexts,
                                   FrontendWebService.daily_available_contexts)
        user = context[CONTEXT_USER]
        patient_ids = context[CONTEXT_PATIENTLIST]
        auth_keys = dict(zip(patient_ids,context[CONTEXT_KEY]))
        
        patient_dict = {}
        for patient_id in set(patient_ids).intersection(patient_spending.keys()):
            try:
                if _authorization_key((user, patient_id)) == auth_keys[patient_id]:
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
        qs['user'] = 'JHU1093124'
        qs['customer_id'] = 1
        qs['encounter'] = '987987917'

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
    alerts_available_contexts = {CONTEXT_USER:str, CONTEXT_PATIENTLIST:list}
    
    @asyncio.coroutine
    def get_alerts(self, _header, _body, qs, _matches, _key):
        global alert_list
        global alert_types
        context = restrict_context(qs, 
                                   FrontendWebService.alerts_required_contexts,
                                   FrontendWebService.alerts_available_contexts)
        user = context[CONTEXT_USER]
        if CONTEXT_PATIENTLIST in context:
            patient_ids = context[CONTEXT_PATIENTLIST]
            print(patient_ids)
            print(alert_list)
            print(list(filter(lambda s: s['patient'] in patient_ids, alert_list)))
            print()
            response_list = [dict(itertools.chain(l.items(),alert_types[l['type']].items())) for l in filter(lambda s: s['patient'] in patient_ids, alert_list)]
        else:
            response_list = [dict(itertools.chain(l.items(),alert_types[l['type']].items())) for l in alert_list]
            
        #auth_keys = dict(zip(patient_ids,context[CONTEXT_KEY]))
        
        return (HTTP.OK_RESPONSE, json.dumps(response_list), None)


    #self.add_handler(['GET'], '/alert_details', self.get_stub)
    def get_alert_details(self, _header, _body, qs, _matches, _key):
        return (HTTP.OK_RESPONSE, b'', None)

    orders_required_contexts = [CONTEXT_USER, CONTEXT_PATIENTLIST]
    orders_available_contexts = {CONTEXT_USER:str, CONTEXT_PATIENTLIST:list}

    #self.add_handler(['GET'], '/orders(?:/(\d+)-(\d+)?)?', self.get_stub)
    @asyncio.coroutine
    def get_orders(self, _header, _body, qs, _matches, _key):
        ### TODO - Remove hardcoded user context and replace with values from production authentication module
        qs['user'] = 'JHU1093124'
        qs['customer_id'] = 1
        qs['encounter'] = '987987917'

        global order_list
        context = restrict_context(qs, 
                                   FrontendWebService.orders_required_contexts,
                                   FrontendWebService.orders_available_contexts)
        user = context[CONTEXT_USER]
        patient_ids = context[CONTEXT_PATIENTLIST]
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
                                           " WHERE mavenorder.encounter_id = '%s' AND encounter.customer_id = %s;" % (columns, qs['encounter'], qs['customer_id']))
            results = []
            for x in cur:
                results.append(x)
                ML.DEBUG(x)

        except:
            raise Exception("Error querying encounter orders from the database")


        for patient_id in set(patient_ids).intersection(order_list.keys()):
            try:
                #if _authorization_key((user, patient_id)) == auth_keys[patient_id]:
                order_dict[patient_id]=order_list[patient_id]
            except TypeError:
                pass
        print(order_dict)
        return (HTTP.OK_RESPONSE, json.dumps(order_dict[1]), None)


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
                ("dbname=%s user=%s password=%s host=%s port=%s" % ('maven', 'maven', 'temporary', 'localhost', '5432')),
                AsyncConnectionPool.CONFIG_MIN_CONNECTIONS: 4,
                AsyncConnectionPool.CONFIG_MAX_CONNECTIONS: 8
            }
        }
    hp = FrontendWebService('httpserver')
    event_loop = asyncio.get_event_loop()
    hp.schedule(event_loop)
    event_loop.run_forever()
