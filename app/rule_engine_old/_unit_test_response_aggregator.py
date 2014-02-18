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
import app.rule_engine.order_response_object as ORO
import app.utils.streaming.stream_processor as SP
import app.rule_engine.response_aggregator as RA
import time
import maven_config as MC
import pickle

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
        SP.readertype_param: "Testing",
        SP.writertype_param: "Testing",
        RA.response_hold_time_param: .01,
        RA.expiration_memory_param: 4
    }
}
MC.MavenConfig = MavenConfig

if __name__ == '__main__':
    def unpickle_writer(obj):
        print(pickle.loads(obj))
else:
    output_buffer = ''

    def unpickle_writer(obj):
        global output_buffer
        output_buffer += str(pickle.loads(obj))+"\n"

count = 0
def wake(sleep_time,s):
    global count, output_buffer
    count = count + 1
    time.sleep(sleep_time)
    if __name__ == '__main__':
        print("wake #%d, %s" % (count, s))
    else:
        output_buffer += "wake #" + str(count) + ", " + s + "\n"
    ra.timed_wake()

ra = RA.ResponseAggregator(ra_test)
ra.write_raw = unpickle_writer
ra.read_object(ORO.OrderResponseObject(1, 1, "(1,1)"))
wake(0,'nothing ready yet')
wake(.02,'message ready to send')
ra.read_object(ORO.OrderResponseObject(2, 2, "(2,2)"))
wake(0, 'nothing ready')
ra.read_object(ORO.OrderResponseObject(2, 4, "(2,4)"))
wake(0, 'nothing ready')
ra.read_object(ORO.OrderResponseObject(2, 3, "(2,3)"))
wake(.02, "key 2 ready too send")
ra.read_object(ORO.OrderResponseObject(1, 2, "(1,2)"))
wake(.02, "key 1 rejected because it was already sent")
ra.read_object(ORO.OrderResponseObject(3, 3, "(3,3)"))
ra.read_object(ORO.OrderResponseObject(4, 3, "(4,3)"))
ra.read_object(ORO.OrderResponseObject(5, 3, "(5,3)"))
ra.read_object(ORO.OrderResponseObject(6, 3, "(6,3)"))
wake(.02, "keys 3-6 sending at once")
ra.read_object(ORO.OrderResponseObject(1, 3, "(1,3)"))
wake(.02, "key 1 getting through again because it's expiration expired")

result = output_buffer.strip()
