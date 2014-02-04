##############################################################################
#  Copyright (c) 2014 - Maven Medical
#
#
#  Description: This is a stream subclass to test the stream class
#               It reads objects, appends them to a list, and writes the list
#
#  Author: Tom DuBois
#  Assumes: Nothing for now, eventually that Rabbit will send a message
#           with a specific format
#  Side Effects: None
#  Last Modified:
##############################################################################

import pickle
import stream_processor as SP

class ConcatenateStreamProcessor(SP.StreamProcessor):
    
    def __init__(self,MavenConfig,configname):
        SP.StreamProcessor.__init__(self,MavenConfig,configname)
        self.master_list=['','','','','']
        
    def read_object(self,obj):
        self.master_list.append(obj)
        self.master_list.pop(0)
        self.write_object(self.master_list)


def MavenConfig(name,description):
    return 'Testing'

sp = ConcatenateStreamProcessor(MavenConfig,'name doesn\'t matter')

def unpickle_writer(obj):
    print(pickle.loads(obj))

sp.write_raw = unpickle_writer

sp.read_object('foo')
sp.read_object('bar')
