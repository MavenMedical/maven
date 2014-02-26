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

import asyncio
import maven_config as MC
import maven_logging as ML


## parameter names for the config file
CONFIG_READERTYPE = "readertype"
CONFIG_WRITERTYPE = "writertype"
CONFIG_PARSERTYPE = "parsertype"
CONFIG_READERNAME = "readername"
CONFIG_WRITERNAME = "writername"
CONFIG_PARSERNAME = "parsername"
CONFIG_WAKESECONDS = "periodic wake seconds"
CONFIGVALUE_THREADEDRABBIT = "threaded ampq"
CONFIGVALUE_ASYNCIOSOCKET = "asyncio socket"
CONFIGVALUE_EXPLICIT = "explicit"
CONFIGVALUE_IDENTITYPARSER = "identity"


class StreamProcessor():
    """ This is a basic stream processor class.  It implements several different stream protocols so that
    developers only have to worry about the logic of their programs, not how they communicate.

    It requires configuration parameters which tell it how to read and write.
    Its subclasses only have to implement read_raw or read_object, and write to write_raw or write_object.
    """

    ##########################
    # Fields to be overwritten
    ##########################
    
    @asyncio.coroutine
    def read_object(self, obj):
        """ This is the entry coroutine5B into the processing logic and must be overridden.
        When a complete message is received, it is decoded into an object, and this coroutine is scheduled
        Note that if a connection breaks, or at object does not parse correctly, this does not get called.

        Note, it must never block.  Any operation that might block must 'yield from' something instead.

        :param obj: an object decoded from the message
        """
        raise NotImplemented

    @asyncio.coroutine
    def timed_wake(self):
        """ This is the entry coroutine for periodic (not message driven) action.
        It will be schedule to wake up at a configurable time intervals.

        Note, it must never block.  Any operation that might block must 'yield from' something instead.
        """
        pass


    def __init__(self, configname):
        """ Initialize the StreamProcessor superclass, getting all of the IO and helper functions from 
        the MavenConfig structure
        :param configname: the name of the instance to pull config parameters
        """
        if not configname:
            raise MC.InvalidConfig("Stream parser needs a config entry")
        self.stream_processor_init = True
        try:
            self.configname = configname
            # make "listener" point to the correct listener
            if not configname in MC.MavenConfig:
                raise MC.InvalidConfig(configname+" is not in the MavenConfig map.")

            config = MC.MavenConfig[configname]
            try:
                readertype = config[CONFIG_READERTYPE]
                readername = config.get(CONFIG_READERNAME,None)
                writertype = config[CONFIG_WRITERTYPE]
                writername = config.get(CONFIG_WRITERNAME, None)
                parsertype = config.get(CONFIG_PARSERTYPE,CONFIGVALUE_IDENTITYPARSER)
                parsername = config.get(CONFIG_PARSERNAME,None)
            except KeyError:
                raise MC.InvalidConfig(configname + " did not have sufficient parameters.")

            try:
                self.parser_factory = lambda loop: lambda: _parser_map[parsertype](parsername, self.read_object, loop)
            except KeyError:
                raise MC.InvalidConfig("Invalid parser type for "+configname+": "+parsertype)

            try:
                self.reader = _reader_map[readertype](readername, self.parser_factory)
            except KeyError:
                raise MC.InvalidConfig("Invalid reader type for "+configname+": "+readertype)

            try:
                self.writer = _writer_map[writertype](writername)
            except KeyError:
                raise MC.InvalidConfig("Invalid writer type for "+configname+": "+writertype)

        except Exception as e:
            ML.ERROR("MC.InvalidConfig in "+self.configname)
            raise e
        

    ################################
    # Fields *not* to be overwritten
    ################################

    def schedule(self, loop):
        if not self.stream_processor_init:
            raise NotImplemented("The stream processor was not implemented correctly")
        self.loop=loop
        return self.reader.schedule(loop)

    def write_object(self, obj):
        """ write_object is used by the stream processing logic to send a message to the configured next step.
        :param obj: the object to write on the output channel
        """
        self.writer.write_object(obj)


class SocketReader():
    
    def __init__(self, configname, parser_factory_factory):
        self.parser_factory_factory = parser_factory_factory
        self.configname = configname
        if not configname in MC.MavenConfig:
            raise MC.InvalidConfig("some real error")
        config = MC.MavenConfig[configname]
        try:
            # get real parameters here
            self.host = config[CONFIG_READERHOST]
            self.port = config[CONFIG_READERPORT]
        except KeyError as e:
            raise MC.InvalidConfig("SocketReader "+configname+" missing parameter: "+e.args[0])
        
    def schedule(self, loop):
        self.loop = loop
        return loop.create_server(parser_factory_factory(loop), self.host, self.port)

class RabbitReader():
    def __init__(self, configname, parser_factory_factory):
        self.parser_factory_factory = parser_factory_factory
        self.configname = configname
        if not configname in MC.MavenConfig:
            raise MC.InvalidConfig("some real error")
        config = MC.MavenConfig[configname]
        try:
            # get real parameters here
            self.host = config[CONFIG_READERHOST]
            self.queue = config[CONFIG_READERQUEUE]
            self.exchange = config[CONFIG_READEREXCHANGE]
            self.incoming_key = config[CONFIG_READERKEY]
        except KeyError as e:
            raise MC.InvalidConfig("RabbitReader "+configname+" missing parameter: "+e.args[0])

    def schedule(self, loop):
        if not self.rabbit_listener_thread_pool:
            self.rabbit_listener_thread_pool = asyncio.ThreadPoolExecutor(max_workers=1)

        self.conn = amqp.Connection(self.host)
        self.chan = conn.channel()
        
        chan.queue_declare(queue=self.queue)  # incoming_work_queue
        chan.exchange_declare(exchange=self.exchange, type="direct")
        chan.queue_bind(queue=self.queue, exchange=self.exchange, 
                        routing_key=self.incoming_key)
        
        self.parser_factory = self.parser_factory_factory(loop)
        return loop.run_in_executor(self.rabbit_listener_thread_pool, chan.basic_consume, 
                                    queue=self.queue, no_ack=False, callback=self.data_received)

    def data_received(self, msg):
        parser = self.parser_factory()
        parser.connection_made(None)
        parser.data_received(msg)
        parser.eof_received()
        parser.connection_lost(None)


class ExplicitReader():
    
    def __init__(self, configname, parser_factory_factory):
        self.configname = configname
        self.parser_factory_factory = parser_factory_factory
    
    def schedule(self, loop):
        self.loop = loop
        self.parser_factory = self.parser_factory_factory(loop)
        return self

    def send_data(self,data):
        parser = self.parser_factory()
        parser.connection_made(None)
        parser.data_received(data)
        parser.eof_received()
        parser.connection_lost(None)
        tasks = asyncio.Task.all_tasks()
        if tasks:
            self.loop.run_until_complete(asyncio.wait(tasks))

import pickle 

class IdentityParser(asyncio.Protocol):
    def __init__(self, configname, read_fn, loop):
        self.configname = configname
        self.read_fn = read_fn
        self.loop = loop

    def connection_made(self, transport):
        pass

    def data_received(self, data):
        asyncio.Task(self.read_fn(data), loop=self.loop)
        #self.loop.call_soon_threadsafe(self.read_fn,data)

class SocketWriter():
    def __init__(self):
        raise NotImplemented

class RabbitWriter():
    def __init__(self):
        raise NotImplemented


class ExplicitWriter():
    def __init__(self, configname):
        self.configname = configname

    def write_object(self, obj):
        ML.PRINT(str(obj))


#  Mapping from reader types in the config file to the classes that handle them
_reader_map = {
    CONFIGVALUE_THREADEDRABBIT:RabbitReader,
    CONFIGVALUE_ASYNCIOSOCKET:SocketReader,
    CONFIGVALUE_EXPLICIT:ExplicitReader
}

#  Mapping from writer types in the config file to the classes that handle them
_writer_map = {
    CONFIGVALUE_THREADEDRABBIT:RabbitWriter,
    CONFIGVALUE_ASYNCIOSOCKET:SocketWriter,
    CONFIGVALUE_EXPLICIT:ExplicitWriter
}

#  Mapping from parser types in the config file to the classes that handle them
_parser_map = {
    CONFIGVALUE_IDENTITYPARSER:IdentityParser
}
