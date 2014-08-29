# *************************************************************************
# Copyright (c) 2014 - Maven Medical
#
# ************************
# AUTHOR:
__author__ = 'Yuki Uchino'
# ************************
# DESCRIPTION:   This file provides the webservice calls required for User Authentication
#
# ************************
# ASSUMES:
# ************************
# SIDE EFFECTS:
# ************************
# LAST MODIFIED FOR JIRA ISSUE: MAV-303
# *************************************************************************
import re
import json
import bcrypt
import asyncio
import utils.crypto.authorization_key as AK
import utils.database.web_persistence as WP
from utils.streaming.http_svcs_wrapper import http_service, CONTEXT, CONFIG_PERSISTENCE
import utils.streaming.http_responder as HTTP
import maven_config as MC

AUTH_LENGTH = 44  # 44 base 64 encoded bits gives the entire 256 bites of SHA2 hash
LOGIN_TIMEOUT = 60 * 60  # 1 hour


class LoginError(Exception):
    pass


class AuthenticationWebservices():

    def __init__(self, configname):
        config = MC.MavenConfig[configname]
        self.persistence = WP.WebPersistence(config[CONFIG_PERSISTENCE])

    @http_service(['POST'], '/login', None, None, None)
    def post_login(self, header, body, _context, _matches, _key):
        info = json.loads(body.decode('utf-8'))

        user_and_pw = set((CONTEXT.USER, 'password')).issubset(info)
        prov_and_auth = set(('provider', 'customer', 'userAuth')).issubset(info)
        if not user_and_pw and not prov_and_auth:
            return HTTP.BAD_RESPONSE, b'', None

        desired = {k: k for k in [
            WP.Results.userid,
            WP.Results.customerid,
            WP.Results.provid,
            WP.Results.displayname,
            WP.Results.officialname,
            WP.Results.password,
            WP.Results.passexpired,
            WP.Results.userstate,
            # WP.Results.failedlogins,
            WP.Results.recentkeys,
            WP.Results.roles
        ]}
        attempted = None
        try:
            method = 'failed'
            user_info = {}
            # if header.get_headers().get('VERIFIED','SUCCESS') == 'SUCCESS':
            if user_and_pw:
                attempted = info['user']
                try:
                    user_info = yield from self.persistence.pre_login(desired,
                                                                      username=attempted)
                except IndexError:
                    raise LoginError('badLogin')
                passhash = user_info[WP.Results.password].tobytes()
                if (not passhash or
                        bcrypt.hashpw(bytes(info['password'], 'utf-8'),
                                      passhash[:29]) != passhash):
                    raise LoginError('badLogin')
                if user_info[WP.Results.passexpired] or 'newpassword' in info:
                    yield from self.hash_new_password(user_info[WP.Results.userid],
                                                      info.get('newpassword', ''))
                method = 'local'
            else:
                attempted = [info['provider'], info['customer']]
                try:  # this means that the password was a pre-authenticated link
                    AK.check_authorization(attempted, info['userAuth'], AUTH_LENGTH)
                except AK.UnauthorizedException:
                    raise LoginError('badLogin')
                user_info = yield from self.persistence.pre_login(desired,
                                                                  provider=attempted,
                                                                  keycheck='1m')
                method = 'forward'
                # was this auth key used recently
                if info['userAuth'] in user_info[WP.Results.recentkeys]:
                    raise LoginError('reusedLogin')

            # make sure this user exists and is active
            if not user_info[WP.Results.userstate] == 'active':
                raise LoginError('disabledUser')

                # at the point, the user has succeeded to login
            user = str(user_info[WP.Results.userid])
            provider = user_info[WP.Results.provid]
            customer = str(user_info[WP.Results.customerid])
            roles = user_info[WP.Results.roles]
            user_auth = AK.authorization_key([[user], [provider], [customer], sorted(roles)],
                                             AUTH_LENGTH, LOGIN_TIMEOUT)

            desired_layout = {
                WP.Results.widget: 'widget',
                WP.Results.template: 'template',
                WP.Results.element: 'element',
                WP.Results.priority: 'priority'
            }
            widgets = yield from self.persistence.layout_info(desired_layout,
                                                              user_info[WP.Results.userid])

            ret = {CONTEXT.USER: user_info[WP.Results.userid],
                   'display': user_info[WP.Results.displayname],
                   'customer_id': customer,
                   'official_name': user_info[WP.Results.officialname],
                   CONTEXT.PROVIDER: provider,
                   CONTEXT.USER: user,
                   CONTEXT.ROLES: roles,
                   'widgets': widgets, CONTEXT.KEY: user_auth}

            return HTTP.OK_RESPONSE, json.dumps(ret), None
        except LoginError as err:
            return HTTP.UNAUTHORIZED_RESPONSE, json.dumps({'loginTemplate':
                                                           err.args[0] + ".html"}), None
        finally:
            yield from self.persistence.record_login(attempted,
                                                     method,
                                                     header.get_headers().get('X-Real-IP'),
                                                     info['userAuth'] if method == 'forward' else None)

    @asyncio.coroutine
    def hash_new_password(self, user, newpassword):
        if (len(newpassword) < 8
                or not re.search("[0-9]", newpassword)
                or not re.search("[a-z]", newpassword)
                or not re.search("[A-Z]", newpassword)):
            raise LoginError('expiredPassword')
        salt = bcrypt.gensalt(4)
        ret = bcrypt.hashpw(bytes(newpassword, 'utf-8'), salt)
        try:
            yield from self.persistence.update_password(user, ret)
        except:
            import traceback
            traceback.print_exc()
            raise LoginError('expiredPassword')
