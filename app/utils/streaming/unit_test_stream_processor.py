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

import pickle
import maven_config as MC
import app.utils.streaming.stream_processor as SP

teststreamname = 'test stream'
MavenConfig = {
    teststreamname:
    {
        'readertype': 'Testing',
        'readerconfig': 'Testing',
        'writertype': 'Testing',
        'writerconfig': 'Testing'
    }
}

MC.MavenConfig = MavenConfig


class ConcatenateStreamProcessor(SP.StreamProcessor):
    
    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)
        self.master_list = ['', '', '', '', '']
        
    def read_object(self, obj):
        self.master_list.append(obj)
        self.master_list.pop(0)
        self.write_object(self.master_list)

sp = ConcatenateStreamProcessor(teststreamname)

if __name__ == '__main__':
    def unpickle_writer(obj):
        print(pickle.loads(obj))
else:
    output_buffer = ''

    def unpickle_writer(obj):
        global output_buffer
        output_buffer += str(pickle.loads(obj))+"\n"
        
sp.write_raw = unpickle_writer

sp.read_object('foo')
sp.read_object('bar')
for x in range(10):
    sp.read_object(x)

try:
    result = output_buffer.strip()
except NameError:
    pass
