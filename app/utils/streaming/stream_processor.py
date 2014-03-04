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
CONFIGVALUE_ASYNCIOSERVERSOCKET = "asyncio server socket"
CONFIGVALUE_ASYNCIOCLIENTSOCKET = "asyncio client socket"
CONFIGVALUE_ASYNCIOSOCKETREPLY = "asyncio server socket reply"
CONFIGVALUE_ASYNCIOSOCKETQUERY = "asyncio client socket query"
CONFIGVALUE_EXPLICIT = "explicit"
CONFIGVALUE_IDENTITYPARSER = "identity"
CONFIGVALUE_UNPICKLEPARSER = "unpickle"
CONFIGVALUE_UNPICKLESTREAMPARSER = "unpicklestream"

CONFIG_HOST = "host"
CONFIG_PORT = "port"
CONFIG_WRITERKEY = "writer key"
CONFIG_WRITERDYNAMICKEY = "dynamic writer key"
CONFIG_QUEUE = "queue"
CONFIG_EXCHANGE = "exchange"
CONFIG_KEY = "key"

global _global_writers

_global_writers = {}

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
    def read_object(self, obj, key):
        """ This is the entry coroutine into the processing logic and must be overridden.
        When a complete message is received, it is decoded into an object, and this coroutine is scheduled
        Note that if a connection breaks, or at object does not parse correctly, this does not get called.

        Note, it must never block.  Any operation that might block must 'yield from' something instead.

        :param obj: an object decoded from the message
        :param key: used when a reader and writer are paired as the way to send a later response back
                    to the correct initial sender.  It may be process-specific.

                    Example, a listening socket server accepts a connection and receives some data.
                    The data object is passed along with the key associated with this socket.
                    After a potentially large number of intermediate steps, we need to send a reply
                    back on the same socket.  Call write_object(obj, key) to send it back on the correct
                    socket.

                    If this is not your behavior, ignore this param.
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
        the MavenConfig structure.  It creates the StreamProcess, but does not yet make network connections.

        :param configname: the name of the instance to pull config parameters
        """
        
        # This section reads the config file and sets up network connections
        if not configname:
            raise MC.InvalidConfig("Stream parser needs a config entry")
        try:
            self.configname = configname
            if not configname in MC.MavenConfig:
                raise MC.InvalidConfig(configname+" is not in the MavenConfig map.")
            config = MC.MavenConfig[configname]

            try:
                readertype = config.get(CONFIG_READERTYPE, None)
                readername = config.get(CONFIG_READERNAME,None)
                writertype = config[CONFIG_WRITERTYPE]
                writernames = config.get(CONFIG_WRITERNAME, None)
                try:
                    self.dynamic_writer = config[CONFIG_WRITERDYNAMICKEY]
                    self.has_dynamic_writer = True
                except KeyError:
                    self.has_dynamic_writer = False
                if not type(writernames) is list:
                    writernames=[writernames]
                parsertype = config.get(CONFIG_PARSERTYPE,CONFIGVALUE_IDENTITYPARSER)
                parsername = config.get(CONFIG_PARSERNAME,None)
                self.wakeup = config.get(CONFIG_WAKESECONDS, None)
            except KeyError:
                raise MC.InvalidConfig(configname + " did not have sufficient parameters.")

            # We have the names and types of the sub-modules, now instantiate them
            try:
                # We need to create a parser factory that knows what the loop is, but we don't have
                # the loop yet.  The factory_factory takes a loop, and creates a parser_factory
                # suitable for use by asyncio.create_server: a function with no arguments that 
                # creates a new parser object.
                # The parser's arguments are it's name (for config stuff if any, a read coroutine function 
                # to schedule a new read, a function to put a new read coroutine instance on the loop
                self.parser_factory_factory = \
                    lambda loop: lambda: _parser_map[parsertype](parsername, self.read_object, 
                                                                 loop, (self._register_writer,
                                                                        self._unregister_writer))

            except KeyError:
                raise MC.InvalidConfig("Invalid parser type for "+configname+": "+parsertype)

            # Create the reader, passing it it's name and the parser_factory_factory which takes
            # messages, buffers and chunks them if needed, and parses them into objects
            try:
                self.reader = _reader_map[readertype](readername, self.parser_factory_factory)
            except KeyError:
                raise MC.InvalidConfig("Invalid reader type for "+configname+": "+readertype)

            # Create the writer(s)
            try:
                self.writers = {}
                for writername in writernames:
                    w = _writer_map[writertype](writername)
                    self.writers[w.writer_key] = w
                    if self.has_dynamic_writer and w.writer_key == self.dynamic_writer:
                        _global_writers[w.writer_key] = w
            except KeyError:
                raise MC.InvalidConfig("Invalid writer type for "+configname+": "+writertype)

            if self.wakeup:
                try:
                    self.wakeup = float(self.wakeup)
                except ValueError:
                    raise MC.InvalidConfig("Wakup time must be int, is "+ str(self.wakeup))

        except Exception as e:
            ML.ERROR("MC.InvalidConfig in "+self.configname)
            raise e
        
    ################################
    # Fields NOT to be overwritten
    # OK, overwrite them, but make
    # to call the StreamProcessor
    # versions too
    ################################

    @asyncio.coroutine
    def wake_up_alarm(self):
        while not self.closed:
            yield from asyncio.sleep(self.wakeup)
            yield from self.timed_wake()

    

    def schedule(self, loop):
        """ schedule starts the networking, registering queues, creating sockets, etc

        :param loop: the main event loop
        """
        self.loop=loop
        self.closed=False
        if self.wakeup:
            self.next_sleep = None
            asyncio.Task(self.wake_up_alarm(),loop=loop)
        for w in self.writers.values():
            w.schedule(loop)
        return self.reader.schedule(loop)

    def write_object(self, obj, writer_key = None):
        """ write_object is used by the stream processing logic to send a message to the configured next step.
        :param obj: the object to write on the output channel
        """
        try:
            w = self.writers[writer_key]
        except KeyError:
            try:
                w = _global_writers[writer_key]
            except KeyError:
                w = self.writers[None]
        w.write_object(obj)

    def _register_writer(self, transport):
        if self.has_dynamic_writer:
            global _global_writers
            w=_global_writers[self.dynamic_writer]._register_new(transport)
            if w:
                _global_writers[w.writer_key]=w
                return w.writer_key
        return None

    def _unregister_writer(self, key):
        if self.has_dynamic_writer:
            global _global_writers
            _global_writers.pop(key).close()

    def close(self):
        """ closes the stream processor's reader and writer
        """
        self.closed = True
        self.reader.close()
        for w in self.writers.values():
            w.close()

#############################
# Network Readers
#############################

class _SocketServerReader():
    ### Starts a server to read data from a socket and pass it to the stream processor 

    def __init__(self, configname, parser_factory_factory):
        # store initialization arguments, and look up the config map
        self.parser_factory_factory = parser_factory_factory
        self.configname = configname
        if not configname in MC.MavenConfig:
            raise MC.InvalidConfig("some real error")
        config = MC.MavenConfig[configname]
        # get real parameters here, throwing errors if necessary ones are missing
        try:
            self.host = config.get(CONFIG_HOST,None)
            self.port = config[CONFIG_PORT]
        except KeyError as e:
            raise MC.InvalidConfig("SocketReader "+configname+" missing parameter: "+e.args[0])
        
    def schedule(self, loop):
        self.loop = loop
        # start a listening server which creates a new instance of the parser for each connection
        self.server = asyncio.Task(loop.create_server(self.parser_factory_factory(loop), 
                                                      host=self.host, port=self.port), loop=loop)
        loop.run_until_complete(asyncio.sleep(.01))
        return self.server

    def close(self):
        self.server.cancel()

class _SocketQueryReader():        
    def __init__(self, configname, parser_factory_factory):
        self.parser_factory_factory = parser_factory_factory
        self.configname = configname
        if not configname in MC.MavenConfig:
            raise MC.InvalidConfig("some real error")
        config = MC.MavenConfig[configname]
        # get real parameters here, throwing errors if necessary ones are missing
        try:
            self.host = config.get(CONFIG_HOST,None)
            self.port = config[CONFIG_PORT]
        except KeyError as e:
            raise MC.InvalidConfig("SocketReader "+configname+" missing parameter: "+e.args[0])

    def schedule(self, loop):
        self.loop = loop
        # start a listening server which creates a new instance of the parser for each connection
        self.server = asyncio.Task(loop.create_connection(self.parser_factory_factory(loop), 
                                                      host=self.host, port=self.port), loop=loop)
        loop.run_until_complete(asyncio.sleep(.01))
        return self.server

    def close(self):
        self.server.cancel()
        

class _RabbitReader():
    ### Starts a server to read data from RabbitMQ and pass it to the stream processor

    def __init__(self, configname, parser_factory_factory):

        # store initialization arguments, and look up the config map
        self.parser_factory_factory = parser_factory_factory
        self.configname = configname
        self.rabbit_listener_thread_pool=None
        if not configname in MC.MavenConfig:
            raise MC.InvalidConfig("some real error")
        config = MC.MavenConfig[configname]

        # get real parameters here, throwing errors if necessary ones are missing
        try:
            self.host = config[CONFIG_HOST]
            self.queue = config[CONFIG_QUEUE]
            self.exchange = config[CONFIG_EXCHANGE]
            self.incoming_key = config[CONFIG_KEY]
        except KeyError as e:
            raise MC.InvalidConfig("RabbitReader "+configname+" missing parameter: "+e.args[0])

    def schedule(self, loop):
        # set up the connections to rabbit
        self.conn = amqp.Connection(self.host)
        self.chan = self.conn.channel()
        
        self.chan.queue_declare(queue=self.queue)  # incoming_work_queue
        self.chan.exchange_declare(exchange=self.exchange, type="direct")
        self.chan.queue_bind(queue=self.queue, exchange=self.exchange, 
                        routing_key=self.incoming_key)
        
        self.parser_factory = self.parser_factory_factory(loop)
        self.chan.basic_consume(queue=self.queue, no_ack=False, 
                                callback=self.data_received)
            
        # create a new thread which will call chan.wait() to receive messages from rabbit
        if not self.rabbit_listener_thread_pool:
            self.rabbit_listener_pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        ret = loop.run_in_executor(self.rabbit_listener_pool,
                                   self._consume_wrapper)
        return ret

    def _consume_wrapper(self):
        # receive and process messages from rabbit.
        # NOT in the main thread
        while self.conn.is_alive:
            self.chan.wait()

    def data_received(self, msg):
        # This will be called during _consume_wrapper's call to chan.wait()
        # NOT in the main thread
        # This also means that the parser will not be in the main thread, 
        # which is why the parser schedules reads using call_soon_threadsafe
        try:
            # each rabbit message is a single, self contained object
            # rabbit already puts packets together into a single buffer and
            # puts multiple items each in their own message, so no need to buffer
            parser = self.parser_factory()
            parser.connection_made(None)
            parser.data_received(msg.body)
            parser.eof_received()
            parser.connection_lost(None)
        except Exception as e:
            ML.DEBUG("CAUGHT EXCEPTION" + e.args[0])

    def close(self):
        try:
            # rabbit in the other thread has some odd behavior when closing (chan.wait() is executing)
            # for now this seems to work
            self.conn.close()
        except IOError:
            pass
        self.rabbit_listener_pool.shutdown(wait=False)

class _ExplicitReader():
    ### No server is started.  Instead of reading data from the network,
    ### this class takes its input from a function call.
    ### Useful mostly for testing purposes
    
    def __init__(self, configname, parser_factory_factory):
        self.configname = configname
        self.parser_factory_factory = parser_factory_factory
    
    def schedule(self, loop):
        self.loop = loop
        self.parser_factory = self.parser_factory_factory(loop)
        return self

    def send_data(self, data):
        # Process <data> as if we just received it over the network
        parser = self.parser_factory()
        parser.connection_made(None)
        parser.data_received(data)
        parser.eof_received()
        parser.connection_lost(None)
        tasks = asyncio.Task.all_tasks()
        # This might not be called from within an event loop, so execute pending read_object tasks
        if tasks and not self.loop.is_running():
            self.loop.run_until_complete(asyncio.wait(tasks))

    def close(self): # nothing to close here
        pass


#############################
# message (stream) parsers
#############################
class MappingParser(asyncio.Protocol):
    """ Mapping parser is a base class for most parsers.
    There are two jobs the parser must do to turn bytes on the stream into
    a sequence of objects to pass to read_object:
    1. Buffer and segment the stream into bytes corresponding to different objects
    2. Turn those bytes into the objects (unpickle, json, xml, etc

    This base class assumes no buffering and segmenting is needed.  Each message is 1 object.
    map_fn turns this group of bytes into input to read_fn
    """

    def __init__(self, configname, read_fn, map_fn, loop, register_fn):
        self.configname = configname
        self.read_fn = read_fn  # the coroutine to schedule with the parsed object
        self.loop = loop
        self.map_fn = map_fn  # the function turning bytes into an object
        self.register_fn, self.unregister_fn = register_fn
        self.registered_key = None

    def connection_made(self, transport):
        if self.register_fn:
            self.registered_key = self.register_fn(transport)

    def data_received(self, data):
        # create the coroutine to process the data
        coro = self.read_fn(self.map_fn(data), self.registered_key)
        # because this might not be in the main thread use call_soon_threadsafe
        self.loop.call_soon_threadsafe(MappingParser.create_task,coro,self.loop)

    def connection_lost(self, _):
        self.unregister_fn(self.registered_key)

    def create_task(coro, loop):
        # only called with loop.call_soon_threadsafe, will be called in the main loop
        asyncio.Task(coro,loop=loop)
        
class _IdentityParser(MappingParser):
    """ Use the identity mapping function (read object gets a raw byte stream """
    def __init__(self, configname, read_fn, loop, register_fn):
        MappingParser.__init__(self, configname, read_fn, lambda x: x, loop, register_fn)

class _UnPickleParser(MappingParser):
    """ Use pickle.loads as the mapping function, assuming the message was one pickled object """
    def __init__(self, configname, read_fn, loop, register_fn):
        MappingParser.__init__(self, configname, read_fn, pickle.loads, loop, register_fn)

#####
# A stream may contain many pickled objects in a row, we need to separate them and
# call read_object on each in succession.  This function takes a buffer,
# grabs as many unpickled objects as it can from the head, and returns
# the objects and the remaining buffer
#####
import pickletools
def pickle_stream(buf):
    ret = []
    try:
        while len(buf):
            # start parsing pickle op codes from the stream
            g=pickletools.genops(buf)
            for x in g:
                l=x[2]
            # we finished an object, append it to the list and adjust the buffer
            ret.append(pickle.loads(buf[:l+1]))
            buf = buf[(l+1):]
    finally:
        # next(g) will throw an exception if the buffer contains an incomplete pickle
        # return the completed objects, and the remaining buffer
        return (ret, buf)    

class _UnPickleStreamParser(MappingParser):
    # Take a stream (like from tcp), and schedule read_object on each 
    # sucessive pickled object from it.

    def __init__(self, configname, read_fn, loop, register_fn):
        MappingParser.__init__(self, configname, read_fn, lambda x: x, loop, register_fn)
        self.buf = b''

    def data_received(self,data):
        self.buf = self.buf + data  # append the data to the buffer
        ret, self.buf = pickle_stream(self.buf)  # pull out any complete objects at the buffer's head
        for obj in ret:  # schedule each of the complete objects for processing by read_object
            coro = self.read_fn(self.map_fn(obj), self.registered_key)
            self.loop.call_soon_threadsafe(MappingParser.create_task,coro,self.loop)
        

#############################
# Network Writers
#############################


class _BaseWriter():
    def __init__(self, configname, require_config=True):
        self.configname = configname
        try:
            self.config = MC.MavenConfig[configname]
            self.writer_key = self.config.get(CONFIG_WRITERKEY, None)
        except:
            if require_config:
                raise MC.InvalidConfig("some real error")
            else:
                self.writer_key = None

    def _register_new(self, obj):
        raise Exception("Cannot register a dynamic writer for obj " + str(type(self)))

class _SocketClientWriter(_BaseWriter):
    # Connects to a remote server over a socket to write its data

    def __init__(self, configname):
        _BaseWriter.__init__(self,configname)
        try:
            # get real parameters here
            self.host = self.config[CONFIG_HOST]
            self.port = self.config[CONFIG_PORT]
            self.writer_key = self.config.get(CONFIG_WRITERKEY, None)
        except KeyError as e:
            raise MC.InvalidConfig("SocketReader "+configname+" missing parameter: "+e.args[0])        
        
    def write_object(self, obj):
        self.socket.sendall(obj)

    def schedule(self, loop):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.socket.setblocking(False)

    def close(self):
        self.socket.close()


class _SocketReplyWriter(_BaseWriter):
    def __init__(self, configname, socket=None):
        if socket:
            self.socket = socket
            self.writer_key = "socket:%d" % socket.fileno()
        else:
            _BaseWriter.__init__(self, configname)
            global _global_writers
            _global_writers[self.writer_key] = self

    def schedule(self, loop):
        pass

    def write_object(self, obj):
        if not self.socket:
            raise Exception("SocketReplyWriter needs a socket to reply on!")
        self.socket.sendall(obj)
        
    def close(self):
        pass

    def _register_new(self, obj):
        return _SocketReplyWriter(self.configname, obj.get_extra_info('socket'))

class _SocketQueryWriter(_BaseWriter):
    def __init__(self, configname, socket=None):
        _BaseWriter.__init__(self, configname)
        self.socket = None

    def schedule(self, loop):
        pass

    def write_object(self, obj):
        if not self.socket:
            raise Exception("SocketReplyWriter needs a socket to reply on!")
        self.socket.sendall(obj)
        
    def close(self):
        pass

    def _register_new(self, obj):
        self.socket = obj.get_extra_info('socket')
        return None
        

class _RabbitWriter(_BaseWriter):
    def __init__(self, configname):
        _BaseWriter.__init__(self,configname)
        try:
            # get real parameters here
            self.host = self.config[CONFIG_HOST]
            self.exchange = self.config[CONFIG_EXCHANGE]
            self.incoming_key = self.config[CONFIG_KEY]
            self.writer_key = self.config.get(CONFIG_WRITERKEY, None)
        except KeyError as e:
            raise MC.InvalidConfig("SocketReader "+configname+" missing parameter: "+e.args[0])

    def schedule(self, loop):
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

class _ExplicitWriter(_BaseWriter):
    def __init__(self, configname):
        _BaseWriter.__init__(self,configname, require_config=False)
        self.count=0

    def write_object(self, obj):
        ML.PRINT(obj)
        #self.count += 1
        #if self.count % 1000 == 0:
        #    print("received %d" % self.count)

    def schedule(self, loop):
        pass

    def close(self):
        pass

#  Mapping from reader types in the config file to the classes that handle them
_reader_map = {
    CONFIGVALUE_THREADEDRABBIT:_RabbitReader,
    CONFIGVALUE_ASYNCIOSERVERSOCKET:_SocketServerReader,
    CONFIGVALUE_EXPLICIT:_ExplicitReader,
    CONFIGVALUE_ASYNCIOSOCKETQUERY:_SocketQueryReader,
}

#  Mapping from writer types in the config file to the classes that handle them
_writer_map = {
    CONFIGVALUE_THREADEDRABBIT:_RabbitWriter,
    CONFIGVALUE_ASYNCIOCLIENTSOCKET:_SocketClientWriter,
    CONFIGVALUE_EXPLICIT:_ExplicitWriter,
    CONFIGVALUE_ASYNCIOSOCKETREPLY:_SocketReplyWriter,
    CONFIGVALUE_ASYNCIOSOCKETQUERY:_SocketQueryWriter,
}

#  Mapping from parser types in the config file to the classes that handle them
_parser_map = {
    CONFIGVALUE_IDENTITYPARSER:_IdentityParser,
    CONFIGVALUE_UNPICKLEPARSER:_UnPickleParser,
    CONFIGVALUE_UNPICKLESTREAMPARSER:_UnPickleStreamParser,
}
