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
import utils.database.web_search as WS

import utils.database.web_persistence as WP

import maven_config as MC
from utils.streaming.http_svcs_wrapper import http_service, CONTEXT, CONFIG_PERSISTENCE, EMPTY_RETURN
from utils.enums import USER_ROLES
import utils.streaming.http_responder as HTTP
import json


class PathwaysWebservices():

    def __init__(self, configname, _rpc):
        config = MC.MavenConfig[configname]
        self.persistence = WP.WebPersistence(config[CONFIG_PERSISTENCE])
        self.search_interface = WS.web_search('search')

    @http_service(['GET'], '/list',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_list(self, _header, body, context, _matches, _key):

        customer_id = context[CONTEXT.CUSTOMERID]
        protocols = yield from self.persistence.get_protocols(customer_id)

        return (HTTP.OK_RESPONSE,
                json.dumps([{CONTEXT.PATHID: k[0],
                             CONTEXT.CANONICALID: k[2],
                             CONTEXT.FOLDER: k[3],
                             'name': k[1], 'canonical': k[2], 'folder': k[3]} for k in protocols]),
                None)

    @http_service(['GET'], '/history',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_hist(self, _header, body, context, _matches, _key):
        return HTTP.OK_RESPONSE, json.dumps(['Alzheimer\'s', 'Diabetes']), None

    """
        customer_id = context[CONTEXT.CUSTOMERID]
        protocols = yield from self.persistence.get_protocol_history(customer_id)

        return (HTTP.OK_RESPONSE,
                json.dumps([{CONTEXT.PATHID: k[0],
                             CONTEXT.CANONICALID: k[2],
                             CONTEXT.FOLDER: k[3],
                             'name': k[1], 'canonical': k[2], 'folder': k[3]} for k in protocols]),
                None)
    """
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

    @http_service(['GET'], '/tree/(\d+)',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_protocol(self, _header, body, context, matches, _key):
        protocol_id = int(matches[0])
        customer = context[CONTEXT.CUSTOMERID]
        if not protocol_id:
            return HTTP.NOTFOUND_RESPONSE, b'', None
        ret = yield from self.persistence.get_protocol(customer, protocol_id)
        return (HTTP.OK_RESPONSE, json.dumps(ret), None)

    @http_service(['POST'], '/tree',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID, CONTEXT.USERID],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int, CONTEXT.USERID: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def create_protocol(self, _header, body, context, _matches, _key):
        full_spec = json.loads(body.decode('utf-8'))
        customer_id = context[CONTEXT.CUSTOMERID]
        user_id = context[CONTEXT.USERID]
        folder = full_spec.get(CONTEXT.FOLDER, None)
        del full_spec[CONTEXT.FOLDER]
        id = yield from self.persistence.create_protocol(full_spec, customer_id, user_id, folder)
        full_spec[CONTEXT.PATHID] = id
        return (HTTP.OK_RESPONSE, json.dumps(full_spec), None)

    @http_service(['DELETE'], '/list/(\d+)',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def delete_protocol(self, _header, body, context, matches, _key):
        canonical_id = int(matches[0])
        customer_id = context[CONTEXT.CUSTOMERID]
        yield from self.persistence.delete_protocol(customer_id, canonical_id=canonical_id)
        return (HTTP.OK_RESPONSE, "", None)

    @http_service(['PUT'], '/tree/(\d+)',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID, CONTEXT.USERID],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int,
                   CONTEXT.USERID: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def update_protocol(self, _header, body, context, matches, _key):
        protocol_json = json.loads(body.decode('utf-8'))
        protocol_id = int(matches[0])
        customer = context[CONTEXT.CUSTOMERID]
        userid = context[CONTEXT.USERID]
        id = yield from self.persistence.update_protocol(protocol_id, customer, userid, protocol_json)
        protocol_json[CONTEXT.PATHID] = id
        return (HTTP.OK_RESPONSE, json.dumps(protocol_json), None)

    @http_service(['POST'], '/activity',
                  [CONTEXT.USERID, CONTEXT.CUSTOMERID],
                  {CONTEXT.USERID: int, CONTEXT.CUSTOMERID: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def post_activity(self, _header, body, context, _matches, _key):
        customer_id = context.get(CONTEXT.CUSTOMERID, None)
        user_id = context.get(CONTEXT.USERID, None)
        activity_msg = json.loads(body.decode('utf-8'))

        result = yield from self.persistence.post_protocol_activity(customer_id, user_id, activity_msg)

        if result:
            return HTTP.OK_RESPONSE, "", None
        else:
            return HTTP.BAD_RESPONSE, "", None

    @http_service(['POST'], '/update_pathway_location',
                  [CONTEXT.USERID, CONTEXT.CUSTOMERID, CONTEXT.CANONICALID],
                  {CONTEXT.USERID: int, CONTEXT.CUSTOMERID: int, CONTEXT.CANONICALID: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def post_pathway_location(self, _header, body, context, _matches, _key):
        customer_id = context[CONTEXT.CUSTOMERID]
        canonical_id = context[CONTEXT.CANONICALID]
        location_msg = json.loads(body.decode('utf-8'))

        result = yield from self.persistence.post_pathway_location(customer_id, canonical_id, location_msg)

        if result:
            return HTTP.OK_RESPONSE, "", None
        else:
            return HTTP.BAD_RESPONSE, "", None


def run():
    from utils.database.database import AsyncConnectionPool
    import utils.streaming.stream_processor as SP
    import utils.database.tree_persistence as TP
    import utils.streaming.webservices_core as WC
    import asyncio

    MC.MavenConfig = \
        {
            "httpserver":
                {
                    SP.CONFIG_HOST: 'localhost',
                    SP.CONFIG_PORT: 8087,
                    TP.CONFIG_PERSISTENCE: "persistence layer",
                },
            'persistence layer': {TP.CONFIG_DATABASE: 'webservices conn pool', },
            'persistance': {TP.CONFIG_DATABASE: 'webservices conn pool'},
            'search': {TP.CONFIG_DATABASE: 'webservices conn pool'},
            'webservices conn pool':
                {
                    AsyncConnectionPool.CONFIG_CONNECTION_STRING: MC.dbconnection,
                    AsyncConnectionPool.CONFIG_MIN_CONNECTIONS: 4,
                    AsyncConnectionPool.CONFIG_MAX_CONNECTIONS: 8
                }
        }
    core_scvs = WC.WebserviceCore('httpserver')
    core_scvs.register_services(PathwaysWebservices('httpserver'))
    event_loop = asyncio.get_event_loop()
    core_scvs.schedule(event_loop)
    event_loop.run_forever()

if __name__ == '__main__':
    run()
