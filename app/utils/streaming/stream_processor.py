##############################################################################
#  Copyright (c) 2014 - Maven Medical
#
#
#  Description: This is a generic stream module base class.
#               
#  Author: Tom DuBois
#  Assumes: Nothing for now, eventually that Rabbit will send a message 
#           with a specific format
#  Side Effects: None
#  Last Modified: 
##############################################################################

import pickle

class StreamProcessor():

    ##########################
    # Fields to be overwritten
    ##########################
    
    # One or the other of these should be overwritten
    # When a message is received, it calls readRaw(), which by default deserialized it and calls readObject
    # Overwriting readRaw prevents the call to readObject
    # Call readRaw with a raw bytestream to simulate input to this module
    def read_raw(self, raw):
        self.read_object(self,pickle.loads(raw))
        return
    def read_object(self, obj):
        return
    

    ################################
    # Fields *not* to be overwritten
    ################################

    # write_raw and write_object are to be called (by a reader typically) and will write to the configured object
    # write_raw is assigned in the __init__ function, write_object is here
    def write_object(self,obj):
        bytes=pickle.dumps(obj)
        self.write_raw(bytes)
    
    # Check the config file to determine what we are listening on/writing to
    def __init__(self, configname):
        global MavenConfig
        try:
            self.configname = configname
            # make "listener" point to the correct listener
            if(not configname in MavenConfig):
                raise Exception(configname+" is not in the MavenConfig map.")
            else:
                try:
                    readertype = MavenConfig[configname]['readertype']
                    readerconfig = MavenConfig[configname]['readerconfig']
                    writertype = MavenConfig[configname]['writertype']
                    writerconfig = MavenConfig[configname]['writerconfig']
                except Exception:
                    raise Exception(configname +" did not have sufficient parameters.")    
            if(readertype == 'RabbitMQ'):
                self.listener=self.rabbit_listener
                # read other config from readerconfig and setup
            elif(readertype == 'NGINX'):
                self.listener=self.nginx_writer
                # read other config from readerconfig and setup
            elif(readertype != "Testing"):
                raise Exception("Invalid reader type for "+configname+": "+readertype)
                # the testing reader does nothing, but raise and exception if readertype is invalid
            if(writertype == 'RabbitMQ'):
                self.write_raw=self.rabbit_writer
                # read other config from writerconfig and setup
            elif(writertype == 'NGINX'):
                self.write_raw=self.nginx_writer
                # read other config from writerconfig and setup
            elif(writertype == 'Testing'):
                self.write_raw=print
                # The default writer is print, however the parent testing class can overwrite with a callback
            else:
                raise Exception("Invalid writer type for "+configname+": "+writertype)
        except Exception as e:
            print("Exception in "+self.configname)
            raise e
        

    def rabbit_listener(self,blah):
        # listens to rabbitMQ messages and calls readRaw
        self.read_raw(blah)
    
    def nginx_listener(self,blah):
        # listens to messages from nginx
        self.read_raw(blah)

    def rabbit_writer(self,bytes):
        # writes to rabbitMQ
        return

    def nginx_writer(self,bytes):
        #writes to nginx
        return

