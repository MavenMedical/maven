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
from clientApp.webservice.clientapp_rpc_endpoint import ClientAppEndpoint


class PathwaysWebservices():

    def __init__(self, configname, rpc):
        config = MC.MavenConfig[configname]
        self.persistence = WP.WebPersistence(config[CONFIG_PERSISTENCE])
        self.search_interface = WS.web_search('search')
        self.client_interface = rpc.create_client(ClientAppEndpoint)

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
                             'name': k[1], 'canonical': k[2], 'folder': k[3], 'enabled': k[4]} for k in protocols]),
                None)

    @http_service(['GET'], '/history(?:(\d+)-(\d+)?)?',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int, CONTEXT.CANONICALID: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_hist(self, _header, body, context, _matches, _key):

        customer_id = context[CONTEXT.CUSTOMERID]
        canonical_id = context.get(CONTEXT.CANONICALID, None)
        limit = self.helper.limit_clause(_matches)

        protocols = yield from self.persistence.get_protocol_history(customer_id, canonical_id, limit=limit)

        return (HTTP.OK_RESPONSE,
                json.dumps([{CONTEXT.PATHID: k[0],
                             CONTEXT.CANONICALID: k[1],
                             'creation_date': k[2].strftime("%Y-%m-%d %H:%M:%S"),
                             CONTEXT.OFFICIALNAME: k[3],
                             CONTEXT.ACTIVE: k[4]} for k in protocols]),
                None)

    @http_service(['POST'], '/history/(\d+)/(\d+)',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def select_hist(self, _header, body, context, matches, _key):
        # choose which pathway in history is currently active

        canonical_id = int(matches[0])
        path_id = int(matches[1])
        customer_id = context[CONTEXT.CUSTOMERID]

        yield from self.persistence.select_active_pathway(customer_id, canonical_id, path_id)

        return (HTTP.OK_RESPONSE, "", None)

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
        ret.pop('id', None)
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
        if folder:
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

        try:
            id = yield from self.persistence.update_protocol(protocol_id, customer, userid, protocol_json)
            if id:
                protocol_json[CONTEXT.PATHID] = id
                protocol_json.pop('id', None)
                return HTTP.OK_RESPONSE, json.dumps(protocol_json), None
            else:
                return HTTP.BAD_RESPONSE, json.dumps('FALSE'), None
        except Exception:
            return HTTP.BAD_RESPONSE, json.dumps('FALSE'), None

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

    @http_service(['PUT'], '/list/(\d+)',
                  [CONTEXT.USERID, CONTEXT.CUSTOMERID],
                  {CONTEXT.USERID: int, CONTEXT.CUSTOMERID: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def toggle_path(self, _header, body, context, matches, _key):
        # enable or disable a pathway

        customer_id = context[CONTEXT.CUSTOMERID]
        canonical_id = int(matches[0])
        msg = json.loads(body.decode('utf-8'))
        active = msg.get("active")

        pathway = yield from self.persistence.toggle_pathway(customer_id, canonical_id, enabled=active)

        if active and pathway:
            children = yield from self.persistence.get_protocol_children(canonical_id)
            for child in children:
                subject = "Changes for your shared pathway '{}'"
                message = ("The master version for your pathway {} has a new live version \n"
                           "Master version: #/pathway/{} \n "
                           "Your Version: #/pathway/{} \n"
                           .format(child['name'], child['name'], pathway['current_id'], child['current_id']))
                yield from self.client_interface.notify_user(customer_id, child['creator'], subject, message)

        return (HTTP.OK_RESPONSE, "", None)

    @http_service(['POST'], '/update_pathway_location',
                  [CONTEXT.USERID, CONTEXT.CUSTOMERID, CONTEXT.CANONICALID],
                  {CONTEXT.USERID: int, CONTEXT.CUSTOMERID: int, CONTEXT.CANONICALID: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def post_pathway_location(self, _header, body, context, _matches, _key):
        customer_id = context[CONTEXT.CUSTOMERID]
        canonical_id = context[CONTEXT.CANONICALID]
        location_msg = json.loads(body.decode('utf-8'))

        yield from self.persistence.post_pathway_location(customer_id, canonical_id, location_msg)

        return (HTTP.OK_RESPONSE, "", None)

    @http_service(['GET'], '/pathway_version',
                  [CONTEXT.USERID, CONTEXT.CUSTOMERID, CONTEXT.PATHID],
                  {CONTEXT.USERID: int, CONTEXT.CUSTOMERID: int, CONTEXT.PATHID: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def copy_protocol(self, _header, body, context, matches, _key):
        customer = context[CONTEXT.CUSTOMERID]
        user_id = context[CONTEXT.USERID]
        protocol = context[CONTEXT.PATHID]

        ret = yield from self.persistence.copy_protocol(customer, user_id, protocol)
        treeJson = json.dumps(ret['full_spec'])

        return HTTP.OK_RESPONSE, json.dumps({'full_spec': treeJson, 'folder': ret['folder']}), None


def run():
    from utils.database.database import AsyncConnectionPool
    import utils.streaming.stream_processor as SP
    import utils.streaming.webservices_core as WC
    import asyncio

    MC.MavenConfig = \
        {
            "httpserver":
                {
                    SP.CONFIG_HOST: 'localhost',
                    SP.CONFIG_PORT: 8087,
                    WP.CONFIG_PERSISTENCE: "persistence layer",
                },
            'persistence layer': {WP.CONFIG_DATABASE: 'webservices conn pool', },
            'persistance': {WP.CONFIG_DATABASE: 'webservices conn pool'},
            'search': {WP.CONFIG_DATABASE: 'webservices conn pool'},
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
