import asyncio
from functools import wraps
import utils.streaming.http_responder as HTTP

CONFIG_PERSISTENCE = 'persistence'
EMPTY_RETURN = [{'id': 000000, 'term': "No Results Found", 'code': 000000, 'type': 'none'}]


class CONTEXT():
    USER = 'user'
    PROVIDER = 'provider'
    ROLES = 'roles'
    DATE = 'date'
    DATERANGE = 'daterange'
    PATIENTLIST = 'patients'
    DEPARTMENT = 'department'
    ORDERTYPE = 'ordertype'
    ORDERID = 'order_id'
    ALERTID = 'alert_id'
    RULEID = 'rule_id'
    KEY = 'userAuth'
    ENCOUNTER = 'encounter'
    CUSTOMERID = 'customer_id'
    DIAGNOSIS = 'diagnosis'
    PATIENTNAME = 'patientname'
    STARTDATE = 'startdate'
    ENDDATE = 'enddate'
    CATEGORY = 'category'
    CATEGORIES = 'categories'
    NAME = 'name'
    ABBREVIATION = "abbr"
    IPADDRESS = "ip"
    LICENSE = "license"
    OFFICIALNAME = 'official_name'
    DISPLAYNAME = 'display_name'
    ACTION = 'action'
    ACTIONCOMMENT = 'action_comment'
    PATHID = 'pathid'
    SEARCH_PARAM = 'search_param'
    TARGETUSER = 'target_user'
    TARGETPROVIDER = 'target_provider'
    TARGETCUSTOMER = 'target_customer'
    STATE = 'state'


def http_service(methods, url, required, available, roles):
    """ decorator for http handlers
    :param methods: the http methods to handle
    :param url: the url to handle
    :param required: a list of keys required to be in the query string
    :param available: a list of keys (and their types) to be extracted
                      from the query string and put into the context
    :param roles: a list of user roles, at least one of which is required
                  to use this service
    """
    roles = roles and {r.value for r in roles}

    def decorator(func):
        # Takes the Webservice Function that was decorated by @http_service
        # and runs that Function through the following code to modify it
        @asyncio.coroutine
        @wraps(func)
        def worker(self, header, body, qs, matches, key):

            # the UI sends a list 'roles' as 'roles[]', so we adjust that here
            if roles and not roles.intersection(qs.get(CONTEXT.ROLES + '[]', set())):
                return HTTP.UNAUTHORIZED_RESPONSE, b'', None
            context = qs
            if required or available:
                context = self.helper.restrict_context(qs, required, available)
            res = yield from func(self, header, body, context, matches, key)
            return res

        # Adding the function attribute gives us the ability to filter on hasattr()
        # when recursively adding base classes' functions to the webservice handler
        worker.maven_webservice = [methods, url]
        return worker
    return decorator
