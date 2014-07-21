##############################################################################
#  Copyright (c) 2014 - Maven Medical
#
#
#  Description: This provides the unit tests for the memory_cache
#               
#  Author: Tom DuBois
#  Assumes: A working asyncio memory cache
#  Side Effects: None
##############################################################################
import asyncio
from collections import defaultdict, OrderedDict

class MemoryCache():
    """
    Many database lookups come from a read-only, or very rarely changing part of the database.
    This class provides a caching layer for these tables, so that we can reduce the load on the
    db machine as well as latency.
    MemoryCache can handle multiple tables, each with different update functionality at once.
    Each table is identified by a unique object (usually a string).  Each table can have at most
    one update function, and any number of lookup functions (including ones which insert and lookup)
    """
    
    def __init__(self):
        self.data = defaultdict(OrderedDict)
        self.cancelled = False
        self.size_limits = defaultdict(lambda: [])

    def set_max_entries(entries, cache_name=None):
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
    def _loop(self, fn, cache_name, period_seconds, delay_seconds, retry_on_error=False, message_fn=None):
        if delay_seconds:
            yield from asyncio.sleep(delay_seconds)
        try:
            temp = yield from fn()
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
                    self.data[cache_name] = OrderedDict(temp)
                except:
                    message_fn and message_fn()
                    if not retry_on_error:
                        return None

    def cache_update(self, cache_name, period_seconds=None, delay_seconds=None, retry_on_error=False,message_fn=None):
        """ Decorator to schedule an update function for a cache
        Apply @<memory_cache instance>.cache_update(...) before a coroutine function to populate the cache
        This function will be called once (or repeatedly if a period is set) to pre-populate the cache
        If the cache name already exists, it will immediately throw an exception instead.
        The decorated function must return a map from keys to values
        :param cache_name: A string (or any object) with which to identify the cache.
                           This string must be passed to the lookup function's decorator as well.
                           While not strictly necessary, we assume it is an error if two update
                           functions are created with the same name.
        :param period_seconds: how often to call update_function
        :param delay_seconds: how long to wait before the initial call to update_function
                              (mostly useful so as not to start many big update_functions at once during
                              the initial schedule)
        :param retry_on_error: if the function throws an error, do we keep retrying, or exit
        :param message_fn: if the function throws an error, call this function
        """
        if cache_name in self.data:
            raise KeyError(cache_name + " already in this cache")
        def decorator(func):
            co_func = asyncio.coroutine(func)
            def scheduler(*args, **kwargs):
                asyncio.Task(self._loop(lambda: co_func(*args, **kwargs), 
                                        cache_name, period_seconds, delay_seconds, retry_on_error, message_fn))
            return scheduler
        return decorator
                
    def cache_lookup(self, cache_name, lookup_on_none=False):
        """ Decorator to lookup a key for a cache, or fetch it if it's not there
        Apply @<memory_cache instance>.cache_lookup(...) to a coroutine that takes a key and finds the value
        This function will only be called if the key isn't already in the cache
        The function's first parameter must be the key to lookup.
        If the cache should contain the entire key space, this function can simply raise an exception.
        :param cache_name: which "table" to look up in, returned from add_cache
        :param lookup_on_none: If the value None is cached, should we treat it as a miss.
        :return: the value for the key in the named cache
        """
        def decorator(func):
            co_func = asyncio.coroutine(func)
            def lookup(key, *args, **kwargs):
                data = self.data[cache_name]
                limit = self.size_limits[cache_name]
                if key in data:
                    data.move_to_end(key)
                    val = data[key]
                    if val or not lookup_on_none:
                        return val
                ret = yield from co_func(key, *args, **kwargs)
                data[key] = ret
                if limit and len(data)>limit:
                    data.popitem(last=False)
                return ret
            return asyncio.coroutine(lookup)
        return decorator
        
    def cache_lookup_multi(self, cache_name, lookup_on_none=False):
        """ Decorator to lookup a list of keys for a cache, or fetch any that are not there
        Apply @<memory_cache instance>.cache_lookup_multi(...) to a coroutine that takes
        an iterable of keys and returns a dict from keys to values
        This function will only be called if their are keys already in the cache
        The function's first parameter is an iterable of key to lookup.
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
                needed=set()
                for key in keys:
                    if key in data:
                        data.move_to_end(key)
                        val = data[key]
                        if val or not lookup_on_none:
                            ret[key]=val
                    if not key in ret:
                        needed.add(key)
                if needed:
                    result = yield from co_func(needed, *args, **kwargs)
                    ret.update(result)
                    data.update(result)
                    if limit:
                        for x in range(limit, len(data)):
                            data.popitem(last=False)
                return ret
            return asyncio.coroutine(lookup)
        return decorator
    
    def cache_explicit_insert(self, cache_name, key, value):
        """ Explicitly insert a key/value pair into a cache
        :param cache_name: the cache_name (similar to a database table)
        :param key: the key
        :param value: the value
        """
        data = self.data[cache_name]
        data[key]=value
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
