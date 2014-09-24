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
import asyncio
import utils.database.web_persistence as WP
from utils.streaming.http_svcs_wrapper import http_service, CONTEXT, CONFIG_PERSISTENCE
from clientApp.webservice.clientapp_rpc_endpoint import ClientAppEndpoint
import utils.streaming.http_responder as HTTP
import utils.crypto.authorization_key as AK
import maven_config as MC
date = str


class AdministrationWebservices():

    def __init__(self, configname, rpc):
        self.client_interface = rpc.create_client(ClientAppEndpoint)
        config = MC.MavenConfig[configname]
        self.persistence = WP.WebPersistence(config[CONFIG_PERSISTENCE])

    @http_service(['POST'], '/setup_customer',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int},
                  {USER_ROLES.administrator})
    def setup_customer(self, _header, body, context, _matches, _key):
        body = json.loads(body.decode('utf-8'))
        user = context[CONTEXT.USER]
        customer = context[CONTEXT.CUSTOMERID]
        clientapp_settings = body
        body.update({CONFIG_PARAMS.EHR_USER_SYNC_INTERVAL.value: 60 * 60})

        is_valid_config = yield from self.client_interface.test_customer_configuration(customer, clientapp_settings)
        if is_valid_config:
            yield from self.persistence.setup_customer(customer, clientapp_settings)
            asyncio.Task(self.persistence.audit_log(user, 'change customer ehr settings', customer,
                                                    details=json.dumps(clientapp_settings)))
            return HTTP.OK_RESPONSE, json.dumps(['TRUE']), None
        else:
            return HTTP.BAD_RESPONSE, json.dumps(['FALSE']), None

    @http_service(['GET'], '/users(?:(\d+)-(\d+)?)?',
                  [CONTEXT.CUSTOMERID],
                  {CONTEXT.CUSTOMERID: int, CONTEXT.ROLES: list},
                  {USER_ROLES.administrator, USER_ROLES.provider,
                   USER_ROLES.mavensupport, USER_ROLES.supervisor})
    def get_users(self, _header, _body, context, matches, _key):
        customer = context[CONTEXT.CUSTOMERID]
        roles = context[CONTEXT.ROLES]
        limit = self.helper.limit_clause(matches)

        if {USER_ROLES.administrator.value, USER_ROLES.provider.value,
           USER_ROLES.mavensupport.value}.intersection(roles):
            desired = {
                WP.Results.userid: 'user_id',
                WP.Results.customerid: 'customer_id',
                WP.Results.provid: 'prov_id',
                WP.Results.username: 'user_name',
                WP.Results.officialname: 'official_name',
                WP.Results.displayname: 'display_name',
                WP.Results.state: 'state',
                WP.Results.ehrstate: 'ehr_state',
                WP.Results.lastlogin: 'last_login',
                WP.Results.profession: 'profession'
            }
        else:
            desired = {WP.Results.username: 'user_name'}
        results = yield from self.persistence.user_info(desired, customer,
                                                        orderby=[WP.Results.ehrstate, WP.Results.profession,
                                                                 WP.Results.displayname],
                                                        limit=limit)

        return HTTP.OK_RESPONSE, json.dumps(results), None

    @http_service(['GET'], '/update_user',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID, CONTEXT.STATE, CONTEXT.TARGETUSER],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int,
                   CONTEXT.STATE: str, CONTEXT.TARGETUSER: str},
                  {USER_ROLES.administrator})
    def update_user(self, _header, _body, context, _matches, _key):
        user = context[CONTEXT.USER]
        target_user = context[CONTEXT.TARGETUSER]
        customer = context[CONTEXT.CUSTOMERID]
        state = context[CONTEXT.STATE]

        yield from self.persistence.update_user(target_user, customer, state)
        if state == 'active':
            asyncio.Task(self.notify_user_reset_password(customer, target_user))
        asyncio.Task(self.persistence.audit_log(user, 'change user state', customer,
                                                target_user=target_user, details=state))

        return HTTP.OK_RESPONSE, json.dumps(['TRUE']), None

    @http_service(['GET'], '/reset_password',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID, CONTEXT.TARGETUSER],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int, CONTEXT.ROLES: list,
                   CONTEXT.TARGETCUSTOMER: int, CONTEXT.TARGETUSER: str},
                  {USER_ROLES.administrator, USER_ROLES.mavensupport})
    def reset_password(self, _header, _body, context, _matches, _key):
        user = context[CONTEXT.USER]
        target_user = context[CONTEXT.TARGETUSER]

        if USER_ROLES.mavensupport.name in context[CONTEXT.ROLES]:
            customer = context[CONTEXT.TARGETCUSTOMER]
        else:
            customer = context[CONTEXT.CUSTOMERID]

        asyncio.Task(self.notify_user_reset_password(customer, target_user))
        asyncio.Task(self.persistence.audit_log(user, 'reset user password', customer,
                                                target_user=target_user))

        return HTTP.OK_RESPONSE, json.dumps(''), None

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

    @asyncio.coroutine
    def notify_user_reset_password(self, customer, username):
        ak = AK.authorization_key([username, str(customer)], 44, 365 * 24 * 60 * 60)
        loginstr = """Welcome to Maven Pathways!

Below are the instructions on how to access Maven for the first time:

1 - Copy the link below to your browser
""" + ('%s#password/newPassword/%s/%s/%s' % (MC.http_addr, username, customer, ak)) + """

2 - Create a new password for your account
Contact Maven Support or your System Admin with any questions."""

        yield from self.client_interface.notify_user(customer, username,
                                                     "Welcome to Maven, set/reset password",
                                                     loginstr)
