# *************************************************************************
# Copyright (c) 2014 - Maven Medical
#
# ************************
# AUTHOR:
__author__ = 'Carlos Brenneisen'
# ************************
# DESCRIPTION:   This file provides the webservice calls required for Administration
#
# ************************
# ASSUMES:
# ************************
# SIDE EFFECTS:
# ************************
# LAST MODIFIED FOR JIRA ISSUE: MAV-303
# *************************************************************************
# from utils.streaming.webservices_core import *

from utils.enums import USER_ROLES
import json
import asyncio
import utils.database.web_persistence as WP
from utils.streaming.http_svcs_wrapper import http_service, CONTEXT, CONFIG_PERSISTENCE
import utils.streaming.http_responder as HTTP
import maven_config as MC
date = str


class AdministrationWebservices():

    def __init__(self, configname):
        config = MC.MavenConfig[configname]
        self.persistence = WP.WebPersistence(config[CONFIG_PERSISTENCE])

    @http_service(['GET'], '/users(?:(\d+)-(\d+)?)?',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID],
                  {CONTEXT.USER: int, CONTEXT.CUSTOMERID: int},
                  {USER_ROLES.supervisor})
    def get_users(self, _header, _body, context, matches, _key):
        customer = context[CONTEXT.CUSTOMERID]

        limit = self.helper.limit_clause(matches)

        desired = {
            WP.Results.userid: 'user_id',
            WP.Results.customerid: 'customer_id',
            WP.Results.provid: 'prov_id',
            WP.Results.username: 'user_name',
            WP.Results.officialname: 'official_name',
            WP.Results.displayname: 'display_name',
            WP.Results.state: 'state'
        }
        results = yield from self.persistence.user_info(desired, customer, limit=limit)

        return HTTP.OK_RESPONSE, json.dumps(results), None

    @http_service(['GET'], '/update_user',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID, CONTEXT.STATE, CONTEXT.TARGETUSER],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int,
                   CONTEXT.STATE: str, CONTEXT.TARGETUSER: int},
                  {USER_ROLES.supervisor})
    def update_user(self, _header, _body, context, _matches, _key):
        userid = context[CONTEXT.TARGETUSER]
        state = context[CONTEXT.STATE]

        result = yield from self.persistence.update_user(userid, state)
        if result:
            return HTTP.OK_RESPONSE, json.dumps(['TRUE']), None
        else:
            return HTTP.OK_RESPONSE, json.dumps(['FALSE']), None

    @http_service(['GET'], '/syncusers',
                  [CONTEXT.CUSTOMERID], {CONTEXT.CUSTOMERID: int}, {USER_ROLES.maventask})
    def EHRsync_get_users(self, _header, _body, context, matches, _key):

        limit = self.helper.limit_clause(matches)

        desired = {
            WP.Results.userid: 'user_id',
            WP.Results.customerid: 'customer_id',
            WP.Results.provid: 'prov_id',
            WP.Results.username: 'user_name',
            WP.Results.officialname: 'official_name',
            WP.Results.displayname: 'display_name',
            WP.Results.state: 'state',
            WP.Results.ehrstate: 'ehr_state'
        }
        results = yield from self.persistence.customer_specific_user_info(desired,
                                                                          limit=limit,
                                                                          customer_id=context['customer_id'])
        return HTTP.OK_RESPONSE, json.dumps(results), None

    @http_service(['POST'], '/synccreateuser',
                  [CONTEXT.CUSTOMERID], {CONTEXT.CUSTOMERID: int}, {USER_ROLES.maventask})
    def EHRsync_create_user_provider(self, _header, _body, context, matches, _key):
        info = json.loads(_body.decode('utf-8'))
        yield from self.persistence.EHRsync_create_user_provider(info)
        return HTTP.OK_RESPONSE, json.dumps(info), None

    @http_service(['POST'], '/syncupdateuser',
                  [CONTEXT.CUSTOMERID], {CONTEXT.CUSTOMERID: int}, {USER_ROLES.maventask})
    def EHRsync_update_user_provider(self, _header, _body, context, matches, _key):
        info = json.loads(_body.decode('utf-8'))
        yield from self.persistence.EHRsync_update_user_provider(info)
        return HTTP.OK_RESPONSE, json.dumps(info), None
