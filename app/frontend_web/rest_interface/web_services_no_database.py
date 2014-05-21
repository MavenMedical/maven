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

import utils.streaming.stream_processor as SP
import utils.streaming.http_responder as HTTP
import asyncio

import utils.crypto.authorization_key as AK
import maven_logging as ML
import maven_config as MC


CONTEXT_USER = 'user'
CONTEXT_PROVIDER = 'provider'
CONTEXT_DATE = 'date'
CONTEXT_DATERANGE = 'daterange'
CONTEXT_PATIENTLIST = 'patients'
CONTEXT_DEPARTMENT = 'department'
CONTEXT_CATEGORY = 'category'
CONTEXT_KEY = 'userAuth'

LOGIN_TIMEOUT = 60 * 60 # 1 hour
AUTH_LENGTH = 10 # ok for this fake data - not for real

patients_list = {
    '1': {'id':'1', 'name':'Batman', 'gender':'Male', 'DOB':'05/03/1987', 'diagnosis':'Asthma', 'cost':-1},
    '2': {'id':'2', 'name':'Wonder Woman', 'gender':'Female', 'DOB':'03/06/1986', 'diagnosis':'Coccidiosis', 'cost':-1},
    '3': {'id':'3', 'name':'Superman', 'gender':'Male', 'DOB':'08/03/1999',  'diagnosis':'Food poisoning', 'cost':-1},
    '4': {'id':'4', 'name':'Storm', 'gender':'Female', 'DOB':'11/07/1935', 'diagnosis':'Giardiasis', 'cost':-1},
} 

patient_extras = {
    '1': {'Allergies': ['Penicillins','Nuts','Cats'], 'ProblemList':['Asthma','Cholera']},
}

order_list = {
    '1': [{'id':'1','name':'Echocardiogram', 'order':'Followup ECG', 'reason':'Mitral regurgitation', 'evidence':'Don\'t test', 'date':'1/1/2014', 'result':'','cost':1200 , 'ecost': 0},
        {'id':'2', 'name':'Immunoglobulin','order':'place holder', 'reason':'klsdf jlkwec', 'evidence':'jmdljxs', 'date':'1/24/2014', 'result':'','cost':130 , 'ecost': 0},
        ],
}

alert_types = {
    1: {'name':'Avoid NSAIDS', 'cost':168, 'html':'<b>Avoid nonsteroidal anti-inflammatory drugs (NSAIDS)</b> in individuals with hypertension or heart failure or CKD of all causes, including diabetes.'},
    2: {'name':'Placeholder', 'cost':0, 'html':'Placeholder alert to be replaced by something real.  Consult <a href="https://www.google.com">google</a> for more information.'},
    3: {'name':'Placeholder', 'cost':0, 'html':'Placeholder alert to be replaced by something real.  Consult <a href="https://www.google.com">google</a> for more information.'},
    4: {'name':'Placeholder', 'cost':0, 'html':'Placeholder alert to be replaced by something real.  Consult <a href="https://www.google.com">google</a> for more information.'},
    5: {'name':'Placeholder', 'cost':0, 'html':'Placeholder alert to be replaced by something real.  Consult <a href="https://www.google.com">google</a> for more information.'},
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

with open('/usr/share/dict/words') as f:
    words = list([x.strip() for x in f.readlines()])
    words.sort(key=str.casefold)

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
    
    if not CONTEXT_KEY in qs:
        raise HTTP.UnauthorizedRequest('User is not logged in.')
    try:
        AK.check_authorization(qs['user'][0], qs[CONTEXT_KEY][0], AUTH_LENGTH)
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

class FrontendWebService(HTTP.HTTPProcessor):
    
    def __init__(self, configname):
        HTTP.HTTPProcessor.__init__(self,configname)

        self.stylesheet='original'
        self.add_handler(['POST'], '/login', self.post_login)
        self.add_handler(['GET'], '/patients(?:/(\d+)-(\d+)?)?', self.get_patients)
        self.add_handler(['GET'], '/patient_details', self.get_patient_details)
        self.add_handler(['GET'], '/total_spend', self.get_total_spend)
        self.add_handler(['GET'], '/spending', self.get_daily_spending)
        self.add_handler(['GET'], '/spending_details', self.get_spending_details)
        self.add_handler(['GET'], '/alerts(?:/(\d+)-(\d+)?)?', self.get_alerts)
#        self.add_handler(['GET'], '/alert_details', self.get_alert_details)
        self.add_handler(['GET'], '/orders(?:/(\d+)-(\d+)?)?', self.get_orders)
#        self.add_handler(['GET'], '/order_details', self.get_order_details)
        self.add_handler(['GET'], '/autocomplete', self.get_autocomplete)

    def schedule(self, loop):
        HTTP.HTTPProcessor.schedule(self, loop)


    @asyncio.coroutine
    def get_stub(self, _header, _body, _qs, _matches, _key):
        return (HTTP.OK_RESPONSE, b'', None)

    @asyncio.coroutine
    def get_autocomplete(self, _header, _body, qs, _matches, _key):
        global words
        term = qs['term'][0].casefold()
        try:
            rind = term.rindex(' ')+1
            prefix = term[:rind]
            term = term[rind:]
        except ValueError:
            prefix = ''
        l = len(term)
        first = 0
        last = len(words)-1
        while last - first > 1:
            mid=int((first+last)/2)
            print([mid,words[mid]])
            if words[mid].casefold()<term:
                first = mid
            else:
                last=mid
            
        print([first, words[first], last, words[last]])

        first +=1
        if not words[first].casefold().startswith(term):
            return (HTTP.OK_RESPONSE,b'',None)
        last=first+1
        while words[last].casefold().startswith(term) and last-first<100:
            print(words[last])
            last += 1
        print(words[last])
        
        return (HTTP.OK_RESPONSE, json.dumps([prefix+x for x in words[first:last]]), None)

    @asyncio.coroutine
    def post_login(self, _header, body, _qs, _matches, _key):
        info = json.loads(body.decode('utf-8'))
        if (not 'user' in info) or (not 'password' in info):
            return (HTTP.BAD_RESPONSE, b'', None)
        else:
            user = info['user']
            if True or not self.stylesheet == 'original':
                self.stylesheet = 'original'

            widgets = [
                ['#fixed-topA-1-1','topBanner','topBanner.html'],
                ['#fixed-topB-1-1','patientInfo'],
                ['#fixed-topB-1-1','patientSearch'],
                ['#rowA-1-1','patientList'],
                ['#rowB-1-1','encounterSummary'],
                ['#rowC-1-1','orderList'],
                ['#rowD-1-1','costdonut','costbreakdown.html'],
                ['#floating-right','alertList'],
            ]

            try:
                AK.check_authorization(user, info['password'], AUTH_LENGTH)
                return (HTTP.OK_RESPONSE, json.dumps({'display':'Dr. Huxtable', 
                                                      'stylesheet':self.stylesheet,
                                                      'widgets': widgets,
                                                  }), None)
            except:
                user_auth = AK.authorization_key(user,AUTH_LENGTH, LOGIN_TIMEOUT)
                return (HTTP.OK_RESPONSE,json.dumps({CONTEXT_KEY:user_auth, 
                                                     'display':'Dr. Huxtable',
                                                     'stylesheet':self.stylesheet,
                                                      'widgets': widgets,
                                                 }), None)

    patients_required_contexts = [CONTEXT_USER]
    patients_available_contexts = {CONTEXT_USER:str}

    @asyncio.coroutine
    def get_patients(self, _header, _body, qs, matches, _key):
        global patients_list

        context = restrict_context(qs, 
                                   FrontendWebService.patients_required_contexts,
                                   FrontendWebService.patients_available_contexts)
        user = context[CONTEXT_USER]
        (start, stop) = _get_range(matches, len(patients_list))

        patient_list = [copy_and_append(v, (CONTEXT_KEY,AK.authorization_key((user, v['id']),AUTH_LENGTH))) 
                        for v in patients_list.values()][start:stop]
        print(patient_list)
        return (HTTP.OK_RESPONSE, json.dumps(patient_list), None)

    patient_required_contexts = [CONTEXT_USER,CONTEXT_KEY,CONTEXT_PATIENTLIST]
    patient_available_contexts = {CONTEXT_USER:str,CONTEXT_KEY:str,CONTEXT_PATIENTLIST:str}

    @asyncio.coroutine
    def get_patient_details(self, _header, _body, qs, matches, _key):
        global patients_list
        context = restrict_context(qs, 
                                   FrontendWebService.patient_required_contexts,
                                   FrontendWebService.patient_available_contexts)
        user = context[CONTEXT_USER]
        patient_id = context[CONTEXT_PATIENTLIST]
        #auth_key = context[CONTEXT_KEY]
        #if not auth_key == _authorization_key((user, patient_id)):
        #    raise HTTP.IncompleteRequest('%s has not been authorized to view patient %d.' % (user, patient_id))
        patient_dict = dict(patients_list[patient_id])
        if patient_id in patient_extras:
            patient_dict.update(patient_extras[patient_id])
        patient_dict.update({'cost':-1, 'Allergies': ['NOT VALID'], 
                             'ProblemList':['NOTVALID', 'NOTVALID'], 'encounters':['1']},)
        return (HTTP.OK_RESPONSE, json.dumps(patient_dict), None)


    totals_required_contexts = [CONTEXT_USER,CONTEXT_KEY]
    totals_available_contexts = {CONTEXT_USER:str,CONTEXT_KEY:list}

    @asyncio.coroutine
    def get_total_spend(self, _header, _body, _qs, _matches, _key):
        ret = {'spending':85100, 'savings':1000}
        return (HTTP.OK_RESPONSE, json.dumps(ret), None)


    daily_required_contexts = [CONTEXT_USER]
    daily_available_contexts = {CONTEXT_USER:str,CONTEXT_KEY:list,CONTEXT_PATIENTLIST:list}

    @asyncio.coroutine
    def get_daily_spending(self, _header, _body, qs, _matches, _key):
        global patient_spending
        context = restrict_context(qs, 
                                   FrontendWebService.daily_required_contexts,
                                   FrontendWebService.daily_available_contexts)
        user = context[CONTEXT_USER]
        patient_ids = context.get(CONTEXT_PATIENTLIST,None)
        #if patient_ids:
        #    auth_keys = dict(zip(patient_ids,context[CONTEXT_KEY]))
            # validate keys here
        
        patient_dict = {}
        if not patient_ids:
            patient_ids = patient_spending.keys()
        for patient_id in patient_ids:
            try:
                for k,v in patient_spending[patient_id].items():
                    if not k in patient_dict:
                        patient_dict[k]=0
                    patient_dict[k] += sum(map(lambda x: x if type(x) is int else 0, v.values()))
            except TypeError:
                pass

        return (HTTP.OK_RESPONSE, json.dumps(patient_dict), None)

    spending_required_contexts = [CONTEXT_USER,CONTEXT_PATIENTLIST,CONTEXT_DATE]
    spending_available_contexts = {CONTEXT_USER:str,CONTEXT_PATIENTLIST:str,CONTEXT_DATE:int}

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
        global order_list
        context = restrict_context(qs, 
                                   FrontendWebService.orders_required_contexts,
                                   FrontendWebService.orders_available_contexts)
        user = context[CONTEXT_USER]
        patient_ids = context[CONTEXT_PATIENTLIST]
        #auth_keys = dict(zip(patient_ids,context[CONTEXT_KEY]))
        
        order_dict = {}
        for patient_id in set(patient_ids).intersection(order_list.keys()):
            try:
                #if _authorization_key((user, patient_id)) == auth_keys[patient_id]:
                order_dict[patient_id]=order_list[patient_id]
            except TypeError:
                pass
        print(order_dict)
        return (HTTP.OK_RESPONSE, json.dumps(order_dict['1']), None)


    #self.add_handler(['GET'], '/order_details', self.get_stub)
    def get_order_details(self, _header, _body, qs, _matches, _key):
        return (HTTP.OK_RESPONSE, b'', None)



if __name__ == '__main__':
    ML.DEBUG = ML.stdout_log
    MC.MavenConfig = {
        "httpserver":
            {
            SP.CONFIG_HOST: 'localhost',
            SP.CONFIG_PORT: 8087,
            },
        }
    
    hp = FrontendWebService('httpserver')
    event_loop = asyncio.get_event_loop()
    hp.schedule(event_loop)
    event_loop.run_forever()
