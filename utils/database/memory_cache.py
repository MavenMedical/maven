##############################################################################
#  Copyright (c) 2014 - Maven Medical
#
#
#  Description: This provides the unit tests for the memory_cache
#
#  Author: Tom DuBois
#  Provides: A working asyncio memory cache
#  This isn't particularly critical, but it can be used for lessening a load
#  on a database or API server.  Essentially you can wrap this around a function
#  and it will cache results from that function for a period of time, so that
#  subsequent calls with the same key do not need to actually call the function
#  again.
##############################################################################
import asyncio
import time
from collections import defaultdict, OrderedDict
from functools import wraps


def firstarg(argskwargs):
    """
    Makes the key the first argument passed to the function
    :param argskwargs: all args and keyword args passed in
    """
    return argskwargs[0][0]


def firstarg_instance_method(argskwargs):
    """
    Makes the key the first (non-self) argument passed to the function.
    Useful for member functions
    :param argskwargs: all args and keyword args passed in
    """
    return argskwargs[0][1]


def keyarg(keykey):
    """
    Selects a key from the kwargs (does not work with implicit keyword args)
    :param argskwargs: all args and keyword args passed in
    :param keykey: the keyword from which to select the key
    """
    return lambda argskwargs: argskwargs[1][keykey]


def allargs(argskwargs):
    """
    Makes the entire argument set the key
    :param argskwargs: all args and keyword args passed in
    """
    return (argskwargs[0], tuple(sorted(argskwargs[1].items())))


class MemoryCache():
    """
    Many database lookups come from a read-only, or very rarely changing part of the database.
    This class provides a caching layer for these tables, so that we can reduce the load on the
    db machine as well as latency.
    MemoryCache can handle multiple tables, each with different update functionality at once.
    Each table is identified by a unique object (usually a string).  Each table can have at most
    one update function, and any number of lookup functions (including ones which insert and
    lookup)
    """

    def __init__(self, timeout=None):
        self.data = defaultdict(OrderedDict)
        self.cancelled = False
        self.size_limits = defaultdict(lambda: [])
        self.timeout = timeout  # if timeout, values stored as (access time, value)

    def set_max_entries(self, entries, cache_name=None):
        """ sets the maximum number of entries per cache
        :param cache_name: the name of the cache whose limit to set or none to set them all
        """
        if not entries:
            entries = []
        if cache_name:
            self.size_limits[cache_name] = entries
        else:
            self.size_limits = defaultdict(lambda: entries)

    @asyncio.coroutine
    def _loop(self, fn, cache_name, period_seconds, delay_seconds, retry_on_error=False,
              message_fn=None):
        if delay_seconds:
            yield from asyncio.sleep(delay_seconds)
        try:
            temp = yield from fn()
            if self.timeout:
                t = time.time()
                temp = {k: (t, v) for k, v in temp.items()}
            self.data[cache_name] = OrderedDict(temp)
        except:
            message_fn and message_fn()
            if not retry_on_error:
                return None
        while period_seconds and not self.cancelled:
            yield from asyncio.sleep(period_seconds)
            if not self.cancelled:
                try:
                    temp = yield from fn()
                    if self.timeout:
                        t = time.time()
                        temp = {k: (t, v) for k, v in temp.items()}
                    self.data[cache_name] = OrderedDict(temp)
                except:
                    message_fn and message_fn()
                    if not retry_on_error:
                        return None

    def cache_update(self, cache_name, period_seconds=None, delay_seconds=None,
                     retry_on_error=False, message_fn=None):
        """ Decorator to schedule an update function for a cache
        Apply @<memory_cache instance>.cache_update(...) before a coroutine
        function to populate the cache
        This function will be called once (or repeatedly if a period is set)
        to pre-populate the cache
        If the cache name already exists, it will immediately throw an exception instead.
        The decorated function must return a map from keys to values
        :param cache_name: A string (or any object) with which to identify the cache.
                           This string must be passed to the lookup function's decorator as well.
                           While not strictly necessary, we assume it is an error if two update
                           functions are created with the same name.
        :param period_seconds: how often to call update_function
        :param delay_seconds: how long to wait before the initial call to update_function
                              (mostly useful so as not to start many big update_functions
                              at once during the initial schedule)
        :param retry_on_error: if the function throws an error, do we keep retrying, or exit
        :param message_fn: if the function throws an error, call this function
        """
        if cache_name in self.data:
            raise KeyError(cache_name + " already in this cache")

        def decorator(func):
            co_func = asyncio.coroutine(func)

            def scheduler(*args, **kwargs):
                asyncio.Task(self._loop(lambda: co_func(*args, **kwargs),
                                        cache_name, period_seconds, delay_seconds,
                                        retry_on_error, message_fn))
            return wraps(func)(scheduler)
        return decorator

    def _get_value(self, data, key):
        if key in data:
            val = data[key]
            if type(val) is asyncio.Future:
                return True, val
            else:
                if self.timeout:
                    if time.time() > self.timeout + val[0]:  # a timeout
                        data.pop(key)
                        return False, None
                    else:
                        return True, val[1]
                else:
                    return True, val
        else:
            return False, None

    def cache_lookup(self, cache_name, lookup_on_none=False, key_function=firstarg):
        """ Decorator to lookup a key for a cache, or fetch it if it's not there
        Apply @<memory_cache instance>.cache_lookup(...) to a coroutine that takes a
        key and finds the value
        This function will only be called if the key isn't already in the cache
        The function's first parameter must be the key to lookup.
        If the cache should contain the entire key space, this function can simply
        raise an exception.
        :param cache_name: which "table" to look up in, returned from add_cache
        :param lookup_on_none: If the value None is cached, should we treat it as a miss.
        :return: the value for the key in the named cache
        """
        def decorator(func):
            co_func = asyncio.coroutine(func)

            def lookup(*args, **kwargs):
                data = self.data[cache_name]
                limit = self.size_limits[cache_name]
                key = key_function((args, kwargs))
                indict, val = self._get_value(data, key)
                if indict:
                    if type(val) is asyncio.Future:
                        yield from asyncio.wait([val])
                        data.move_to_end(key)
                        return val.result()
                    else:
                        data.move_to_end(key)
                        return val
                lookup_future = asyncio.Future()
                lookup_coroutine = co_func(*args, **kwargs)
                data[key] = lookup_future
                ret = yield from lookup_coroutine
                if self.timeout:
                    data[key] = (time.time(), ret)
                else:
                    data[key] = ret
                lookup_future.set_result(ret)
                if limit and len(data) > limit:
                    data.popitem(last=False)
                return ret
            return asyncio.coroutine(wraps(func)(lookup))
        return decorator

    def cache_lookup_multi(self, cache_name, lookup_on_none=False):
        """ Decorator to lookup a list of keys for a cache, or fetch any that are not there
        Apply @<memory_cache instance>.cache_lookup_multi(...) to a coroutine that takes
        an iterable of keys and returns a dict from keys to values
        This function will only be called if their are keys already in the cache
        The function's first parameter is an iterable of key to lookup.

        NOTE - if a request for key foo is flying, this will issue a new request instead
        of waiting for the existing one to complete

        :param cache_name: which "table" to look up in, returned from add_cache
        :param lookup_on_none: If the value None is cached, should we treat it as a miss.
        :return: a dict mapping each key to its value
        """
        def decorator(func):
            co_func = asyncio.coroutine(func)

            def lookup(keys, *args, **kwargs):
                data = self.data[cache_name]
                limit = self.size_limits[cache_name]
                ret = {}
                needed = set()
                futures = set()
                for key in keys:
                    indict, val = self._get_value(data, key)
                    if indict:
                        data.move_to_end(key)
                        if type(val) is asyncio.Future:
                            futures.add((key, val))
                        else:
                            ret[key] = val
                    else:
                        needed.add(key)
                results = {}
                if needed:
                    results = yield from co_func(needed, *args, **kwargs)
                if futures:
                    yield from asyncio.gather(fut[1] for fut in futures)
                    results.update([(k, v.result()) for k, v in futures])
                if results:
                    ret.update(results)
                    if self.timeout:
                        t = time.time()
                        data.update([(k, (t, v)) for k, v in results])
                    else:
                        data.update(results)
                    if limit:
                        for x in range(limit, len(data)):
                            data.popitem(last=False)
                return ret
            return asyncio.coroutine(wraps(func)(lookup))
        return decorator

    def cache_explicit_insert(self, cache_name, key, value):
        """ Explicitly insert a key/value pair into a cache
        :param cache_name: the cache_name (similar to a database table)
        :param key: the key
        :param value: the value
        """
        data = self.data[cache_name]
        data[key] = value
        limit = self.size_limits[cache_name]
        if limit and len(data) > limit:
            data.popitem(last=False)

    def cache_explicit_update(self, cache_name, pairs):
        """ Explicitly insert a dict of key/value pairs into a cache
        :param cache_name: the cache_name (similar to a database table)
        :param pairs: the key/value pairs
        """
        data = self.data[cache_name]
        limit = self.size_limits[cache_name]
        data.update(pairs)
        if limit:
            for x in range(limit, len(data)):
                data.popitem(last=False)

    def cache_clear(self, cache_name):
        """ Clear a named cache
        :param cache_name: the cache_name (similar to a database table)
        """
        self.data[cache_name].clear()

    def cancel(self):
        """ Cancels updating for all caches
        """
        self.cancelled = True

cache = MemoryCache()
