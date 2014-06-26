import utils.streaming.http_responder as HTTP    
import utils.crypto.authorization_key as AK
import itertools
import asyncio


class HTTPHelper:
    def __init__(self, contexts_user, context_key, auth_length):
        self.contexts_user = contexts_user
        self.context_key = context_key
        self.auth_length = auth_length
        

    def restrict_context(self, qs, required, available):
        if not set(required).issubset(qs.keys()):
            raise HTTP.IncompleteRequest('Request is incomplete.  Required arguments are: '
                                         +', '.join(required)+".\n")
        # not implemented yet - making sure optional parameters are the right type

        if not self.context_key in qs:
            raise HTTP.UnauthorizedRequest('User is not logged in.')
        try:
#            print([qs[x][0] for x in self.contexts_user])
            AK.check_authorization([qs[x][0] for x in self.contexts_user], qs[self.context_key][0], self.auth_length)
        except AK.UnauthorizedException as ue:
            raise HTTP.UnauthorizedRequest(str(ue))

        context = {}
        for k, v in qs.items():
            if k in available:
                if available[k] is list:
                    context[k]=v
                else:
                    if len(v) is 1:
                        try:
                            context[k] = available[k](v[0])
                        except ValueError:
                            raise HTTP.IncompleteRequest('Request has parameter %s which is of the wrong type.' % k)
                    else:
                        raise HTTP.IncompleteRequest('Request requires exactly one instance of parameter %s.' % k)
        return context

    def copy_and_append(self, m, kv):
        return dict(itertools.chain(m.items(),[kv]))

    def limit_clause(self, matches):
        if len(matches)==2 and all(matches):
            return " LIMIT %d OFFSET %d" % (int(matches[1])-int(matches[0]), int(matches[0]))
        else:
            return ""

    @asyncio.coroutine
    def stub(self, _header, _body, _qs, _matches, _key):
        return (HTTP.OK_RESPONSE, b'', None)



