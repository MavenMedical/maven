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
from utils.enums import CONFIG_PARAMS, USER_ROLES
import maven_config as MC
import maven_logging as ML

AUTH_LENGTH = 44  # 44 base 64 encoded bits gives the entire 256 bites of SHA2 hash
LOGIN_TIMEOUT = 60 * 60  # 1 hour

CONFIG_SPECIFICROLE = 'specificrole'
CONFIG_OAUTH = 'oauth'


class LoginError(Exception):
    pass


class AuthenticationWebservices():

    def __init__(self, configname, _rpc, timeout=None):
        config = MC.MavenConfig[configname]
        self.persistence = WP.WebPersistence(config[CONFIG_PERSISTENCE])
        self.persistence.schedule()
        self.specific_role = config.get(CONFIG_SPECIFICROLE, None)
        self.oauth = config.get(CONFIG_OAUTH, None)
        self.timeout = timeout or LOGIN_TIMEOUT

    @http_service(['POST'], '/login', None, None, None)
    def post_login(self, header, body, _context, _matches, _key):
        info = json.loads(body.decode('utf-8'))

        user_and_pw = set((CONTEXT.USER, CONTEXT.CUSTOMERID, CONTEXT.PASSWORD)).issubset(info)
        prov_and_auth = (set((CONTEXT.USER, CONTEXT.CUSTOMERID)).issubset(info)
                         and (CONFIG_OAUTH in info or 'userAuth' in info))

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
            WP.Results.roles,
            WP.Results.ehrstate,
            WP.Results.settings,
        ]}
        attempted = None
        if info.get(CONTEXT.ROLES, None):
            rolefilter = lambda r: r in info[CONTEXT.ROLES]
        else:
            rolefilter = lambda r: True
        auth = ''
        username = info[CONTEXT.USER].upper()
        customer = info[CONTEXT.CUSTOMERID]
        method = 'failed'
        user_info = {}
        # import pdb
        # pdb.set_trace()
        try:
            # if header.get_headers().get('VERIFIED','SUCCESS') == 'SUCCESS':
            if user_and_pw:
                attempted = ' '.join([username, customer])
                try:
                    user_info = yield from self.persistence.pre_login(desired, customer,
                                                                      username)
                    # pdb.set_trace()

                except IndexError:
                    raise LoginError('badLogin')
                passhash = user_info[WP.Results.password].tobytes()
                if (not passhash or
                        bcrypt.hashpw(bytes(info[CONTEXT.PASSWORD], 'utf-8'),
                                      passhash[:29]) != passhash):
                    raise LoginError('badLogin')
                method = 'local'
            else:
                if info.get(CONTEXT.ROLES, None):
                    attempted = [info[CONTEXT.USER], info[CONTEXT.CUSTOMERID], info[CONTEXT.ROLES]]
                else:
                    attempted = [info[CONTEXT.USER], info[CONTEXT.CUSTOMERID]]
                auth = info.get('userAuth', None) or info.get(CONFIG_OAUTH, None)
                try:  # this means that the password was a pre-authenticated link
                    AK.check_authorization(attempted, auth, AUTH_LENGTH)
                except AK.UnauthorizedException as e:
                    ML.DEBUG('forward login failed for %s: %s' % (attempted, e))
                    raise LoginError('badLogin')
                user_info = yield from self.persistence.pre_login(desired,
                                                                  customer,
                                                                  username,
                                                                  keycheck='1m')
                method = 'forward'
                # was this auth key used recently
                if auth in user_info[WP.Results.recentkeys]:
                    raise LoginError('reusedLogin')

            if (user_info[WP.Results.userstate] != 'active'
               or (user_info[WP.Results.ehrstate] == 'disabled' and USER_ROLES.administrator.value not in user_info[WP.Results.roles])):
                raise LoginError('disabledLogin')

            customer = str(user_info[WP.Results.customerid])
            if user_info[WP.Results.passexpired] or 'newpassword' in info:
                yield from self.hash_new_password(user_info[WP.Results.userid],
                                                  info.get('newpassword', ''))
                asyncio.Task(self.persistence.audit_log(username, 'updated password', customer))

            # at the point, the user has succeeded to login
            provider = user_info[WP.Results.provid]
            roles = [self.specific_role] if self.specific_role else user_info[WP.Results.roles]
            roles = list(filter(rolefilter, roles))
            try:
                clientapp_settings = json.loads(user_info[WP.Results.settings])
                timeout = float(clientapp_settings[CONFIG_PARAMS.EHR_USER_TIMEOUT.value]) * 60
            except (KeyError, ValueError):
                timeout = self.timeout
            user_auth = AK.authorization_key([[username], [provider], [customer], sorted(roles)],
                                             AUTH_LENGTH, timeout)

            desired_layout = {
                WP.Results.widget: 'widget',
                WP.Results.template: 'template',
                WP.Results.element: 'element',
                WP.Results.priority: 'priority'
            }
            widgets = yield from self.persistence.layout_info(desired_layout,
                                                              user_info[WP.Results.userid])

            ret = {CONTEXT.USERID: user_info[WP.Results.userid],
                   'display': user_info[WP.Results.displayname],
                   CONTEXT.CUSTOMERID: customer,
                   'official_name': user_info[WP.Results.officialname],
                   CONTEXT.PROVIDER: provider,
                   CONTEXT.USER: username,
                   CONTEXT.ROLES: roles,
                   'widgets': widgets, CONTEXT.KEY: user_auth}

            if self.oauth and method != 'forward':
                ak = AK.authorization_key([username, customer, roles], AUTH_LENGTH,
                                          180 * 24 * 60 * 60)  # half a year for oauth
                ret[CONFIG_OAUTH] = ak
            return HTTP.OK_RESPONSE, json.dumps(ret), None
        except LoginError as err:
            return HTTP.UNAUTHORIZED_RESPONSE, json.dumps({'loginTemplate':
                                                           err.args[0] + ".html"}), None
        finally:
            if method == 'failed' and user_info:
                asyncio.Task(self.persistence.audit_log(username, 'failed login', customer))
            yield from self.persistence.record_login(username, customer,
                                                     method,
                                                     header.get_headers().get('X-Real-IP'),
                                                     auth if method == 'forward' else None)

    @asyncio.coroutine
    def hash_new_password(self, user, newpassword):
        if (len(newpassword) < 8
                or not re.search("[0-9]", newpassword)
                or not re.search("[a-z]", newpassword)
                or not re.search("[A-Z]", newpassword)):
            raise LoginError('badNewPassword')
        salt = bcrypt.gensalt(4)
        ret = bcrypt.hashpw(bytes(newpassword, 'utf-8'), salt)
        try:
            yield from self.persistence.update_password(user, ret)
        except:
            raise LoginError('badNewPassword')
