# *************************************************************************
# Copyright (c) 2014 - Maven Medical
#
# ************************
# AUTHOR:
__author__ = 'Yuki Uchino'
# ************************
# DESCRIPTION:   This file provides the webservice calls required for Maven Pathways functionality
#
# ************************
# ASSUMES:
# ************************
# SIDE EFFECTS:
# ************************
# LAST MODIFIED FOR JIRA ISSUE: MAV-303
# *************************************************************************
from utils.streaming.webservices_core import *


class PathwaysWebservices():

    @http_service(['GET'], '/list',
                  [],
                  {},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_list(self, _header, body, qs, _matches, _key):

        database_pathways = yield from self.save_interface.fetch_pathways()

        return (HTTP.OK_RESPONSE, json.dumps([{CONTEXT.PATHID: k[0], 'name': k[1]} for k in database_pathways]), None)

    @http_service(['GET'], '/search',
                  [CONTEXT.SEARCH_PARAM],
                  {'type': str, CONTEXT.SEARCH_PARAM: str},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def search(self, _header, body, context, _matches, _key):
        hasSearch = context.get(CONTEXT.SEARCH_PARAM, None)
        if (not hasSearch):
            return HTTP.OK_RESPONSE, json.dumps(EMPTY_RETURN), None
        results = yield from self.search_interface.do_search(context[CONTEXT.SEARCH_PARAM], context['type'])

        return HTTP.OK_RESPONSE, json.dumps(results), None

    @http_service(['GET'], '/tree',
                  [CONTEXT.PATHID],
                  {CONTEXT.PATHID: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_tree(self, _header, body, context, _matches, _key):
        ret = yield from self.save_interface.get_tree(context[CONTEXT.PATHID])
        ret = json.loads(ret)
        ret['id'] = context[CONTEXT.PATHID]

        return (HTTP.OK_RESPONSE, json.dumps(ret), None)

    @http_service(['PUT'], '/tree',
                  [],
                  {},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def put_update(self, _header, body, context, _matches, _key):
        info = json.loads(body.decode('utf-8'))
        yield from self.save_interface.update_tree(info)
        return (HTTP.OK_RESPONSE, json.dumps(info), None)

    @http_service(['DELETE'], '/tree',
                  [CONTEXT.PATHID],
                  {CONTEXT.PATHID: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def delete_pathway(self, _header, body, context, _matches, _key):
        yield from self.save_interface.delete_pathway(context[CONTEXT.PATHID])
        return (HTTP.OK_RESPONSE, "", None)

    @http_service(['POST'], '/tree',
                  [],
                  {},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def post_create(self, _header, body, qs, _matches, _key):
        info = json.loads(body.decode('utf-8'))
        resultid = yield from self.save_interface.create_tree(info)
        info['id'] = resultid
        return (HTTP.OK_RESPONSE, json.dumps(info), None)


def run():
    from utils.database.database import AsyncConnectionPool

    MC.MavenConfig = \
        {
            "httpserver":
                {
                    SP.CONFIG_HOST: 'localhost',
                    SP.CONFIG_PORT: 8087,
                    CONFIG_PERSISTENCE: "persistence layer",
                },
            'persistence layer': {WP.CONFIG_DATABASE: 'webservices conn pool', },
            'persistance': {TP.CONFIG_DATABASE: 'webservices conn pool'},
            'search': {TP.CONFIG_DATABASE: 'webservices conn pool'},
            'webservices conn pool':
                {
                    AsyncConnectionPool.CONFIG_CONNECTION_STRING: MC.dbconnection,
                    AsyncConnectionPool.CONFIG_MIN_CONNECTIONS: 4,
                    AsyncConnectionPool.CONFIG_MAX_CONNECTIONS: 8
                }
        }
    core_scvs = WebserviceCore('httpserver')
    core_scvs.register_services([PathwaysWebservices])
    event_loop = asyncio.get_event_loop()
    core_scvs.schedule(event_loop)
    event_loop.run_forever()

if __name__ == '__main__':
    run()
