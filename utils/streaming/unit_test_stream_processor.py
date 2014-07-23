##############################################################################
#  Copyright (c) 2014 - Maven Medical
#
#
#  Description: This is a stream subclass to test the stream class
#               It reads objects, appends them to a list, and writes the list
#               This tests read_object and write_object, which implicitly test
#               read_raw and write_raw.  
#               It does not test the network connectivity.
#
#  Author: Tom DuBois
#  Assumes: Nothing
#  Side Effects: None
#  Last Modified:
##############################################################################

import asyncio

import maven_config as MC
import utils.streaming.stream_processor as SP
import maven_logging as ML

explicitteststreamname = 'test stream explicit'
rabbittestproducername = 'test producer rabbit'
rabbittestconsumername = 'test consumer rabbit'
trippletestproducername = 'test producer socket'
trippletestconsumername = 'test consumer socket'
trippletestmiddlename = 'test middle socket'

MavenConfig = {
    explicitteststreamname:
    {
        SP.CONFIG_READERTYPE: SP.CONFIGVALUE_EXPLICIT,
        SP.CONFIG_READERNAME: explicitteststreamname+".Test Reader",
        SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_EXPLICIT,
        SP.CONFIG_WRITERNAME: explicitteststreamname+".Test Writer",
    },
    rabbittestproducername:
    {
        SP.CONFIG_READERTYPE: SP.CONFIGVALUE_EXPLICIT,
        SP.CONFIG_READERNAME: rabbittestproducername+".Test Reader",
        SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
        SP.CONFIG_WRITERNAME: rabbittestproducername+".Test Writer",
    },
    rabbittestproducername+".Test Writer":
    {
        SP.CONFIG_HOST:'localhost',
        SP.CONFIG_QUEUE:'incoming_work_queue_sp_test',
        SP.CONFIG_EXCHANGE:'maven_exchange',
        SP.CONFIG_KEY:'incoming'
    },
    rabbittestconsumername:
    {
        SP.CONFIG_READERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
        SP.CONFIG_READERNAME: rabbittestconsumername+".Test Reader",
        SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_EXPLICIT,
        SP.CONFIG_WRITERNAME: rabbittestconsumername+".Test Writer",
        SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_UNPICKLEPARSER,
    },
    rabbittestconsumername+".Test Reader":
    {
        SP.CONFIG_HOST:'localhost',
        SP.CONFIG_QUEUE:'incoming_work_queue_sp_test',
        SP.CONFIG_EXCHANGE:'maven_exchange',
        SP.CONFIG_KEY:'incoming'
    },
    trippletestproducername:
    {
        SP.CONFIG_READERTYPE: SP.CONFIGVALUE_EXPLICIT,
        SP.CONFIG_READERNAME: trippletestproducername+".Test Reader",
        SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
        SP.CONFIG_WRITERNAME: trippletestproducername+".Test Writer",
    },
    trippletestproducername+".Test Writer":
    {
        SP.CONFIG_HOST:'localhost',
        SP.CONFIG_QUEUE:'incoming_work_queue_sp_test',
        SP.CONFIG_EXCHANGE:'maven_exchange',
        SP.CONFIG_KEY:'incoming'
    },

    trippletestmiddlename:
    {
        SP.CONFIG_READERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
        SP.CONFIG_READERNAME: trippletestmiddlename+".Test Reader",
        SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOCLIENTSOCKET,
        SP.CONFIG_WRITERNAME: trippletestmiddlename+".Test Writer",
    },
    trippletestmiddlename+".Test Reader":
    {
        SP.CONFIG_HOST:'localhost',
        SP.CONFIG_QUEUE:'incoming_work_queue_sp_test',
        SP.CONFIG_EXCHANGE:'maven_exchange',
        SP.CONFIG_KEY:'incoming'
    },
    trippletestmiddlename+".Test Writer":
    {
        SP.CONFIG_HOST:'127.0.0.1',
        SP.CONFIG_PORT:12345
    },
    trippletestconsumername:
    {
        SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSERVERSOCKET,
        SP.CONFIG_READERNAME: trippletestconsumername+".Test Reader",
        SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_EXPLICIT,
        SP.CONFIG_WRITERNAME: trippletestconsumername+".Test Writer",
        SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_UNPICKLESTREAMPARSER,
    },
    trippletestconsumername+".Test Reader":
    {
        #SP.CONFIG_HOST:'127.0.0.1',
        SP.CONFIG_PORT:12345
    },


}

MC.MavenConfig = MavenConfig

class ConcatenateStreamProcessor(SP.StreamProcessor):
    
    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)
        self.master_list = ['', '', '', '', '']
        
    @asyncio.coroutine
    def read_object(self, obj, key):
        self.master_list.append(obj)
        self.master_list.pop(0)
        self.write_object(self.master_list)

class IdentityStreamProcessor(SP.StreamProcessor):
    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)

    @asyncio.coroutine
    def read_object(self, obj, key):
        self.write_object(obj)

def single_test():
    sp = ConcatenateStreamProcessor(explicitteststreamname)
    loop = asyncio.get_event_loop()
    sender = sp.schedule(loop)
    
    sender.send_data('foo')
    sender.send_data('bar')
    for x in range(10):
        sender.send_data(x)
    loop.run_until_complete(asyncio.sleep(.01))
        #loop.run_until_complete(asyncio.wait(asyncio.Task.all_tasks(loop)))

def rabbit_test():
    sp_producer = ConcatenateStreamProcessor(rabbittestproducername)
    sp_consumer = IdentityStreamProcessor(rabbittestconsumername)

    loop = asyncio.get_event_loop()
    sender = sp_producer.schedule(loop)
    receiver = sp_consumer.schedule(loop)

    sender.send_data('foo')
    sender.send_data('bar')
    for x in range(20):
        for y in range(1000):
            sender.send_data(x)
        print("sent %d" % (1000*(x+1)))
        loop.run_until_complete(asyncio.sleep(.03))
        
    while asyncio.Task.all_tasks(loop):
        loop.run_until_complete(asyncio.wait(asyncio.Task.all_tasks(loop)))
                
    sp_producer.close()
    sp_consumer.close()

def tripple_test():
    loop = asyncio.get_event_loop()
    sp_consumer = IdentityStreamProcessor(trippletestconsumername)
    sp_middle = IdentityStreamProcessor(trippletestmiddlename)
    sp_producer = ConcatenateStreamProcessor(trippletestproducername)

    sp_consumer.schedule(loop)
    loop.run_until_complete(asyncio.sleep(.1))
    sp_middle.schedule(loop)
    sender = sp_producer.schedule(loop)
    #loop.run_until_complete(asyncio.sleep(.1))

    sender.send_data('foo')
    sender.send_data('bar')
    for x in range(10):
        #for y in range(1000):
        sender.send_data(x)
        #print("sent %d" % (1000*(x+1)))
    loop.run_until_complete(asyncio.sleep(.1))
    tasks = asyncio.Task.all_tasks(loop)
    if any([not t.done() for t in tasks]):
        loop.run_until_complete(asyncio.sleep(.2))
      

    sp_producer.close()
    sp_middle.close()
    sp_consumer.close()

#single_test()
tripple_test()
if __name__ == '__main__':
    print(ML.get_results())
