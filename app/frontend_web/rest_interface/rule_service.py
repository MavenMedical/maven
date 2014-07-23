#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
__author__='Tom DuBois'
#************************
#DESCRIPTION:
# This file contains the core web services to support creation and editing of rules
#************************
#*************************************************************************

import json
import utils.database.web_search as WS
import utils.streaming.stream_processor as SP
import asyncio


import utils.streaming.http_responder as HTTP
import utils.streaming.http_helper as HH
import utils.crypto.authorization_key as AK

from utils.database.memory_cache import cache

import maven_logging as ML
import maven_config as MC
EMPTY_RETURN = [{'id':000000, 'term':"No Results Found", 'code':000000, 'type':'none'}]
JNAME = 'name'
JDX = 'pl_dx'
JTRIGGER = 'triggers'
SEARCH_PARAM = 'search_param'
CONTEXT_DISPLAY = 'display'
CONTEXT_AUTH = 'auth'
CONTEXT_USER = 'user'
CONTEXT_RULEID = 'id'
CONTEXT_RULENAME = 'name'
CONTEXT_PASSWORD = 'password'

AUTH_LENGTH = 44
LOGIN_TIMEOUT = 60 * 60  # 1 hour
static_id = 4
rules = {

}

triggers = [{'type': 'snomed', 'code': '456', 'id': 1}
            ,{'type': 'CPT', 'code': '789', 'id': 0}
            ,{'type': 'CPT', 'code': '0123', 'id': 2}]
details = [{'type': 'pl_dx', 'id': '1'},
           {'type': 'hist_dx', 'id': '2'},
           {'type': "lab", 'id': '3'},
           {'type': "enc_dx", 'id': '4'},
           {'type': "enc_pl_dx", 'id': '5'},
           {'type': "hist_proc", 'id': '6'},
           {'type': "ml_med", 'id': '7'},
           {'type': "vitals", 'id': '8'},
           {'type': "vitals_bp", 'id': '9'}]


@cache.cache_lookup(__name__)
def get_med_routes(key):
    raise KeyError(key)

class RuleService(HTTP.HTTPProcessor):
    
    def __init__(self, configname):
        HTTP.HTTPProcessor.__init__(self,configname)
        self.add_handler(['POST'], '/login', self.post_login)
        self.add_handler(['GET'], '/list', self.get_list)
        self.add_handler(['GET'], '/rule', self.get_rule)

        self.add_handler(['PUT'], '/rule', self.put_update)
        self.add_handler(['POST'], '/rule', self.post_add)
        self.add_handler(['DELETE'], '/rule', self.delete_rule)

        self.add_handler(['GET'], '/details', self.get_details)
        self.add_handler(['GET'], '/search', self.search)
        self.add_handler(['GET'], '/triggers', self.search)
        self.add_handler(['GET'], '/routes', self.get_routes)
        self.helper = HH.HTTPHelper([CONTEXT_USER], CONTEXT_AUTH, AUTH_LENGTH)
        self.search_interface = WS.web_search('search')
        self.update_med_routes()
        
    @cache.cache_update(__name__, period_seconds=60*60*24, message_fn=lambda: ML.EXCEPTION("Failed to get med routes"))
    def update_med_routes(self):
        route_list = yield from self.search_interface.get_routes();
        print("XXXXXXXXX")
        return {'routes': route_list}

    @asyncio.coroutine
    def post_login(self, _header, body, _qs, _matches, _key):
        info = json.loads(body.decode('utf-8'))
        if (not CONTEXT_USER in info) or (not CONTEXT_PASSWORD in info):
            return (HTTP.BAD_RESPONSE, b'', None)
        else:
            user = info[CONTEXT_USER]
            user_auth = AK.authorization_key([user], AUTH_LENGTH, LOGIN_TIMEOUT)

        ret = {
            CONTEXT_DISPLAY: 'Dr. Huxtable',
            CONTEXT_AUTH: user_auth,
            CONTEXT_USER: user,
            }
        return (HTTP.OK_RESPONSE, json.dumps(ret), None)

    update_required_contexts = [CONTEXT_USER, CONTEXT_RULEID]
    update_available_contexts = {CONTEXT_USER:str, CONTEXT_RULEID: int}

    @asyncio.coroutine
    def put_update(self, _header, body, qs, _matches, _key):
        info = json.loads(body.decode('utf-8'))
        context = self.helper.restrict_context(qs,
                                               RuleService.update_required_contexts,
                                               RuleService.update_available_contexts)

        yield from self.search_interface.update_db(info);

        return (HTTP.OK_RESPONSE, json.dumps(info), None)



    add_required_contexts = [CONTEXT_USER]
    add_available_contexts = {CONTEXT_USER:str}

    @asyncio.coroutine
    def post_add(self, _header, body, qs, _matches, _key):
        info = json.loads(body.decode('utf-8'))
        context = self.helper.restrict_context(qs,
                                               RuleService.add_required_contexts,
                                               RuleService.add_available_contexts)


        n = yield from self.search_interface.add_to_db(info)
        info[CONTEXT_RULEID]=n
        return (HTTP.OK_RESPONSE, json.dumps(info), None)


    delete_required_context = [CONTEXT_USER, CONTEXT_RULEID]
    delete_available_context = {CONTEXT_USER:str, CONTEXT_RULEID:int}

    @asyncio.coroutine
    def delete_rule(self, _header, body, qs, _matches, _key):
        print(rules)
        context = self.helper.restrict_context(qs,
                                               RuleService.delete_required_context,
                                               RuleService.delete_available_context)

        ruleid = context[CONTEXT_RULEID]
        yield from self.search_interface.delete_rule(ruleid)
        return (HTTP.OK_RESPONSE, json.dumps(""), None)



    list_required_context = [CONTEXT_USER]
    list_available_context = {CONTEXT_USER:str, CONTEXT_RULEID:int}

    @asyncio.coroutine
    def get_list(self, _header, body, qs, _matches, _key):
        context = self.helper.restrict_context(qs,
                                               RuleService.list_required_context,
                                               RuleService.list_available_context)

        database_rules = yield from self.search_interface.fetch_rules()
        global rules

        return (HTTP.OK_RESPONSE, json.dumps([{CONTEXT_RULEID:k[0], JNAME:k[1]} for k in database_rules]), None)

    triggers_required_context = [CONTEXT_USER]
    triggers_available_context = {CONTEXT_USER:str, CONTEXT_RULEID:int, SEARCH_PARAM:str, 'search_type': str}

    @asyncio.coroutine
    def get_triggers(self, _header, body, qs, _matches, _key):
        context = self.helper.restrict_context(qs,
                                               RuleService.triggers_required_context,
                                               RuleService.triggers_available_context)
        global triggers
        print("searching22")
        results = yield from self.search_interface.do_search(context[SEARCH_PARAM], 'DX')

        return (HTTP.OK_RESPONSE, json.dumps(results), None)

    search_required_context = [CONTEXT_USER, SEARCH_PARAM, 'type']
    search_available_context = {CONTEXT_USER:str, CONTEXT_RULEID:int, SEARCH_PARAM:str, 'type': str}

    @asyncio.coroutine
    def search(self, _header, body, qs, _matches, _key):
        hasSearch = qs.get(SEARCH_PARAM, None)
        if (not hasSearch):
         return (HTTP.OK_RESPONSE, json.dumps(EMPTY_RETURN), None);
        context = self.helper.restrict_context(qs,
                                               RuleService.search_required_context,
                                               RuleService.search_available_context)
        print(context)
        results = yield from self.search_interface.do_search(context[SEARCH_PARAM], context['type'])

        return (HTTP.OK_RESPONSE, json.dumps(results), None)


    details_required_context = [CONTEXT_USER]
    details_available_context = {CONTEXT_USER:str, CONTEXT_RULEID:int, SEARCH_PARAM:str}

    @asyncio.coroutine
    def get_details(self, _header, body, qs, _matches, _key):
        context = self.helper.restrict_context(qs,
                                               RuleService.details_required_context,
                                               RuleService.details_available_context)


        return (HTTP.OK_RESPONSE, json.dumps(details), None)

    routes_required_context = [CONTEXT_USER]
    routes_available_context = {CONTEXT_USER:str, CONTEXT_RULEID:int, SEARCH_PARAM:str}

    @asyncio.coroutine
    def get_routes(self, _header, body, qs, _matches, _key):
        context = self.helper.restrict_context(qs,
                                               RuleService.routes_required_context,
                                               RuleService.routes_available_context)

        result = yield from get_med_routes('routes')
        return (HTTP.OK_RESPONSE, json.dumps(result), None)

    rule_required_context = [CONTEXT_USER, CONTEXT_RULEID]
    rule_available_context = {CONTEXT_USER:str, CONTEXT_RULEID:int}


    @asyncio.coroutine
    def get_rule(self, _header, body, qs, _matches, _key):
        print(rules)
        context = self.helper.restrict_context(qs,
                                               RuleService.rule_required_context,
                                               RuleService.rule_available_context)

        ruleid = context[CONTEXT_RULEID]
        rule = yield from self.search_interface.fetch_rule(ruleid)
        ret = json.loads(rule[0])
        ret[CONTEXT_RULEID] = ruleid
        return (HTTP.OK_RESPONSE, json.dumps(ret), None)



if __name__ == '__main__':
    print("python execution")
    from utils.database.database import AsyncConnectionPool
    print("python execution")
    MC.MavenConfig = {
            "httpserver":
                {
                    SP.CONFIG_HOST: 'localhost',
                    SP.CONFIG_PORT: 8092,

                },
            'search': {WS.CONFIG_DATABASE: 'webservices conn pool'},
            'webservices conn pool': {
                AsyncConnectionPool.CONFIG_CONNECTION_STRING: MC.dbconnection,
                AsyncConnectionPool.CONFIG_MIN_CONNECTIONS: 4,
                AsyncConnectionPool.CONFIG_MAX_CONNECTIONS: 8
            }
        }
    hp = RuleService('httpserver')
    event_loop = asyncio.get_event_loop()
    hp.schedule(event_loop)
    event_loop.run_forever()



