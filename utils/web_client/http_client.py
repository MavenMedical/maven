import aiohttp
import asyncio
import json


class http_api():
    """ This class encapsulates all of the common details for contacting a
    REST or other remote procedure call - like API on a single remote server.

    The client can specifically request the results at a URL, or it can apply
    a decorator and get results passed in as arguments once they are fetched.

    It is designed to be either subclassed (a function get_data() calls get("data"))
    or as a decorator

    It also handles timeouts, caching, and other common functionality.
    """

    def __init__(self, url, other_headers=[], decode=True, postprocess=None):
        """ Create a new instance of the remote query object using the shared parameters
        :param url: the shared url base for all remote methods
        :param other_headers=[]: optional parameter for additional headers (api key)
        """
        self.base_url = url
        self.other_headers = other_headers
        self.decode = decode

    @asyncio.coroutine
    def initiate(self, resource, method, **kwargs):
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
    def get(self, resource, **kwargs):
        return self.initiate(resource, 'GET', **kwargs)

    @asyncio.coroutine
    def put(self, resource, **kwargs):
        return self.initiate(resource, 'PUT', **kwargs)

    @asyncio.coroutine
    def post(self, resource, **kwargs):
        return self.initiate(resource, 'POST', **kwargs)

    def prefetch(self, *resources):
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
