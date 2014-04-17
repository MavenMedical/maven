##############################################################################
#  Copyright (c) 2014 - Maven Medical
#
#
#  Description: Tests the rules engine aggregator
#               
#  Author: Tom DuBois
#  Assumes: 
#  Side Effects: None
#  Last Modified: 
##############################################################################

#import app.rule_engine.order_response_object as RE
import time

import asyncio

import app.backend.module_rule_engine.order_response_object as ORO
import utils.streaming.stream_processor as SP
import app.backend.module_rule_engine.response_aggregator as RA
import maven_config as MC
from maven_logging import PRINT


#class ResponseAggregator(SP.StreamProcessor):
#    def __init__(self, configname):
#    def read_object(self, obj):
#    def timed_wake(self):

# the configuration for this test has to include both StreamProcessor's configs
# and also ResponseAggregator's configs
ra_test = "response aggregator test"
MavenConfig = {
    ra_test:
    {
        SP.CONFIG_READERTYPE: SP.CONFIGVALUE_EXPLICIT,
        SP.CONFIG_READERNAME: ra_test+".Test Reader",
        SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_EXPLICIT,
        SP.CONFIG_WRITERNAME: ra_test+".Test Writer",
        RA.CONFIG_RESPONSE_HOLD_TIME: .01,
        RA.CONFIG_EXPIRATION_MEMORY: 4,
        SP.CONFIG_WAKESECONDS: .01,
    }
}
MC.MavenConfig = MavenConfig



count = 0
loop=asyncio.get_event_loop()

def wake(sleep_time, s):
    global count
    count += 1
    time.sleep(sleep_time)
    PRINT("wake #%d, %s" % (count, s))
    loop.run_until_complete(asyncio.sleep(.03))

def task(coro):
    asyncio.Task(coro,loop=loop)

ra = RA.ResponseAggregator(ra_test)
ra.schedule(loop)
task(ra.read_object(ORO.OrderResponseObject(1, 1, "(1,1)"), None))
wake(0, 'nothing ready yet')
wake(.02, 'message ready to send')
task(ra.read_object(ORO.OrderResponseObject(2, 2, "(2,2)"),None)
wake(0, 'nothing ready')
task(ra.read_object(ORO.OrderResponseObject(2, 4, "(2,4)"),None)
wake(0, 'nothing ready')
task(ra.read_object(ORO.OrderResponseObject(2, 3, "(2,3)"),None)
wake(.02, "key 2 ready too send")
task(ra.read_object(ORO.OrderResponseObject(1, 2, "(1,2)"),None)
wake(.02, "key 1 rejected because it was already sent")
task(ra.read_object(ORO.OrderResponseObject(3, 3, "(3,3)"),None)
task(ra.read_object(ORO.OrderResponseObject(4, 3, "(4,3)"),None)
task(ra.read_object(ORO.OrderResponseObject(5, 3, "(5,3)"),None)
task(ra.read_object(ORO.OrderResponseObject(6, 3, "(6,3)"),None)
wake(.02, "keys 3-6 sending at once")
task(ra.read_object(ORO.OrderResponseObject(1, 3, "(1,3)"),None)
wake(.02, "key 1 getting through again because it's expiration expired")

