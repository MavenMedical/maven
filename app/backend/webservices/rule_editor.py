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
from utils.streaming.http_svcs_wrapper import CONTEXT, http_service, EMPTY_RETURN
from utils.enums import USER_ROLES
import utils.streaming.http_responder as HTTP


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
LOGIN_TIMEOUT = 60 * 60 * 48 # 1 hour
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


class RuleEditorWebservices(HTTP.HTTPProcessor):

    def __init__(self, configname, _rpc):
        # config = MC.MavenConfig[configname]
        self.search_interface = WS.web_search('search')
        self.update_med_routes()


    @cache.cache_update(__name__, period_seconds=60*60*24, message_fn=lambda: ML.EXCEPTION("Failed to get med routes"))
    def update_med_routes(self):
        route_list = yield from self.search_interface.get_routes();
        return {'routes': route_list}


    @http_service(['PUT'], '/rule',
                  [],
                  {CONTEXT_USER: str, SEARCH_PARAM: str},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def put_update(self, _header, body, context, _matches, _key):
        info = json.loads(body.decode('utf-8'))
        info['conflicts'] = yield from self.search_interface.update_db(info);
        return (HTTP.OK_RESPONSE, json.dumps(info), None)




    @http_service(['POST'], '/rule',
                  [],
                  {CONTEXT_USER: str, SEARCH_PARAM: str},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def post_add(self, _header, body, qs, _matches, _key):
        info = json.loads(body.decode('utf-8'))
        info[CONTEXT_RULEID] = yield from self.search_interface.add_to_db(info)
        return (HTTP.OK_RESPONSE, json.dumps(info), None)


    delete_required_context = [CONTEXT_USER, CONTEXT_RULEID]
    delete_available_context = {CONTEXT_USER:str, CONTEXT_RULEID:int}

    @http_service(['DELETE'], '/rule',
                  [CONTEXT_RULEID],
                  {CONTEXT_RULEID: int, CONTEXT_USER: str, SEARCH_PARAM: str},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def delete_rule(self, _header, body, context, _matches, _key):
        print(rules)
        ruleid = context[CONTEXT_RULEID]
        yield from self.search_interface.delete_rule(ruleid)
        return (HTTP.OK_RESPONSE, json.dumps(""), None)

    @http_service(['GET'], '/rulelist',
                  [],
                  {CONTEXT_USER: str, SEARCH_PARAM: str},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_list(self, _header, body, context, _matches, _key):
        database_rules = yield from self.search_interface.fetch_rules()
        return (HTTP.OK_RESPONSE, json.dumps([{CONTEXT_RULEID:k[0], JNAME:k[1]} for k in database_rules]), None)

    triggers_required_context = [CONTEXT_USER]
    triggers_available_context = {CONTEXT_USER:str, CONTEXT_RULEID:int, SEARCH_PARAM:str, 'search_type': str}

    @http_service(['GET'], '/triggers',
                  [SEARCH_PARAM],
                  {SEARCH_PARAM: str, CONTEXT_USER: str},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_triggers(self, _header, body, context, _matches, _key):
        results = yield from self.search_interface.do_search(context[SEARCH_PARAM], 'DX')
        return (HTTP.OK_RESPONSE, json.dumps(results), None)

    search_required_context = [CONTEXT_USER, SEARCH_PARAM, ]
    search_available_context = {CONTEXT_USER:str, CONTEXT_RULEID:int, SEARCH_PARAM:str, 'type': str}

    @http_service(['GET'], '/search',
                  [SEARCH_PARAM, 'type'],
                  {SEARCH_PARAM:str, 'type':str, CONTEXT_USER: str},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def search(self, _header, body, context, _matches, _key):
        results = yield from self.search_interface.do_search(context[SEARCH_PARAM], context['type'])
        return (HTTP.OK_RESPONSE, json.dumps(results), None)




    @http_service(['GET'], '/details',
                  [],
                  {CONTEXT_USER: str, SEARCH_PARAM: str},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_details(self, _header, body, qs, _matches, _key):
        return (HTTP.OK_RESPONSE, json.dumps(details), None)


    @http_service(['GET'], '/routes',
                  [],
                  {CONTEXT_USER: str, SEARCH_PARAM: str},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_routes(self, _header, body, qs, _matches, _key):
        result = yield from get_med_routes('routes')
        return (HTTP.OK_RESPONSE, json.dumps(result), None)



    @http_service(['GET'], '/rule',
                  [CONTEXT_RULEID],
                  {CONTEXT_RULEID:int, CONTEXT_USER: str, SEARCH_PARAM: str},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_rule(self, _header, body, context, _matches, _key):
        print(rules)
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



