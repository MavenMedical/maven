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
import pickle 
import amqp
import traceback
import socket
import queue
import concurrent.futures
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
CONFIGVALUE_UNPICKLEPARSER = "unpickle"
CONFIGVALUE_UNPICKLESTREAMPARSER = "unpicklestream"

CONFIG_HOST = "host"
CONFIG_PORT = "port"
CONFIG_QUEUE = "queue"
CONFIG_EXCHANGE = "exchange"
CONFIG_KEY = "key"

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
        self.object_queue = queue.Queue()

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
                self.parser_factory = lambda loop: lambda: _parser_map[parsertype](parsername, self._read_object, self.object_queue.put, loop)
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
        #print("writing " +str(obj)+" to "+str(self.writer))
        self.writer.write_object(obj)

    def close(self):
        self.reader.close()
        self.writer.close()

    @asyncio.coroutine
    def _read_object(self):
        obj = self.object_queue.get_nowait()
        if obj:
            yield from self.read_object(obj)

#############################
# Network Readers
#############################
class SocketReader():
    
    def __init__(self, configname, parser_factory_factory):
        #print("in socket reader()")
        self.parser_factory_factory = parser_factory_factory
        self.configname = configname
        if not configname in MC.MavenConfig:
            raise MC.InvalidConfig("some real error")
        config = MC.MavenConfig[configname]
        try:
            # get real parameters here
            self.host = config.get(CONFIG_HOST,None)
            self.port = config[CONFIG_PORT]
        except KeyError as e:
            raise MC.InvalidConfig("SocketReader "+configname+" missing parameter: "+e.args[0])
        
    def schedule(self, loop):
        self.loop = loop
        self.server = asyncio.Task(loop.create_server(self.parser_factory_factory(loop), 
                                                      host=self.host, port=self.port), loop=loop)
        return self.server

    def close(self):
        self.server.cancel()
        

class RabbitReader():
    def __init__(self, configname, parser_factory_factory):
        self.parser_factory_factory = parser_factory_factory
        self.configname = configname
        self.rabbit_listener_thread_pool=None
        if not configname in MC.MavenConfig:
            raise MC.InvalidConfig("some real error")
        config = MC.MavenConfig[configname]
        try:
            # get real parameters here
            self.host = config[CONFIG_HOST]
            self.queue = config[CONFIG_QUEUE]
            self.exchange = config[CONFIG_EXCHANGE]
            self.incoming_key = config[CONFIG_KEY]
        except KeyError as e:
            raise MC.InvalidConfig("RabbitReader "+configname+" missing parameter: "+e.args[0])
        #ML.DEBUG("Created a RabbitReader")

    def schedule(self, loop):
        if not self.rabbit_listener_thread_pool:
            self.rabbit_listener_pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        #ML.DEBUG("created a thread pool: "+str(self.rabbit_listener_pool))
        
        self.conn = amqp.Connection(self.host)
        self.chan = self.conn.channel()
        
        self.chan.queue_declare(queue=self.queue)  # incoming_work_queue
        self.chan.exchange_declare(exchange=self.exchange, type="direct")
        self.chan.queue_bind(queue=self.queue, exchange=self.exchange, 
                        routing_key=self.incoming_key)
        
        self.parser_factory = self.parser_factory_factory(loop)
        self.chan.basic_consume(queue=self.queue, no_ack=False, 
                                callback=self.data_received)
            
        
        ret = loop.run_in_executor(self.rabbit_listener_pool,
                                   self._consume_wrapper)
        return ret

    def _consume_wrapper(self):
        while self.conn.is_alive:
            #ML.DEBUG("waiting on channel")
            self.chan.wait()

    def data_received(self, msg):
        #ML.DEBUG("received a message from rabbit: "+str(msg.body))
        try:
            parser = self.parser_factory()
            parser.connection_made(None)
            parser.data_received(msg.body)
            parser.eof_received()
            parser.connection_lost(None)
        except Exception as e:
            ML.DEBUG("CAUGHT EXCEPTION" + e.args[0])

    def close(self):
        #self.chan.basic_cancel(self.queue,nowait=True)
        #self.chan.close()
        try:
            self.conn.close()
        except IOError:
            pass
        self.rabbit_listener_pool.shutdown(wait=False)

class ExplicitReader():
    
    def __init__(self, configname, parser_factory_factory):
        self.configname = configname
        self.parser_factory_factory = parser_factory_factory
    
    def schedule(self, loop):
        self.loop = loop
        self.parser_factory = self.parser_factory_factory(loop)
        return self

    def send_data(self,data):
        #ML.DEBUG("got an explicit message:" + str(data))
        parser = self.parser_factory()
        parser.connection_made(None)
        parser.data_received(data)
        parser.eof_received()
        parser.connection_lost(None)
        tasks = asyncio.Task.all_tasks()
        if tasks and not self.loop.is_running():
            self.loop.run_until_complete(asyncio.wait(tasks))

    def close(self):
        pass


#############################
# message (stream) parsers
#############################
class MappingParser(asyncio.Protocol):
    def __init__(self, configname, read_fn, enqueue_fn, map_fn, loop):
        self.configname = configname
        self.read_fn = read_fn
        self.loop = loop
        self.map_fn = map_fn
        self.enqueue_fn = enqueue_fn

    def connection_made(self, transport):
        pass

    def data_received(self, data):
        #ML.DEBUG("parser got: " +str(data))
        self.enqueue_fn(self.map_fn(data))
        coro = self.read_fn()
        self.loop.call_soon_threadsafe(MappingParser.create_task,coro,self.loop)

    def create_task(coro, loop):
        asyncio.Task(coro,loop=loop)
        

class IdentityParser(MappingParser):
    def __init__(self, configname, read_fn, enqueue_fn, loop):
        MappingParser.__init__(self, configname, read_fn, enqueue_fn, lambda x: x, loop)

class UnPickleParser(MappingParser):
    def __init__(self, configname, read_fn, enqueue_fn, loop):
        MappingParser.__init__(self, configname, read_fn, enqueue_fn, pickle.loads, loop)

import pickletools
def pickle_stream(buf):
    ret = []
    try:
        while True:
            g=pickletools.genops(buf)
            for x in g:
                l=x[2]
            ret.append(pickle.loads(buf[:l+1]))
            buf = buf[(l+1):]
    finally:
        return (ret, buf)    

class UnPickleStreamParser(MappingParser):
    def __init__(self, configname, read_fn, enqueue_fn, loop):
        MappingParser.__init__(self, configname, read_fn, enqueue_fn, lambda x: x, loop)
        self.buf = b''

    def data_received(self,data):
        try:
            self.buf = self.buf + data
            s=len(self.buf)
            ret, self.buf = pickle_stream(self.buf)
            lr=0
            for obj in ret:
                self.enqueue_fn(self.map_fn(obj))
                lr += 1
                coro = self.read_fn()
                self.loop.call_soon_threadsafe(MappingParser.create_task,coro,self.loop)
            #print("%s in data_recv, buf was %d, is %d, %d objects" % (str(data), s, len(self.buf), lr))
        except Exception:
            print("EXCEPTION")
            traceback.print_exc()

        

#############################
# Network Writers
#############################

class SocketWriter():
    def __init__(self, configname):
        self.configname = configname
        if not configname in MC.MavenConfig:
            raise MC.InvalidConfig("some real error")
        config = MC.MavenConfig[configname]
        try:
            # get real parameters here
            self.host = config[CONFIG_HOST]
            self.port = config[CONFIG_PORT]
        except KeyError as e:
            raise MC.InvalidConfig("SocketReader "+configname+" missing parameter: "+e.args[0])        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.socket.setblocking(False)
        
    def write_object(self, obj):
        self.socket.sendall(obj)

    def close(self):
        self.socket.close()

class RabbitWriter():
    def __init__(self, configname):
        self.configname = configname
        if not configname in MC.MavenConfig:
            raise MC.InvalidConfig("some real error")
        config = MC.MavenConfig[configname]
        try:
            # get real parameters here
            self.host = config[CONFIG_HOST]
            self.exchange = config[CONFIG_EXCHANGE]
            self.incoming_key = config[CONFIG_KEY]
        except KeyError as e:
            raise MC.InvalidConfig("SocketReader "+configname+" missing parameter: "+e.args[0])
        try:
            self.conn = amqp.Connection(self.host)
            self.chan = self.conn.channel()
        except:
            traceback.print_exc()
            raise

    def write_object(self, obj):
        #ML.DEBUG("rabbit writing obj: "+str(obj))
        message = amqp.Message(pickle.dumps(obj))
        self.chan.basic_publish(message, exchange=self.exchange, 
                                routing_key=self.incoming_key)

    def close(self):
        self.chan.close()
        self.conn.close()

class ExplicitWriter():
    def __init__(self, configname):
        self.configname = configname
        self.count=0

    def write_object(self, obj):
        ML.PRINT(str(obj))
        #self.count += 1
        #if self.count % 1000 == 0:
        #    print("received %d" % self.count)

    def close(self):
        pass

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
    CONFIGVALUE_IDENTITYPARSER:IdentityParser,
    CONFIGVALUE_UNPICKLEPARSER:UnPickleParser,
    CONFIGVALUE_UNPICKLESTREAMPARSER:UnPickleStreamParser,
}
