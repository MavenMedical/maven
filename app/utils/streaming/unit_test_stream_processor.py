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

teststreamname = 'test stream'
MavenConfig = {
    teststreamname:
    {
        SP.CONFIG_READERTYPE: SP.CONFIGVALUE_EXPLICIT,
        SP.CONFIG_READERNAME: "Test Reader",
        SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_EXPLICIT,
        SP.CONFIG_WRITERNAME: "Test Writer",
    }
}

MC.MavenConfig = MavenConfig

class ConcatenateStreamProcessor(SP.StreamProcessor):
    
    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)
        self.master_list = ['', '', '', '', '']
        
    @asyncio.coroutine
    def read_object(self, obj):
        self.master_list.append(obj)
        self.master_list.pop(0)
        self.write_object(self.master_list)

sp = ConcatenateStreamProcessor(teststreamname)
sender = sp.schedule(asyncio.get_event_loop())

sender.send_data('foo')
sender.send_data('bar')
for x in range(10):
    sender.send_data(x)
