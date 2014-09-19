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

from utils.enums import USER_ROLES, CONFIG_PARAMS
import json
import utils.database.web_persistence as WP
from utils.streaming.http_svcs_wrapper import http_service, CONTEXT, CONFIG_PERSISTENCE
import utils.streaming.http_responder as HTTP
import maven_config as MC
date = str


class AdministrationWebservices():

    def __init__(self, configname):
        config = MC.MavenConfig[configname]
        self.persistence = WP.WebPersistence(config[CONFIG_PERSISTENCE])

    @http_service(['POST'], '/setup_customer',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int},
                  {USER_ROLES.administrator})
    def setup_customer(self, _header, body, context, _matches, _key):
        body = json.loads(body.decode('utf-8'))

        customer = context[CONTEXT.CUSTOMERID]
        clientapp_settings = {
            CONFIG_PARAMS.EHR_API_BASE_URL.value: body[CONTEXT.IPADDRESS],
            CONFIG_PARAMS.EHR_API_APPNAME.value: body[CONTEXT.NAME],
            CONFIG_PARAMS.EHR_API_POLLING_INTERVAL.value: body[CONTEXT.POLLING],
            CONFIG_PARAMS.EHR_USER_TIMEOUT.value: body[CONTEXT.TIMEOUT],
            CONFIG_PARAMS.EHR_API_PASSWORD.value: body[CONTEXT.PASSWORD],
            CONFIG_PARAMS.EHR_USER_SYNC_DELAY.value: 60 * 60,
        }
        if self.client_interface.test_customer_configuration(customer, clientapp_settings):
            results = yield from self.persistence.setup_customer(customer, clientapp_settings)
            if results:
                return HTTP.OK_RESPONSE, json.dumps(['TRUE']), None
        else:
            return HTTP.BAD_RESPONSE, json.dumps(['FALSE']), None

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
                   CONTEXT.STATE: str, CONTEXT.TARGETUSER: str},
                  {USER_ROLES.administrator})
    def update_user(self, _header, _body, context, _matches, _key):
        user = context[CONTEXT.TARGETUSER]
        customer = context[CONTEXT.CUSTOMERID]
        state = context[CONTEXT.STATE]

        result = yield from self.persistence.update_user(user, customer, state)
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
