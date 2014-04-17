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


name = 'test producer socket'

MavenConfig = {
    name:
    {
        SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSERVERSOCKET,
        SP.CONFIG_READERNAME: name+".Test Reader",
        SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_EXPLICIT,
        SP.CONFIG_WRITERNAME: name+".Test Writer"
    },
    name+".Test Reader":
    {
        SP.CONFIG_HOST:'127.0.0.1',
        SP.CONFIG_PORT:12345,
    },
    name+".Test Writer":
    {
    },
}

MC.MavenConfig = MavenConfig

class RedirectStreamProcessor(SP.StreamProcessor):
    
    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)

    @asyncio.coroutine
    def read_object(self, obj, key):
        l = obj.split(b',')
        yield from self.write_object(l[0], l[1].decode(), int(l[2]))

class ConcatenateStreamProcessor2(SP.StreamProcessor):
    
    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)

    @asyncio.coroutine
    def read_object(self, obj, key):
        print([self.configname, obj, key])
        self.write_object(bytes(str(obj[0]),'utf-8'), obj[1])

def single_test():
    sp1 = RedirectStreamProcessor(name)
    loop = asyncio.get_event_loop()
    sender = sp1.schedule(loop)
    
    #sender.send_data('foo')
    #sender.send_data('bar')
    #for x in range(10):
    #    sender.send_data(x)
    #loop.run_until_complete(asyncio.sleep(.01))
        #loop.run_until_complete(asyncio.wait(asyncio.Task.all_tasks(loop)))
    loop.run_forever()

single_test()
