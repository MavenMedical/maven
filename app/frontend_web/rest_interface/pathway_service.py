# *************************************************************************
# Copyright (c) 2014 - Maven Medical
#
# ************************
# AUTHOR:
__author__ = 'Tom DuBois'
# ************************
# DESCRIPTION:
#  This file contains the core web services to support creation and editing of rules
# ************************

import json
import utils.database.tree_persistence as TP
import utils.database.web_search as WS
import utils.streaming.stream_processor as SP
import asyncio

import utils.streaming.http_responder as HTTP
import utils.streaming.http_helper as HH
import utils.crypto.authorization_key as AK

from utils.database.memory_cache import cache

import maven_logging as ML
import maven_config as MC


EMPTY_RETURN = [{'id': 000000, 'term': "No Results Found", 'code': 000000, 'type': 'none'}]
JNAME = 'name'
JDX = 'pl_dx'
JTRIGGER = 'triggers'
SEARCH_PARAM = 'search_param'
CONTEXT_DISPLAY = 'display'
CONTEXT_AUTH = 'auth'
CONTEXT_USER = 'user'
CONTEXT_PATHID = 'id'
CONTEXT_PATHNAME = 'name'
CONTEXT_PASSWORD = 'password'
AUTH_LENGTH = 44
LOGIN_TIMEOUT = 60 * 60 * 48  # 1 hour
static_id = 4
rules = {

}


@cache.cache_lookup(__name__)
def get_med_routes(key):
    raise KeyError(key)


class pathway_service(HTTP.HTTPProcessor):
    def __init__(self, configname):
        HTTP.HTTPProcessor.__init__(self, configname)
        self.add_handler(['PUT'], '/tree', self.put_update)
        self.add_handler(['POST'], '/tree', self.post_create)
        self.add_handler(['GET'], '/tree', self.get_tree)
        self.add_handler(['GET'], '/search', self.search)
        self.add_handler(['GET'], '/list', self.get_list)
        self.add_handler(['POST'], '/login/0', self.post_login)
        self.add_handler(['DELETE'], '/tree', self.delete_pathway)
        self.helper = HH.HTTPHelper([CONTEXT_USER], CONTEXT_AUTH, AUTH_LENGTH)
        self.save_interface = TP.tree_persistence('persistance')
        self.search_interface = WS.web_search('search')

    @asyncio.coroutine
    def post_login(self, _header, body, _qs, _matches, _key):
        info = json.loads(body.decode('utf-8'))
        if (CONTEXT_USER not in info) or (CONTEXT_PASSWORD not in info):
            return (HTTP.BAD_RESPONSE, b'', None)
        else:
            user = info[CONTEXT_USER]
            user_auth = AK.authorization_key([user], AUTH_LENGTH, LOGIN_TIMEOUT)

        ret = {
            CONTEXT_DISPLAY: 'Dr. Huxtable',
            CONTEXT_AUTH: user_auth,
            CONTEXT_USER: user,
            'widgets': [
                ['#rowA-1-1', 'TreeView', 'treeTemplate.html'],
                ['#fixed-topA-1-1', 'topBanner', 'treeTemplate.html'],
                ['#fixed-topB-1-1', 'pathwaySearch', 'treeTemplate.html'],
                ['#floating-right', 'actionList', 'treeTemplate.html'],
                ['#floating-left', 'pathwaysList', 'pathwaysList.html']

            ]
        }
        return (HTTP.OK_RESPONSE, json.dumps(ret), None)

    list_required_context = [CONTEXT_USER]
    list_available_context = {CONTEXT_USER: str, CONTEXT_PATHID: int}

    @asyncio.coroutine
    def get_list(self, _header, body, qs, _matches, _key):
        context = self.helper.restrict_context(qs,
                                               pathway_service.list_required_context,
                                               pathway_service.list_available_context)

        database_pathways = yield from self.save_interface.fetch_pathways()

        return (HTTP.OK_RESPONSE, json.dumps([{CONTEXT_PATHID: k[0], JNAME: k[1]} for k in database_pathways]), None)

    search_required_context = [CONTEXT_USER, SEARCH_PARAM, 'type']
    search_available_context = {CONTEXT_USER: str, CONTEXT_PATHID: int, SEARCH_PARAM: str, 'type': str}

    @asyncio.coroutine
    def search(self, _header, body, qs, _matches, _key):
        hasSearch = qs.get(SEARCH_PARAM, None)
        if (not hasSearch):
            return HTTP.OK_RESPONSE, json.dumps(EMPTY_RETURN), None
        context = self.helper.restrict_context(qs,
                                               pathway_service.search_required_context,
                                               pathway_service.search_available_context)
        print(context)
        results = yield from self.search_interface.do_search(context[SEARCH_PARAM], context['type'])

        return HTTP.OK_RESPONSE, json.dumps(results), None

    @asyncio.coroutine
    def get_tree(self, _header, body, qs, _matches, _key):
        print(qs['id'][0])
        ret = yield from self.save_interface.get_tree(qs['id'][0])
        ret = json.loads(ret)
        ret['id'] = qs['id'][0]

        return (HTTP.OK_RESPONSE, json.dumps(ret), None)

    @asyncio.coroutine
    def put_update(self, _header, body, qs, _matches, _key):
        info = json.loads(body.decode('utf-8'))
        yield from self.save_interface.update_tree(info)

        return (HTTP.OK_RESPONSE, json.dumps(info), None)

    delete_required_context = [CONTEXT_USER, CONTEXT_PATHID]
    delete_available_context = {CONTEXT_USER: str, CONTEXT_PATHID: int}

    @asyncio.coroutine
    def delete_pathway(self, _header, body, qs, _matches, _key):
        context = self.helper.restrict_context(qs,
                                               pathway_service.delete_required_context,
                                               pathway_service.delete_available_context)

        yield from self.save_interface.delete_pathway(context[CONTEXT_PATHID])
        return (HTTP.OK_RESPONSE, "", None)

    @asyncio.coroutine
    def post_create(self, _header, body, qs, _matches, _key):
        info = json.loads(body.decode('utf-8'))
        resultid = yield from self.save_interface.create_tree(info)
        info['id'] = resultid
        return (HTTP.OK_RESPONSE, json.dumps(info), None)


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
        'persistance': {TP.CONFIG_DATABASE: 'webservices conn pool'},
        'search': {TP.CONFIG_DATABASE: 'webservices conn pool'},
        'webservices conn pool': {
            AsyncConnectionPool.CONFIG_CONNECTION_STRING: MC.dbconnection,
            AsyncConnectionPool.CONFIG_MIN_CONNECTIONS: 4,
            AsyncConnectionPool.CONFIG_MAX_CONNECTIONS: 8}
    }
    hp = pathway_service('httpserver')
    event_loop = asyncio.get_event_loop()
    hp.schedule(event_loop)
    event_loop.run_forever()
