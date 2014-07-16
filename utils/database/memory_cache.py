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

class MemoryCache():
    """
    Many database lookups come from a read-only, or very rarely changing part of the database.
    This class provides a caching layer for these tables, so that we can reduce the load on the
    db machine as well as latency.
    MemoryCache can handle multiple tables, each with different update functionality at once.
    Different "tables" are registered with add_cache which returns an id.  lookup requires this
    id to know what "table" to look for.
    """
    
    def __init__(self):
        self.data = []
        self.next_type_id = 0
        self.handlers = []
        self.periods = []
        self.delays = []
        self.fallback_handlers = []
        self.cancelled = False

    @asyncio.coroutine
    def loop(self, fn, ind, period_seconds, delay_seconds):
        if delay_seconds:
            yield from asyncio.sleep(delay_seconds)
        self.data[ind] = yield from fn()
        while period_seconds and not self.cancelled:
            yield from asyncio.sleep(period_seconds)
            if not self.cancelled:
                self.data[ind] = yield from fn()

    def add_cache(self, update_function, fallback_function, period_seconds, delay_seconds):
        """ Register a "table" with the memory cache.
        :return: an id for this table.  use this id as the index in lookup
        :param update_function: this function is called initially, and periodically afterwards
                                think of it as syncing with the database.  It should return a map
                                of lookup key to lookup data.  If this function is slow, it should frequently
                                yield so as not to block other server functionality.
        :param fallback_function: The update_function does not have to load everything.  If a key isn't
                                  already cached, fallback_function will take the key, insert the key into the map
                                  and return the value.  If can query the database, or just throw a keyerror
        :param period_seconds: how often to call update_function
        :param delay_seconds: how long to wait before the initial call to update_function
                              (mostly useful so as not to start many big update_functions at once during
                              the initial schedule)
        """
        self.data.append({})
        self.handlers.append(update_function)
        self.periods.append(period_seconds)
        self.delays.append(delay_seconds)
        self.fallback_handlers.append(fallback_function)
        i=len(self.data)-1
        self.looptask = asyncio.Task(self.loop(update_function, i, period_seconds, delay_seconds))

        return i
        
    @asyncio.coroutine
    def lookup(self, index, key):
        """ lookup a key in the registered "table"
        :param index: which "table" to look up in, returned from add_cache
        :param key: the key to look up (likely corresponds to a unique, indexed field in a database
        :return: the value for the key in the indexed table
        """
        data = self.data[index]
        if key in data:
            return data[key]
        else:
            ret = yield from self.fallback_handlers[index](key)
            data[key] = ret
            return ret

    def cancel(self):
        self.cancelled = True
