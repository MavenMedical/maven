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


rabbittestproducername = 'test producer rabbit'
rabbittestconsumername = 'test consumer rabbit'
trippletestproducername = 'test producer socket'
trippletestconsumername = 'test consumer socket'
trippletestmiddlename = 'test middle socket'


explicitteststreamname1 = 'test stream explicit1'
explicitteststreamname2 = 'test stream explicit2'


MavenConfig = {
    explicitteststreamname1:
    {
        SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSERVERSOCKET,
        SP.CONFIG_READERNAME: explicitteststreamname1+".Test Reader",
        SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOCLIENTSOCKET,
        SP.CONFIG_WRITERNAME: explicitteststreamname1+".Test Writer",
        SP.CONFIG_WRITERDYNAMICKEY:1
    },
    explicitteststreamname1+".Test Reader":
    {
        SP.CONFIG_HOST:'127.0.0.1',
        SP.CONFIG_PORT:12345,
    },
    explicitteststreamname1+".Test Writer":
    {
        SP.CONFIG_HOST:'127.0.0.1',
        SP.CONFIG_PORT:12346,
    },
    explicitteststreamname2:
    {
        SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSERVERSOCKET,
        SP.CONFIG_READERNAME: explicitteststreamname2+".Test Reader",
        SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETREPLY,
        SP.CONFIG_WRITERNAME: explicitteststreamname2+".Test Writer",
        SP.CONFIG_WRITERDYNAMICKEY:1,
        SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_UNPICKLESTREAMPARSER,
        SP.CONFIG_PARSERNAME: explicitteststreamname2+".Parser",
    },
    explicitteststreamname2+".Test Reader":
    {
        SP.CONFIG_HOST:'127.0.0.1',
        SP.CONFIG_PORT:12346,
    },
    explicitteststreamname2+".Test Writer":
    {
        SP.CONFIG_WRITERKEY:1,
    },
}

MC.MavenConfig = MavenConfig
import pickle

class ConcatenateStreamProcessor1(SP.StreamProcessor):
    
    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)
        self.master_list = ['', '', '', '', '']

    @asyncio.coroutine
    def read_object(self, obj, key):
        self.master_list.append(obj)
        self.master_list.pop(0)
        print([self.configname, self.master_list, key])
        self.write_object(pickle.dumps([self.master_list,key]))

class ConcatenateStreamProcessor2(SP.StreamProcessor):
    
    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)

    @asyncio.coroutine
    def read_object(self, obj, key):
        print([self.configname, obj, key])
        self.write_object(bytes(str(obj[0]),'utf-8'), obj[1])

def single_test():
    sp1 = ConcatenateStreamProcessor1(explicitteststreamname1)
    sp2 = ConcatenateStreamProcessor2(explicitteststreamname2)
    loop = asyncio.get_event_loop()
    sp2.schedule(loop)
    sender = sp1.schedule(loop)
    
    #sender.send_data('foo')
    #sender.send_data('bar')
    #for x in range(10):
    #    sender.send_data(x)
    #loop.run_until_complete(asyncio.sleep(.01))
        #loop.run_until_complete(asyncio.wait(asyncio.Task.all_tasks(loop)))
    loop.run_forever()

single_test()
