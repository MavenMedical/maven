import aiohttp
import asyncio
import json
from utils.enums import CONFIG_PARAMS
from maven_logging import WARN
CONFIG_BASEURL = 'base url'
CONFIG_OTHERHEADERS = 'other headers'

_http_responses = {
    400: 'BAD REQUEST',
    401: 'UNAUTHORIZED',
    403: 'FORBIDDEN',
    404: 'NOT FOUND',
    405: 'NOT ALLOWED',
    500: 'INTERNAL SERVER ERROR',
    502: 'BAD GATEWAY',
    503: 'SERVICE UNAVAILABLE',
    504: 'GATEWAY TIMEOUT',
}


class HttpClientException(Exception):

    def __init__(self, string):
        Exception.__init__(self, str(string))


class http_api():
    """ This class encapsulates all of the common details for contacting a
    REST or other remote procedure call - like API on a single remote server.

    The client can specifically request the results at a URL, or it can apply
    a decorator and get results passed in as arguments once they are fetched.

    It is designed to be either subclassed (a function get_data() calls get("data"))
    or as a decorator

    It also handles timeouts, caching, and other common functionality.
    """

    def __init__(self, config: dict, other_headers: {str: str}=None,
                 decode: bool=True):
        """ Create a new instance of the remote query object using the shared parameters
        :param configname: the name of this module in the configuration file.
                           It must contain the base url
        :param other_headers=None: optional parameter for additional headers (api key)
        :param decode: True if the output should be returned as a string, false means bytes
        """
        self.config = config
        self.base_url = self.config[CONFIG_PARAMS.EHR_API_BASE_URL.value]
        self.other_headers = self.config.get(CONFIG_OTHERHEADERS, {})
        if other_headers:
            self.other_headers.update(other_headers)
        self.decode = decode

    def update_config(self, config):
        if config == self.config:
            return False
        else:
            self.config = config
            base_url = self.config[CONFIG_PARAMS.EHR_API_BASE_URL.value]
            if base_url == self.base_url:
                return False
            else:
                self.base_url = base_url
                return True

    @asyncio.coroutine
    def initiate(self, resource: str, method: ['GET', 'POST', 'PUT'],
                 rawdata=False, newheaders=None, **kwargs) -> {bytes, str}:
        """ make a connection to a remote server and wait for a response
        :param resource: A string to append to the base url
        :param method: one of the standard http methods
        :param rawdata: True if the data should be passed straight instead of sent as json
        :param newheaders: overwrite any existing headers with these
        :param kwargs: data to send.  If it contains a key 'data', it is dumped as json
                       and put in the body.  If it contains a key 'params', they are
                       added to the url.  If neither, then the entire kwargs are added to
                       the body (if post/put) or url (if get)
                       The key must contain "data" if rawdata is used
        """
        data = None
        params = None
        if 'params' in kwargs:
            params = kwargs['params']
        if 'data' in kwargs:
            if rawdata:
                data = kwargs['data']
            else:
                data = json.dumps(kwargs['data'])
        if 'params' not in kwargs and 'data' not in kwargs:
            if method in ('POST', 'PUT'):
                data = json.dumps(kwargs)
            else:
                params = kwargs
        headers = dict(self.other_headers)
        if newheaders:
            headers.update(newheaders)
        resp = None
        try:
            resp = yield from aiohttp.request(method, self.base_url + resource, params=params,
                                              data=data, headers=headers)
            if resp.status < 200 or resp.status >= 300:
                WARN('query %s returned %s' % ((self.base_url + resource, params, data, headers), resp.status))
                raise HttpClientException("HTTP %s: %s" % (resp.status, _http_responses.get(resp.status, '')))
            ret = yield from resp.content.read()
            if self.decode:
                ret = ret.decode()
        finally:
            if resp:
                try:
                    resp.close()
                except:
                    WARN('Could not close response object')
                    pass

        return ret

    @asyncio.coroutine
    def get(self, resource: str, rawdata, **kwargs) -> {str, bytes}:
        return self.initiate(resource, 'GET', rawdata=rawdata, **kwargs)

    @asyncio.coroutine
    def put(self, resource: str, rawdata=False, **kwargs) -> {bytes, str}:
        return self.initiate(resource, 'PUT', rawdata=rawdata, **kwargs)

    @asyncio.coroutine
    def post(self, resource: str, rawdata=False, headers=None, **kwargs) -> {bytes, str}:
        return self.initiate(resource, 'POST', rawdata=rawdata, newheaders=headers, **kwargs)

    def prefetch(self, *resources: [str]):
        def decorator(func):
            co_func = asyncio.coroutine(func)

            def worker(*args, **kwargs):
                futures = [self.get(resource, **kwargs) for resource in resources]
                print(futures)
                results = yield from asyncio.gather(*futures)
                args = list(args)
                args.extend(results)
                return (yield from co_func(*args))
            return asyncio.coroutine(worker)
        return decorator


if __name__ == "__main__":
    rpc = http_api("http://www.cs.umd.edu")
    loop = asyncio.get_event_loop()

    @rpc.prefetch('', '/~tdubois')
    def lengths(base, tdubois):
        print(len(base))
        print(len(tdubois))

    loop.run_until_complete(lengths())
