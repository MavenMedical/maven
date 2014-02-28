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
import app.utils.streaming.stream_processor as SP

explicitteststreamname = 'test stream explicit'
rabbittestproducername = 'test producer rabbit'
rabbittestconsumername = 'test consumer rabbit'
trippletestproducername = 'test producer socket'
trippletestconsumername = 'test consumer socket'
trippletestmiddlename = 'test middle socket'

MavenConfig = {
    explicitteststreamname:
    {
        SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSERVERSOCKET,
        SP.CONFIG_READERNAME: explicitteststreamname+".Test Reader",
        SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETREPLY,
        SP.CONFIG_WRITERNAME: explicitteststreamname+".Test Writer",
        SP.CONFIG_WRITERDYNAMICKEY:1
    },
    explicitteststreamname+".Test Reader":
    {
        SP.CONFIG_HOST:'127.0.0.1',
        SP.CONFIG_PORT:12345,
    },
    explicitteststreamname+".Test Writer":
    {
        SP.CONFIG_HOST:'127.0.0.1',
        SP.CONFIG_PORT:12346,
        SP.CONFIG_WRITERKEY:1,
    },
}

MC.MavenConfig = MavenConfig
import pickle

class ConcatenateStreamProcessor(SP.StreamProcessor):
    
    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)
        self.master_list = ['', '', '', '', '']

    @asyncio.coroutine
    def read_object(self, obj, key):
        self.master_list.append(obj)
        self.master_list.pop(0)
        self.write_object(bytes(str(self.master_list),'utf-8'), key)

def single_test():
    sp = ConcatenateStreamProcessor(explicitteststreamname)
    loop = asyncio.get_event_loop()
    sender = sp.schedule(loop)
    
    #sender.send_data('foo')
    #sender.send_data('bar')
    #for x in range(10):
    #    sender.send_data(x)
    #loop.run_until_complete(asyncio.sleep(.01))
        #loop.run_until_complete(asyncio.wait(asyncio.Task.all_tasks(loop)))
    loop.run_forever()

single_test()
