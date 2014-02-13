##############################################################################
#  Copyright (c) 2014 - Maven Medical
#
#
#  Description: Aggregates order response objects to return a single block of text
#               Multiple rules engines will receive each order object, and they
#               will respond separately and at different times.
#               We need to aggregate these, and send them out as a single unit.
#               We can wait a (configurable) little while,
#               
#  Author: Tom DuBois
#  Assumes: 
#  Side Effects: None
#  Last Modified: 
##############################################################################

#import app.rule_engine.order_response_object as RE
import app.utils.streaming.stream_processor as SP
import collections
import time
import maven_config as MC

response_hold_time_param = "response_hold_time"
expiration_memory_param = "expiration_memory"


class ResponseAggregator(SP.StreamProcessor):

    # configure this StreamProcessor
    # the super class takes care of the connectivity
    # the base class reads in local config parameters
    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)
        self.queue = collections.OrderedDict()  # queue/dict to hold pending responses
        self.expired = collections.OrderedDict()  # (limited memory) queue to avoid double-sending messages
        self.delay = MC.MavenConfig[configname][response_hold_time_param]  # how long to hold messages waiting
        self.max_expired_memory = MC.MavenConfig[configname][expiration_memory_param]  # how many old messages to hold

    # read_object is triggered whenever a new message is delivered
    def read_object(self, obj):
        if not obj.oid in self.expired:  # only respond if we haven't sent out a message for this order
            if not obj.oid in self.queue:
                # if this if the first message for this id, add to the queue and set the timeout
                obj.hold_time = time.time()+self.delay
                self.queue[obj.oid] = [obj]
                self.max_sleep(self.delay)
            else:
                # there are already responses for this id in the queue, append them, but don't change the timeout
                self.queue[obj.oid].append(obj)

    # timed_wake triggers whenever a response's delay might have expired, and it's time to send what we have
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
            self.max_sleep(responses[0].hold_time-time.time())
        except KeyError:  # if the queue is empty, it will throw a KeyError
            pass