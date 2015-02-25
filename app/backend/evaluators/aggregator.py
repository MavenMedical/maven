#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:   This aggregator.py contains the class(es) required to aggregate
#               multiple messages into a single, concise message so that clinicians
#               are not bombarded by constant notification messages.
#
#************************
#ASSUMES:
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-123
#*************************************************************************

import collections
import time
import asyncio
import utils.streaming.stream_processor as SP
import maven_config as MC
import maven_logging as ML
import app.backend.module_rule_engine.order_response_object as ORO

CONFIG_RESPONSE_HOLD_TIME = "response_hold_time"
CONFIG_EXPIRATION_MEMORY = "expiration_memory"


class Aggregator(SP.StreamProcessor):

    # configure this StreamProcessor
    # the super class takes care of the connectivity
    # the base class reads in local config parameters
    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)
        self.queue = collections.OrderedDict()  # queue/dict to hold pending responses
        self.expired = collections.OrderedDict()  # (limited memory) queue to avoid double-sending messages
        try:
            self.delay = MC.MavenConfig[configname][CONFIG_RESPONSE_HOLD_TIME]  # how long to hold messages waiting
            self.max_expired_memory = MC.MavenConfig[configname][CONFIG_EXPIRATION_MEMORY]  # how many old messages to hold
        except KeyError:
            raise MC.InvalidConfig("something")

    # read_object is triggered whenever a new message is delivered
    @asyncio.coroutine
    def read_object(self, obj, _):
        if not obj.oid in self.expired:  # only respond if we haven't sent out a message for this order
            if not obj.oid in self.queue:
                # if this if the first message for this id, add to the queue and set the timeout
                obj.hold_time = time.time()+self.delay
                self.queue[obj.oid] = [obj]
            else:
                # there are already responses for this id in the queue, append them, but don't change the timeout
                self.queue[obj.oid].append(obj)

    # timed_wake triggers whenever a response's delay might have expired, and it's time to send what we have
    @asyncio.coroutine
    def timed_wake(self):
        try:
            [key, responses] = self.queue.popitem(False)  # pop the oldest response off of the list
            while responses[0].hold_time <= time.time():  # while the oldest response is ready to go
                # create a single response string from the list of responses, sorted by priority and joined with \n
                responses = sorted(responses, key=lambda x: x.priority())
                self.write_object([key, '\n'.join([rsp.text() for rsp in responses])])
                # add this item to the expired queue, and evict something if necessary
                self.expired[key] = key
                if len(self.expired) > self.max_expired_memory:
                    self.expired.popitem(False)
                [key, responses] = self.queue.popitem(False)  # dequeue the next oldest element
            # this element is not ready to go yet, put it back at the head of the queue, and reset the wake up timer
            self.queue[key] = responses
            self.queue.move_to_end(key, False)
        except KeyError:  # if the queue is empty, it will throw a KeyError
            pass

count = 0

def run_aggregator():
    ra_test = "response aggregator test"

    MavenConfig = {
        ra_test:
        {
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_EXPLICIT,
            SP.CONFIG_READERNAME: ra_test+".Test Reader",
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_EXPLICIT,
            SP.CONFIG_WRITERNAME: ra_test+".Test Writer",
            CONFIG_RESPONSE_HOLD_TIME: .01,
            CONFIG_EXPIRATION_MEMORY: 4,
            SP.CONFIG_WAKESECONDS: .01,
        }
    }

    MC.MavenConfig = MavenConfig
    aggregator = Aggregator(ra_test)
    loop = asyncio.get_event_loop()
    aggregator.schedule(loop)
    
    def task(coro):
        asyncio.Task(coro, loop=loop)
        
    def wake(sleep_time, s):
        global count
        count += 1
        time.sleep(sleep_time)
        ML.PRINT("wake #%d, %s" % (count, s))
        loop.run_until_complete(asyncio.sleep(.03))

    task(aggregator.read_object(ORO.OrderResponseObject(1, 1, "(1,1)", None), None))
    wake(0, 'nothing ready yet')
    wake(.02, 'message ready to send')
    task(aggregator.read_object(ORO.OrderResponseObject(2, 2, "(2,2)", None), None))
    wake(0, 'nothing ready')
    task(aggregator.read_object(ORO.OrderResponseObject(2, 4, "(2,4)", None), None))
    wake(0, 'nothing ready')
    task(aggregator.read_object(ORO.OrderResponseObject(2, 3, "(2,3)", None), None))
    wake(.02, "key 2 ready too send")
    task(aggregator.read_object(ORO.OrderResponseObject(1, 2, "(1,2)", None), None))
    wake(.02, "key 1 rejected because it was already sent")
    task(aggregator.read_object(ORO.OrderResponseObject(3, 3, "(3,3)", None), None))
    task(aggregator.read_object(ORO.OrderResponseObject(4, 3, "(4,3)", None), None))
    task(aggregator.read_object(ORO.OrderResponseObject(5, 3, "(5,3)", None), None))
    task(aggregator.read_object(ORO.OrderResponseObject(6, 3, "(6,3)", None), None))
    wake(.02, "keys 3-6 sending at once")
    task(aggregator.read_object(ORO.OrderResponseObject(1, 3, "(1,3)", None), None))
    wake(.02, "key 1 getting through again because it's expiration expired")

if __name__ == '__main__':
    run_aggregator()
