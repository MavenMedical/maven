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

CONFIG_DATABASE = 'database'

CONTEXT_USER = 'user'
CONTEXT_PROVIDER = 'provider'
CONTEXT_DATE = 'date'
CONTEXT_DATERANGE = 'daterange'
CONTEXT_PATIENTLIST = 'patients'
CONTEXT_DEPARTMENT = 'department'
CONTEXT_CATEGORY = 'category'
CONTEXT_KEY = 'key'


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
    

patients = {
    1: {'id':1, 'name':'Jordon Severt', 'gender':'Male', 'DOB':'05/03/1987', 'diagnosis':'Asthma'},
    2: {'id':2, 'name':'Adaline Malachi', 'gender':'Female', 'DOB':'03/06/1986', 'diagnosis':'Coccidiosis'},
    3: {'id':3, 'name':'Jefferson Lariviere', 'gender':'Male', 'DOB':'08/03/1999',  'diagnosis':'Food poisoning'},
    4: {'id':4, 'name':'Beulah Gay', 'gender':'Female', 'DOB':'11/07/1935', 'diagnosis':'Giardiasis'},
} 

patient_extras = {
    1: {'Allergies': ['Penicillins','Nuts','Cats'], 'Problem List':['Asthma','Cholera']},
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
    1: create_spend(100, .1,.5),
    2: create_spend(100,.2,.3),
    3: create_spend(200,.05,.8),
    4: create_spend(100,.1,.5),
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
        self.add_handler(['GET'], '/total_savings', self.get_total_savings)
        self.add_handler(['GET'], '/spending', self.get_daily_spending)
        self.add_handler(['GET'], '/spending_details', self.get_spending_details)
        self.db = AsyncConnectionPool(db_configname)


        self.add_handler(['GET'], '/alerts(?:/(\d+)-(\d+)?)?', self.get_alerts)
        self.add_handler(['GET'], '/alert_details', self.get_alert_details)
        self.add_handler(['GET'], '/orders(?:/(\d+)-(\d+)?)?', self.get_orders)
        self.add_handler(['GET'], '/order_details', self.get_order_details)

    def schedule(self, loop):
        HTTP.HTTPProcessor.schedule(self, loop)
        self.db.schedule(loop)


    @asyncio.coroutine
    def get_stub(self, _header, _body, _qs, _matches, _key):
        return (HTTP.OK_RESPONSE, b'', None)

    patients_required_contexts = [CONTEXT_USER]
    patients_available_contexts = {CONTEXT_USER:str}

    @asyncio.coroutine
    def get_patients(self, _header, _body, qs, matches, _key):
        global patients

        context = restrict_context(qs, 
                                   FrontendWebService.patients_required_contexts,
                                   FrontendWebService.patients_available_contexts)
        user = context[CONTEXT_USER]
        (start, stop) = _get_range(matches, len(patients))

        patient_cursor = yield from self.db.execute_single('select patname, sex, birth_month from patient')
        print("patient cursor ")

        pat =[]
        for r in patient_cursor:
            pat.append(r)
            print(r)

        patient_list = [copy_and_append(v, (CONTEXT_KEY,_authorization_key((user, v['id'])))) 
                        for v in patients.values()][start:stop]
        print(patient_list)
        return (HTTP.OK_RESPONSE, json.dumps(patient_list), None)

    patient_required_contexts = [CONTEXT_USER,CONTEXT_KEY,CONTEXT_PATIENTLIST]
    patient_available_contexts = {CONTEXT_USER:str,CONTEXT_KEY:str,CONTEXT_PATIENTLIST:int}

    @asyncio.coroutine
    def get_patient_details(self, _header, _body, qs, matches, _key):
        global patients
        context = restrict_context(qs, 
                                   FrontendWebService.patient_required_contexts,
                                   FrontendWebService.patient_available_contexts)
        user = context[CONTEXT_USER]
        patient_id = context[CONTEXT_PATIENTLIST]
        auth_key = context[CONTEXT_KEY]
        if not auth_key == _authorization_key((user, patient_id)):
            raise HTTP.IncompleteRequest('%s has not been authorized to view patient %d.' % (user, patient_id))
        patient_dict = dict(patients[patient_id])
        if patient_id in patient_extras:
            patient_dict.update(patient_extras[patient_id])
        return (HTTP.OK_RESPONSE, json.dumps(patient_dict), None)

    @asyncio.coroutine
    def get_total_spend(self, _header, _body, _qs, _matches, _key):
        return (HTTP.OK_RESPONSE, json.dumps(95100), None)

    @asyncio.coroutine
    def get_total_savings(self, _header, _body, _qs, _matches, _key):
        return (HTTP.OK_RESPONSE, json.dumps(10700), None)

    daily_required_contexts = [CONTEXT_USER,CONTEXT_KEY,CONTEXT_PATIENTLIST]
    daily_available_contexts = {CONTEXT_USER:str,CONTEXT_KEY:list,CONTEXT_PATIENTLIST:list}

    @asyncio.coroutine
    def get_daily_spending(self, _header, _body, qs, _matches, _key):
        global patient_spending
        context = restrict_context(qs, 
                                   FrontendWebService.daily_required_contexts,
                                   FrontendWebService.daily_available_contexts)
        user = context[CONTEXT_USER]
        patient_ids = list(map(int,context[CONTEXT_PATIENTLIST]))
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
    spending_available_contexts = {CONTEXT_USER:str,CONTEXT_PATIENTLIST:int,CONTEXT_DATE:int}

    @asyncio.coroutine
    def get_spending_details(self, _header, _body, qs, _matches, _key):
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
    def get_alerts(self, _header, _body, qs, _matches, _key):
        return (HTTP.OK_RESPONSE, b'', None)


    #self.add_handler(['GET'], '/alert_details', self.get_stub)
    def get_alert_details(self, _header, _body, qs, _matches, _key):
        return (HTTP.OK_RESPONSE, b'', None)

    #self.add_handler(['GET'], '/orders(?:/(\d+)-(\d+)?)?', self.get_stub)
    def get_orders(self, _header, _body, qs, _matches, _key):
        return (HTTP.OK_RESPONSE, b'', None)

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
                    CONFIG_DATABASE: "test conn pool",
                },
            'test conn pool': {
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
