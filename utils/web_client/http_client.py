import aiohttp
import asyncio
import json

from maven_config import MavenConfig

CONFIG_BASEURL = 'base url'
CONFIG_OTHERHEADERS = 'other headers'

class http_api():
    """ This class encapsulates all of the common details for contacting a
    REST or other remote procedure call - like API on a single remote server.

    The client can specifically request the results at a URL, or it can apply
    a decorator and get results passed in as arguments once they are fetched.

    It is designed to be either subclassed (a function get_data() calls get("data"))
    or as a decorator

    It also handles timeouts, caching, and other common functionality.
    """

    def __init__(self, configname:str, other_headers:{str:str}=None, 
                 decode:bool=True):
        """ Create a new instance of the remote query object using the shared parameters
        :param configname: the name of this module in the configuration file.
                           It must contain the base url
        :param other_headers=None: optional parameter for additional headers (api key)
        :param decode: True if the output should be returned as a string, false means bytes
        """
        self.config = MavenConfig[configname]
        self.base_url = self.config[CONFIG_BASEURL]
        self.other_headers = self.config.get(CONFIG_OTHERHEADERS,{})
        if other_headers:
            self.other_headers.update(other_headers)
        self.decode = decode

    @asyncio.coroutine
    def initiate(self, resource:str, method:['GET', 'POST', 'PUT'], **kwargs) -> {bytes, str}:
        """ make a connection to a remote server and wait for a response
        :param resource: A string to append to the base url
        :param method: one of the standard http methods
        :param kwargs: data to send.  If it contains a key 'data', it is dumped as json
                       and put in the body.  If it contains a key 'params', they are 
                       added to the url.  If neither, then the entire kwargs are added to
                       the body (if post/put) or url (if get)
        """
        data = None
        params = None
        if 'params' in kwargs:
            params = kwargs['params']
        if 'data' in kwargs:
            data = json.dumps(kwargs['data'])
        if 'params' not in kwargs and 'data' not in kwargs:
            if method in ('POST', 'PUT'):
                data = json.dumps(kwargs)
            else:
                params = kwargs
        resp = yield from aiohttp.request(method, self.base_url + resource, params=params,
                                          data=data, headers=self.other_headers)
        ret = yield from resp.content.read()
        if self.decode:
            ret = ret.decode()
        return ret

    @asyncio.coroutine
    def get(self, resource:str, **kwargs) -> {str, bytes}:
        return self.initiate(resource, 'GET', **kwargs)

    @asyncio.coroutine
    def put(self, resource:str, **kwargs) -> {bytes, str}:
        return self.initiate(resource, 'PUT', **kwargs)

    @asyncio.coroutine
    def post(self, resource:str, **kwargs) -> {bytes, str}:
        return self.initiate(resource, 'POST', **kwargs)

    def prefetch(self, *resources:[str]):
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
