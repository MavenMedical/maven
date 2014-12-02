import time
import utils.streaming.http_responder as HTTP
from app.backend.webservices.authentication import AUTH_LENGTH
import utils.crypto.authorization_key as AK
import itertools
import asyncio
from dateutil.parser import parse
import maven_logging as ML
from collections import defaultdict
# from datetime import datetime, timezone, timedelta

logger = ML.get_logger()
ML.set_debug('/tmp/http_helper.log')


class HTTPHelper:
    def __init__(self, contexts_user, context_key, cookie_map=None):
        self.contexts_user = contexts_user
        self.context_key = context_key
        self.auth_length = AUTH_LENGTH
        self.cookie_map = defaultdict(lambda: lambda x: x[0])
        if cookie_map:
            self.cookie_map.update(cookie_map)

    def make_auth_and_cookie(self, qs, timeout, ip, all_cookies=True):
        timeout = int(timeout)
        # expires = (datetime.now(timezone.utc) + timedelta(seconds=timeout))
        # expires = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')

        def make_cookie(k, v, expires=None):
            # if expires:
            # return bytes('Set-Cookie: %s=%s; Expires=%s; Path=/;' % (k, v, expires), 'utf-8')
            # else:
            if type(v) != tuple:
                v = (v, '')
            return bytes('Set-Cookie: %s=%s; Path=/; %s' % (k, v[0], v[1]), 'utf-8')

        auth_list = [sorted(qs[k]) for k in self.contexts_user]
        user_auth = AK.authorization_key(auth_list + [[timeout], [ip]],
                                         self.auth_length, timeout)

        # add 8 bytes at the beginning for the timeout code
        user_auth = AK.bytestostring(int(timeout).to_bytes(4, 'big')) + user_auth

        thistime = time.time()
        cookie_base = {
            self.context_key: (user_auth, 'HttpOnly;'),
            'valid-through': int(thistime + timeout) * 1000,
            'now': int(thistime) * 1000,
        }
        if all_cookies:
            cookie_base.update({k: self.cookie_map[k](qs[k]) for k in self.contexts_user})

        cookies = [make_cookie(k, v) for k, v in cookie_base.items()]
        return user_auth, cookies

    def restrict_context(self, qs, required, available, ip):
        for k in list(qs.keys()):
            try:
                if k[-2:] == '[]':
                    qs[k[:-2]] = qs.pop(k)
            except (KeyError, IndexError):
                pass

        if not set(required).issubset(qs.keys()):
            raise HTTP.IncompleteRequest('Request is incomplete.  Required arguments are: '
                                         + ', '.join(required) + ".\n")

        if self.context_key not in qs:
            raise HTTP.UnauthorizedRequest('User is not logged in.')
        user_auth = qs[self.context_key][0]
        timeout = int.from_bytes(AK.stringtobytes(user_auth[:8]), 'big')
        user_auth = user_auth[8:]
        try:
            AK.check_authorization([sorted(qs.get(x, [''])) for x in self.contexts_user]
                                   + [[timeout], [ip]],
                                   user_auth, self.auth_length)
        except AK.UnauthorizedException as ue:
            raise HTTP.UnauthorizedRequest(str(ue))

        new_auth, cookie = self.make_auth_and_cookie(qs, timeout, ip, False)

        context = {}
        for k, v in qs.items():
            if k in available:
                if available[k] is list:
                    context[k] = v
                else:
                    if len(v) is 1:
                        try:
                            # logger.debug(k + "\t" + str(available[k]) + "\t" + str(v))
                            context[k] = available[k](v[0])
                        except ValueError:
                            raise HTTP.IncompleteRequest('Request has parameter %s which '
                                                         + 'is of the wrong type %s.' % (k, v[0]))
                    else:
                        raise HTTP.IncompleteRequest('Request requires exactly one instance '
                                                     + 'of parameter %s.' % (k,))
        return context, cookie

    def copy_and_append(self, m, kv):
        return dict(itertools.chain(m.items(), [kv]))

    def get_date(self, context, field):
        d = context.get(field, None)
        if d:
            return parse(d).date()
        else:
            return None

    def limit_clause(self, matches):
        if len(matches) == 2 and all(matches):
            return " LIMIT %d OFFSET %d" % (int(matches[1]) - int(matches[0]), int(matches[0]))
        else:
            return ""

    @asyncio.coroutine
    def stub(self, _header, _body, _qs, _matches, _key):
        return (HTTP.OK_RESPONSE, b'', None)
