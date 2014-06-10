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

import utils.streaming.stream_processor as SP
import asyncio

import utils.streaming.http_responder as HTTP
import utils.streaming.http_helper as HH
import utils.crypto.authorization_key as AK

import maven_logging as ML
import maven_config as MC

JNAME = 'name'
JDX = 'dx'
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
static_id = 3
rules = {

    1: {
        JNAME: 'rule 1',
        JDX: [{'code':'123', 'negative': 'false'}, {'code':'412', 'negative': 'true'}],
        JTRIGGER: [
            {'type': 'CPT', 'code':'456', 'id':1},
            {'type': 'snomed', 'code':'789', 'id':0},
            ]
        },

    }
triggers = [{'type': 'snomed', 'code': '456', 'id': 1}
            ,{'type': 'CPT', 'code': '789', 'id': 0}
            ,{'type': 'CPT', 'code': '0123', 'id': 2}]


class RuleService(HTTP.HTTPProcessor):
    
    def __init__(self, configname):
        HTTP.HTTPProcessor.__init__(self,configname)

        self.add_handler(['POST'], '/login', self.post_login)
        self.add_handler(['GET'], '/list', self.get_list)
        self.add_handler(['GET'], '/rule', self.get_rule)

        self.add_handler(['PUT'], '/rule', self.put_update)
        self.add_handler(['POST'], '/rule', self.post_add)
        self.add_handler(['DELETE'], '/rule', self.delete_rule)


        self.add_handler(['GET'], '/trigger', self.get_triggers);
        self.helper = HH.HTTPHelper(CONTEXT_USER, CONTEXT_AUTH, AUTH_LENGTH)
                
    @asyncio.coroutine
    def post_login(self, _header, body, _qs, _matches, _key):
        info = json.loads(body.decode('utf-8'))
        if (not CONTEXT_USER in info) or (not CONTEXT_PASSWORD in info):
            return (HTTP.BAD_RESPONSE, b'', None)
        else:
            user = info[CONTEXT_USER]
            user_auth = AK.authorization_key(user, AUTH_LENGTH, LOGIN_TIMEOUT)

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
        global rules
        ruleid = context.get(CONTEXT_RULEID, 1+len(rules))
        rules[ruleid] = info
        info[CONTEXT_RULEID]=ruleid
        return (HTTP.OK_RESPONSE, json.dumps(info), None)



    add_required_contexts = [CONTEXT_USER]
    add_available_contexts = {CONTEXT_USER:str}

    @asyncio.coroutine
    def post_add(self, _header, body, qs, _matches, _key):
        info = json.loads(body.decode('utf-8'))
        context = self.helper.restrict_context(qs,
                                               RuleService.add_required_contexts,
                                               RuleService.add_available_contexts)
        global rules
        global static_id
        ruleid = static_id
        static_id = static_id + 1;
        rules[ruleid] = info
        info[CONTEXT_RULEID]=ruleid
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
        rules.pop(ruleid);
        return (HTTP.OK_RESPONSE, json.dumps(""), None)



    list_required_context = [CONTEXT_USER]
    list_available_context = {CONTEXT_USER:str, CONTEXT_RULEID:int}

    @asyncio.coroutine
    def get_list(self, _header, body, qs, _matches, _key):
        context = self.helper.restrict_context(qs,
                                               RuleService.list_required_context,
                                               RuleService.list_available_context)
        global rules
        
        return (HTTP.OK_RESPONSE, json.dumps([{CONTEXT_RULEID:k, JNAME:rules[k][JNAME]} for k in rules.keys()]), None)

    triggers_required_context = [CONTEXT_USER]
    triggers_available_context = {CONTEXT_USER:str, CONTEXT_RULEID:int, SEARCH_PARAM:str}

    @asyncio.coroutine
    def get_triggers(self, _header, body, qs, _matches, _key):
        context = self.helper.restrict_context(qs,
                                               RuleService.triggers_required_context,
                                               RuleService.triggers_available_context)
        global triggers

        return (HTTP.OK_RESPONSE, json.dumps(triggers), None)

    rule_required_context = [CONTEXT_USER, CONTEXT_RULEID]
    rule_available_context = {CONTEXT_USER:str, CONTEXT_RULEID:int}


    @asyncio.coroutine
    def get_rule(self, _header, body, qs, _matches, _key):
        print(rules)
        context = self.helper.restrict_context(qs,
                                               RuleService.rule_required_context,
                                               RuleService.rule_available_context)

        ruleid = context[CONTEXT_RULEID]
        ret = dict(rules[ruleid])
        ret[CONTEXT_RULEID]=ruleid
        return (HTTP.OK_RESPONSE, json.dumps(ret), None)



if __name__ == '__main__':
    ML.DEBUG = ML.stdout_log
    MC.MavenConfig = {
        "httpserver":
            {
            SP.CONFIG_HOST: 'localhost',
            SP.CONFIG_PORT: 8092,
            },
        }
    
    hp = RuleService('httpserver')
    event_loop = asyncio.get_event_loop()
    hp.schedule(event_loop)
    event_loop.run_forever()



