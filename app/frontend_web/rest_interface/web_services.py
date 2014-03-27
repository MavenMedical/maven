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
            pass #db_configname = self.config[CONFIG_DATABASE]
        except KeyError:
            raise MC.InvalidConfig('some real error')

        self.db = AsyncConnectionPool(db_configname)

        self.add_handler(['GET'], '/patients(?:/(\d+)-(\d+)?)?', self.get_patients)
        self.add_handler(['GET'], '/patient_details', self.get_patient_details)
        self.add_handler(['GET'], '/total_spend', self.get_total_spend)
        self.add_handler(['GET'], '/total_savings', self.get_total_savings)
        self.add_handler(['GET'], '/spending', self.get_daily_spending)
        self.add_handler(['GET'], '/spending_details', self.get_spending_details)
<<<<<<< HEAD
        #self.db = AsyncConnectionPool(db_configname)


=======
>>>>>>> ce96b68f8e6299196cb06b797a3683e03e554e33
        self.add_handler(['GET'], '/alerts(?:/(\d+)-(\d+)?)?', self.get_alerts)
        self.add_handler(['GET'], '/orders(?:/(\d+)-(\d+)?)?', self.get_orders)

    def schedule(self, loop):
        HTTP.HTTPProcessor.schedule(self, loop)
        #self.db.schedule(loop)


    #@asyncio.coroutine
    #def get_stub(self, _header, _body, _qs, _matches, _key):
    #    return (HTTP.OK_RESPONSE, b'', None)

    patients_required_contexts = [CONTEXT_USER]
    patients_available_contexts = {CONTEXT_USER:str}

    @asyncio.coroutine
    def get_patients(self, _header, _body, qs, matches, _key):
        context = restrict_context(qs, 
                                   FrontendWebService.patients_required_contexts,
                                   FrontendWebService.patients_available_contexts)
        user = context[CONTEXT_USER]
        (start, stop) = _get_range(matches, len(patients_list))

<<<<<<< HEAD
        '''patient_cursor = yield from self.db.execute_single('select patname, sex, birth_month from patient')
        print("patient cursor ")

        pat =[]
        for r in patient_cursor:
            pat.append(r)
            print(r)'''

        patient_list = [copy_and_append(v, (CONTEXT_KEY,_authorization_key((user, v['id']))))
                        for v in patients.values()][start:stop]
=======
        patient_cursor = yield from self.db.execute_single('select pat_id, customer_id, patname, sex, birth_month from patient')
        print("patient cursor ")

        #pat =[]
        #for r in patient_cursor:
        #    pat.append(r)
        #    print(r)

        patient_list = [copy_and_append(v, (CONTEXT_KEY,_authorization_key((user, v['id'])))) 
                        for v in patients_list.values()][start:stop]
>>>>>>> ce96b68f8e6299196cb06b797a3683e03e554e33
        print(patient_list)
        return (HTTP.OK_RESPONSE, json.dumps(patient_list), None)

    patient_required_contexts = [CONTEXT_USER,CONTEXT_KEY,CONTEXT_PATIENTLIST]
    patient_available_contexts = {CONTEXT_USER:str,CONTEXT_KEY:str,CONTEXT_PATIENTLIST:int}

    @asyncio.coroutine
    def get_patient_details(self, _header, _body, qs, matches, _key):
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
    
    alerts_required_contexts = [CONTEXT_USER, CONTEXT_PATIENTLIST]
    alerts_available_contexts = {CONTEXT_USER:str, CONTEXT_PATIENTLIST:list}
    
    @asyncio.coroutine
    def get_alerts(self, _header, _body, qs, _matches, _key):
        context = restrict_context(qs, 
                                   FrontendWebService.alerts_required_contexts,
                                   FrontendWebService.alerts_available_contexts)
        user = context[CONTEXT_USER]
        patient_ids = list(map(int,context[CONTEXT_PATIENTLIST]))
        #auth_keys = dict(zip(patient_ids,context[CONTEXT_KEY]))
        
        response_list = [dict(itertools.chain(l.items(),alert_types[l['type']].items())) for l in filter(lambda s: s['patient'] in patient_ids, alert_list)]
        
        return (HTTP.OK_RESPONSE, json.dumps(response_list), None)




    orders_required_contexts = [CONTEXT_USER, CONTEXT_PATIENTLIST]
    orders_available_contexts = {CONTEXT_USER:str, CONTEXT_PATIENTLIST:list}

    #self.add_handler(['GET'], '/orders(?:/(\d+)-(\d+)?)?', self.get_stub)
    @asyncio.coroutine
    def get_orders(self, _header, _body, qs, _matches, _key):
        context = restrict_context(qs, 
                                   FrontendWebService.orders_required_contexts,
                                   FrontendWebService.orders_available_contexts)
        user = context[CONTEXT_USER]
        patient_ids = list(map(int,context[CONTEXT_PATIENTLIST]))
        #auth_keys = dict(zip(patient_ids,context[CONTEXT_KEY]))
        
        order_dict = {}
        for patient_id in set(patient_ids).intersection(order_list.keys()):
            try:
                #if _authorization_key((user, patient_id)) == auth_keys[patient_id]:
                order_dict[patient_id]=order_list[patient_id]
            except TypeError:
                pass

        return (HTTP.OK_RESPONSE, json.dumps(order_dict), None)


if __name__ == '__main__':
    ML.DEBUG = ML.stdout_log
    MC.MavenConfig = \
        {
            "httpserver":
                {
                    SP.CONFIG_HOST: 'localhost',
                    SP.CONFIG_PORT: 8087,
                    #CONFIG_DATABASE: "test conn pool",
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
