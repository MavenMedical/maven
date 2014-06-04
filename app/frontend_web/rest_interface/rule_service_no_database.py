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
JTRIGGER = 'cpt'

CONTEXT_DISPLAY = 'display'
CONTEXT_AUTH = 'auth'
CONTEXT_USER = 'user'
CONTEXT_RULEID = 'id'
CONTEXT_PASSWORD = 'password'

AUTH_LENGTH = 44
LOGIN_TIMEOUT = 60 * 60  # 1 hour

rules = {
    1: {
        JNAME: 'rule 1',
        JDX: [{JDX:'123'}],
        JTRIGGER: [
            {JTRIGGER:'456'},
            {JTRIGGER:'789'},
            ]
        },
    2: {
        JNAME: 'rule 2',
        JDX: [{JDX:'abc'}],
        JTRIGGER: [
            {JTRIGGER:'def'},
            {JTRIGGER:'ghi'},
            ]
        },
    } 

class RuleService(HTTP.HTTPProcessor):
    
    def __init__(self, configname):
        HTTP.HTTPProcessor.__init__(self,configname)

        self.add_handler(['POST'], '/login', self.post_login)
        self.add_handler(['GET'], '/list', self.get_list)
        self.add_handler(['GET'], '/rule', self.get_rule)
        self.add_handler(['POST', 'PUT'], '/rule', self.post_update)
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

    update_required_contexts = [CONTEXT_USER]
    update_available_contexts = {CONTEXT_USER:str, CONTEXT_RULEID: int}

    @asyncio.coroutine
    def post_update(self, _header, body, qs, _matches, _key):
        info = json.loads(body.decode('utf-8'))
        context = self.helper.restrict_context(qs,
                                               RuleService.update_required_contexts,
                                               RuleService.update_available_contexts)
        global rules
        ruleid = context.get(CONTEXT_RULEID, 1+len(rules))
        rules[ruleid] = info
        info[CONTEXT_RULEID]=ruleid
        return (HTTP.OK_RESPONSE, json.dumps(info), None)

    list_required_context = [CONTEXT_USER]
    list_available_context = {CONTEXT_USER:str}
    
    @asyncio.coroutine
    def get_list(self, _header, body, qs, _matches, _key):
        context = self.helper.restrict_context(qs,
                                               RuleService.list_required_context,
                                               RuleService.list_available_context)
        global rules
        
        return (HTTP.OK_RESPONSE, json.dumps([{CONTEXT_RULEID:k, JNAME:rules[k][JNAME]} for k in rules.keys()]), None)

    rule_required_context = [CONTEXT_USER, CONTEXT_RULEID]
    rule_available_context = {CONTEXT_USER:str, CONTEXT_RULEID:int}

    @asyncio.coroutine
    def get_rule(self, _header, body, qs, _matches, _key):
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



