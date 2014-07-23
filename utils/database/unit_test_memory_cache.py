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
from utils.database.memory_cache import cache
import os
os.environ['MAVEN_TESTING']=''
import maven_logging as ML
import time

class Timer():
    def __init__(self):
        self.basetime = time.time()

    def elapsed(self):
        return str(round(10*(time.time()-self.basetime)))

timer = Timer()
                
@cache.cache_update("name", period_seconds=.5)
def update_fun():
    ML.PRINT("updating "+timer.elapsed())
    return {1:2, 3:4}

update_fun()

@cache.cache_lookup("name")
def lookup(key):
    ML.PRINT("looking up %d at %s" %(key, timer.elapsed()))
    return key+2

@cache.cache_lookup_multi("name")
def lookupmulti(keys):
    ML.PRINT("looking up %s at %s" %(str(keys), timer.elapsed()))
    return {k:k+3 for k in keys}

@asyncio.coroutine
def PRINT(co_fn):
    ret = yield from co_fn
    ML.PRINT("returned "+str(ret)+" at "+timer.elapsed())

@asyncio.coroutine
def run():
    yield from asyncio.sleep(.05)
    for i in range(8):
        yield from PRINT(lookup(1))
        yield from PRINT(lookup(2))
        yield from PRINT(lookupmulti([1,2,3,4]))
        yield from asyncio.sleep(.1)
    cache.cancel()
    yield from asyncio.sleep(.1)
        
asyncio.get_event_loop().run_until_complete(run())
if __name__ == '__main__':
    print(ML.get_results())
        
