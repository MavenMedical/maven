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
from utils.database.memory_cache import MemoryCache
from maven_logging import PRINT
import time

@asyncio.coroutine
def default(x):
    yield from asyncio.sleep(.02)
    return x+3
    
@asyncio.coroutine
def update():
    PRINT('updating')
    return {1:2}

mc = MemoryCache()
ind1=mc.add_cache(update, default, .09, 0)
loop = asyncio.get_event_loop()


@asyncio.coroutine
def queries(prefix, ind, sleep_time, initial_sleep):
    if initial_sleep:
        yield from asyncio.sleep(initial_sleep)
    for i in range(9):
        r = yield from mc.lookup(ind, i%5)
#        PRINT(str(int((time.time() % 1) * 10000)) + " " +prefix +": " + str(i%10) + " -> "+ str(r))
        PRINT(prefix +": " + str(i%5) + " -> "+ str(r))
        yield from asyncio.sleep(sleep_time)
        
t1=asyncio.Task(queries(str(ind1), ind1, .01, .003))
loop.run_until_complete(t1)
for task in asyncio.Task.all_tasks(loop):
    task.cancel()
