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

    @http_service(['GET'], '/setup_customer',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID, CONTEXT.IPADDRESS,
                   CONTEXT.NAME, CONTEXT.PASSWORD, CONTEXT.TIMEOUT,
                   CONTEXT.POLLING],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int,
                   CONTEXT.NAME: str, CONTEXT.IPADDRESS: str,
                   CONTEXT.PASSWORD: str, CONTEXT.TIMEOUT: int,
                   CONTEXT.POLLING: int},
                  {USER_ROLES.administrator})
    def setup_customer(self, _header, _body, context, _matches, _key):
        customer = context[CONTEXT.CUSTOMERID]
        ip = context[CONTEXT.IPADDRESS]
        appname = context[CONTEXT.NAME]
        polling = context[CONTEXT.POLLING]
        timeout = context[CONTEXT.TIMEOUT]

        results = yield from self.persistence.setup_customer(customer, ip, appname, polling, timeout)

        if results:
            return HTTP.OK_RESPONSE, json.dumps(['TRUE']), None
        else:
            return HTTP.OK_RESPONSE, json.dumps(['FALSE']), None

    @http_service(['GET'], '/users(?:(\d+)-(\d+)?)?',
                  [CONTEXT.CUSTOMERID],
                  {CONTEXT.CUSTOMERID: int},
                  {USER_ROLES.administrator})
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
            WP.Results.state: 'state',
            WP.Results.lastlogin: 'last_login'
        }
        results = yield from self.persistence.user_info(desired, customer, limit=limit)

        return HTTP.OK_RESPONSE, json.dumps(results), None

    @http_service(['GET'], '/update_user',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID, CONTEXT.STATE, CONTEXT.TARGETUSER],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int,
                   CONTEXT.STATE: str, CONTEXT.TARGETUSER: int},
                  {USER_ROLES.administrator})
    def update_user(self, _header, _body, context, _matches, _key):
        userid = context[CONTEXT.TARGETUSER]
        state = context[CONTEXT.STATE]

        result = yield from self.persistence.update_user(userid, state)
        if result:
            return HTTP.OK_RESPONSE, json.dumps(['TRUE']), None
        else:
            return HTTP.OK_RESPONSE, json.dumps(['FALSE']), None

    @http_service(['GET'], '/reset_password',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID, CONTEXT.ROLES],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int, CONTEXT.ROLES: list,
                   CONTEXT.TARGETCUSTOMER: int, CONTEXT.TARGETUSER: str},
                  {USER_ROLES.administrator, USER_ROLES.mavensupport})
    def reset_password(self, _header, _body, context, _matches, _key):
        user = None
        customer = None

        if (USER_ROLES.administrator.name in context[CONTEXT.ROLES] or
                USER_ROLES.mavensupport.name in context[CONTEXT.ROLES]):
            user = context.get(CONTEXT.TARGETUSER, None)

        if USER_ROLES.mavensupport.name in context[CONTEXT.ROLES]:
            customer = context.get(CONTEXT.TARGETCUSTOMER, None)

        if not user:
            user = context[CONTEXT.USER]
        if not customer:
            customer = context[CONTEXT.CUSTOMERID]

        result = yield from self.persistence.reset_password(user, customer)
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

    @http_service(['GET'], '/customer_info',
                  [CONTEXT.CUSTOMERID],
                  {CONTEXT.CUSTOMERID: int},
                  {USER_ROLES.administrator, USER_ROLES.mavensupport})
    def get_customer_info(self, _header, _body, context, matches, _key):
        """
        This method returns ClientApp Details by formatting the dictionary
        contained in the related column in the customer table
        """
        customerid = context[CONTEXT.CUSTOMERID]

        desired = {
            WP.Results.settings: 'settings',
        }
        results = yield from self.persistence.customer_info(desired, customerid)

        return HTTP.OK_RESPONSE, json.dumps(results[0]), None

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
