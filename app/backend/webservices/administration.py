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
from maven_logging import TASK
from recaptcha.client import captcha
date = str


class AdministrationWebservices():

    def __init__(self, configname, rpc):
        self.client_interface = rpc.create_client(ClientAppEndpoint)
        config = MC.MavenConfig[configname]
        self.persistence = WP.WebPersistence(config[CONFIG_PERSISTENCE])

    @http_service(['POST'], '/setup_customer',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID, CONTEXT.ROLES],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int,
                   CONTEXT.ROLES: list, CONTEXT.TARGETCUSTOMER: int},
                  {USER_ROLES.administrator, USER_ROLES.mavensupport})
    def setup_customer(self, _header, body, context, _matches, _key):
        body = json.loads(body.decode('utf-8'))
        user = context[CONTEXT.USER]
        customer = context[CONTEXT.CUSTOMERID]
        target_customer = context.get(CONTEXT.TARGETCUSTOMER, None)
        if not target_customer or (USER_ROLES.mavensupport.value not in context[CONTEXT.ROLES]):
            target_customer = customer

        clientapp_settings = body
        body.update({CONFIG_PARAMS.EHR_USER_SYNC_INTERVAL.value: 60 * 60})
        if 'locked' in clientapp_settings:
            clientapp_settings.pop('locked')
            result = yield from self.persistence.customer_info({WP.Results.settings: 'settings'},
                                                               customer=customer)
            settings = result[0]['settings']
            if settings:
                settings.update(clientapp_settings)
                clientapp_settings = settings
        try:
            yield from self.client_interface.test_customer_configuration(target_customer,
                                                                         clientapp_settings)
        except Exception as e:
            return HTTP.BAD_RESPONSE, json.dumps(str(e)), None

        # at this point, the configuration has succeeded
        yield from self.persistence.setup_customer(target_customer, clientapp_settings)
        logged_settings = {k: clientapp_settings.get(k, None) for k in {
            CONFIG_PARAMS.EHR_DISABLE_INTEGRATION.value,
            CONFIG_PARAMS.EHR_API_BASE_URL.value
        }}
        TASK(self.persistence.audit_log(user, 'change customer ehr settings', customer,
                                        details=json.dumps(logged_settings),
                                        target_user_and_customer=('', target_customer)))
        return HTTP.OK_RESPONSE, json.dumps(['TRUE']), None

    @http_service(['GET'], '/users(?:(\d+)-(\d+)?)?',
                  [CONTEXT.CUSTOMERID],
                  {CONTEXT.CUSTOMERID: int, CONTEXT.ROLES: list,
                   CONTEXT.TARGETROLE: str, CONTEXT.TARGETUSER: str,
                   CONTEXT.TARGETCUSTOMER: int},
                  {USER_ROLES.administrator, USER_ROLES.provider,
                   USER_ROLES.mavensupport, USER_ROLES.supervisor})
    def get_users(self, _header, _body, context, matches, _key):
        customer = context[CONTEXT.CUSTOMERID]
        roles = context[CONTEXT.ROLES]
        targetrole = context.get(CONTEXT.TARGETROLE, None)
        targetuser = context.get(CONTEXT.TARGETUSER, None)
        target_customer = context.get(CONTEXT.TARGETCUSTOMER, None)
        if not target_customer or USER_ROLES.mavensupport.value not in roles:
            target_customer = customer

        limit = self.helper.limit_clause(matches)

        if {USER_ROLES.administrator.value, USER_ROLES.provider.value,
           USER_ROLES.mavensupport.value}.intersection(roles) and not targetrole:
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
                WP.Results.profession: 'profession',
                WP.Results.roles: 'roles',
                WP.Results.notify1: 'notify_primary',
                WP.Results.notify2: 'notify_secondary'
            }
        else:
            desired = {
                # WP.Results.officialname: 'official_name',
                # WP.Results.username: 'user_name',
                WP.Results.officialname: 'label',
                WP.Results.username: 'value',
            }
        results = yield from self.persistence.user_info(desired, target_customer, role=targetrole,
                                                        officialname=targetuser,
                                                        orderby=[WP.Results.ehrstate, WP.Results.profession,
                                                                 WP.Results.displayname],
                                                        limit=limit)

        return HTTP.OK_RESPONSE, json.dumps(results), None

    @http_service(['GET'], '/update_user',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID, CONTEXT.STATE, CONTEXT.TARGETUSER,
                   CONTEXT.ROLES],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int, CONTEXT.ROLES: list,
                   CONTEXT.STATE: str, CONTEXT.TARGETUSER: str, CONTEXT.TARGETCUSTOMER: int},
                  {USER_ROLES.administrator, USER_ROLES.mavensupport})
    def update_user(self, _header, _body, context, _matches, _key):
        user = context[CONTEXT.USER]
        target_user = context[CONTEXT.TARGETUSER]
        customer = context[CONTEXT.CUSTOMERID]
        state = context[CONTEXT.STATE]
        target_customer = context.get(CONTEXT.TARGETCUSTOMER, None)
        if not target_customer or USER_ROLES.mavensupport.value not in context[CONTEXT.ROLES]:
            target_customer = customer

        results = yield from self.persistence.update_user(target_user, target_customer, state, {WP.Results.ehrstate: 'ehr_state'})
        user_info = results[0]

        message = 'TRUE'
        if state == 'active':
            if user_info['ehr_state'] != "active":
                ak = AK.authorization_key([target_user, str(target_customer)], 44, 365 * 24 * 60 * 60)
                message = '%s#password/newPassword/%s/%s/%s' % (MC.http_addr, target_user, target_customer, ak)
            else:
                TASK(self.notify_user_reset_password(target_customer, target_user))

        TASK(self.persistence.audit_log(user, 'change user state', customer,
                                        target_user_and_customer=(target_user, target_customer),
                                        details=state))
        TASK(self.client_interface.update_user_state(target_customer, target_user, state))

        return HTTP.OK_RESPONSE, json.dumps(message), None

    @http_service(['GET'], '/update_user_pref',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID, CONTEXT.ROLES],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int, CONTEXT.TARGETUSER: str,
                   CONTEXT.NOTIFY_PRIMARY: str, CONTEXT.NOTIFY_SECONDARY: str,
                   CONTEXT.ROLES: list, CONTEXT.TARGETCUSTOMER: int},
                  {USER_ROLES.administrator, USER_ROLES.mavensupport})
    def update_user_pref(self, _header, _body, context, _matches, _key):

        customer = context.get(CONTEXT.CUSTOMERID, None)
        prov_user_name = context.get(CONTEXT.USER, None)
        target_user_name = context.get(CONTEXT.TARGETUSER, None)
        notify_primary = context.get(CONTEXT.NOTIFY_PRIMARY, None)
        notify_secondary = context.get(CONTEXT.NOTIFY_SECONDARY, None)
        target_customer = context.get(CONTEXT.TARGETCUSTOMER, None)
        if not target_customer or (USER_ROLES.mavensupport.value not in context[CONTEXT.ROLES]):
            target_customer = customer

        # allow customer administrator to override user preferences
        if target_user_name and ((USER_ROLES.administrator.value in context[CONTEXT.ROLES]) or
           (USER_ROLES.mavensupport.value in context[CONTEXT.ROLES])):
            prov_user_name = target_user_name

        try:
            yield from self.persistence.update_user_notify_preferences(prov_user_name, target_customer,
                                                                       notify_primary, notify_secondary)
        except Exception as e:
            return HTTP.BAD_RESPONSE, json.dumps(str(e)), None

        return HTTP.OK_RESPONSE, json.dumps(['TRUE']), None

    @http_service(['GET'], '/reset_password',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID, CONTEXT.TARGETUSER, CONTEXT.ROLES],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int, CONTEXT.ROLES: list,
                   CONTEXT.TARGETCUSTOMER: int, CONTEXT.TARGETUSER: str, CONTEXT.EHR_STATE: str},
                  {USER_ROLES.administrator, USER_ROLES.mavensupport})
    def reset_password(self, _header, _body, context, _matches, _key):
        user = context[CONTEXT.USER]
        target_user = context[CONTEXT.TARGETUSER]
        ehr_state = context[CONTEXT.EHR_STATE]

        customer = context[CONTEXT.CUSTOMERID]
        target_customer = context[CONTEXT.TARGETCUSTOMER]
        if not target_customer or USER_ROLES.mavensupport.name not in context[CONTEXT.ROLES]:
            target_customer = customer

        message = ''
        if ehr_state != "active":
            ak = AK.authorization_key([target_user, str(target_customer)], 44, 365 * 24 * 60 * 60)
            message = '%s#password/newPassword/%s/%s/%s' % (MC.http_addr, target_user, target_customer, ak)
        else:
            TASK(self.notify_user_reset_password(target_customer, target_user))

        TASK(self.persistence.audit_log(user, 'reset user password', customer,
                                        target_user_and_customer=(target_user, target_customer)))

        return HTTP.OK_RESPONSE, json.dumps(message), None

    @http_service(['GET'], '/customer_info',
                  [CONTEXT.CUSTOMERID],
                  {CONTEXT.CUSTOMERID: int, CONTEXT.TARGETCUSTOMER: int,
                   CONTEXT.ROLES: list},
                  {USER_ROLES.administrator, USER_ROLES.mavensupport})
    def get_customer_info(self, _header, _body, context, matches, _key):
        """
        This method returns ClientApp Details by formatting the dictionary
        contained in the related column in the customer table
        """
        customer = context[CONTEXT.CUSTOMERID]
        target_customer = context.get(CONTEXT.TARGETCUSTOMER, None)
        if not target_customer or (USER_ROLES.mavensupport.name not in context[CONTEXT.ROLES]):
            target_customer = customer

        desired = {
            WP.Results.settings: 'settings',
        }
        results = yield from self.persistence.customer_info(desired, target_customer)

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

    @http_service(['GET'], '/recaptcha', None, None, None)
    def get_recaptcha(self, *args):
        public = MC.recaptcha_public
        if public:
            return HTTP.OK_RESPONSE, bytes(public, 'utf-8'), [b'Content-Type: text/html']
            # recaptcha = captcha.displayhtml(public, use_ssl=True)
            # return HTTP.OK_RESPONSE, bytes(recaptcha, 'utf-8'), [b'Content-Type: text/html']
        else:
            return HTTP.BAD_RESPONSE, b'', None

    @asyncio.coroutine
    def verify_recaptcha(self, challenge, response, ip):
        if not MC.recaptcha_private:
            return HTTP.BAD_RESPONSE, b'', None
        resp = yield from captcha.submit(challenge, response, MC.recaptcha_private, ip)
        return resp.is_valid

    @http_service(['GET'], '/send_reset_password', None, None, None)
    def emr_reset_password(self, headers, body, context, matches, key):
        challenge = context['recaptcha_challenge_field'][0]
        response = context['recaptcha_response_field'][0]
        username = context[CONTEXT.USER][0].upper()
        customer = int(context[CONTEXT.CUSTOMERID][0])
        ip = headers.get_headers()['X-Real-IP']
        valid = yield from self.verify_recaptcha(challenge, response, ip)
        if not valid:
            return HTTP.BAD_RESPONSE, b'', None
        else:
            TASK(self.notify_user_reset_password(customer, username))
            TASK(self.persistence.audit_log(username, 'self-service reset password', customer))
            return HTTP.OK_RESPONSE, b'', None
