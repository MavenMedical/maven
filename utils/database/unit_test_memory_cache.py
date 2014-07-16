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
import maven_logging as ML
import time

@asyncio.coroutine
def default(x):
    yield from asyncio.sleep(.02)
    return x+3
    
@asyncio.coroutine
def update():
    ML.PRINT('updating')
    return {1:2}

mc = MemoryCache()
ind1=mc.add_cache(update, default, .2, 0)
loop = asyncio.get_event_loop()


@asyncio.coroutine
def queries(prefix, ind, sleep_time, initial_sleep):
    if initial_sleep:
        yield from asyncio.sleep(initial_sleep)
    for i in range(9):
        r = yield from mc.lookup(ind, i%5)
#        PRINT(str(int((time.time() % 1) * 10000)) + " " +prefix +": " + str(i%10) + " -> "+ str(r))
        ML.PRINT(prefix +": " + str(i%5) + " -> "+ str(r))
        yield from asyncio.sleep(sleep_time)

import traceback
t1=queries(str(ind1), ind1, .02, .01)
loop.run_until_complete(t1)
mc.cancel()
for task in asyncio.Task.all_tasks(loop):
    if not task.done():
        loop.run_until_complete(task)
    
if __name__ == '__main__':
    print(ML.get_results())
