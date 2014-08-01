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
import pickletools
import amqp
import traceback
import socket
import time
import concurrent.futures
import maven_config as MC
import maven_logging as ML

# parameter names for the config file
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
CONFIGVALUE_DISCONNECTRESTART = 'restart'
CONFIGVALUE_DISCONNECTIGNORE = 'ignore'

CONFIG_HOST = "host"
CONFIG_PORT = "port"
CONFIG_WRITERKEY = "writer key"
CONFIG_WRITERDYNAMICKEY = "dynamic writer key"
CONFIG_DEFAULTWRITEKEY = "default writer key"
CONFIG_QUEUE = "queue"
CONFIG_EXCHANGE = "exchange"
CONFIG_KEY = "key"
CONFIG_ONDISCONNECT = 'disconnect'
CONFIG_PARSERTIMEOUT = "parser timeout"


global _global_writers

_global_writers = {}


class StreamProcessorException(Exception):
    pass


class StreamProcessor():
    """ This is a basic stream processor class.  It implements several different stream
    protocols so that developers only have to worry about the logic of their programs,
    not how they communicate.

    It requires configuration parameters which tell it how to read and write.  Its subclasses
    only have to implement read_raw or read_object, and write to write_raw or write_object.
    """

    ##########################
    # Fields to be overwritten
    ##########################

    @asyncio.coroutine
    def read_object(self, obj, key):
        """ This is the entry coroutine into the processing logic and must be overridden.
        When a complete message is received, it is decoded into an object, and this
        coroutine is scheduled.  Note that if a connection breaks, or at object does
        not parse correctly, this does not get called.

        Note, it must never block.  Any operation that might block must 'yield from'
        something instead.

        :param obj: an object decoded from the message
        :param key: used when a reader and writer are paired as the way to send a later
                    response back to the correct initial sender.  It may be process-specific.

                    Example, a listening socket server accepts a connection and receives some data.
                    The data object is passed along with the key associated with this socket.
                    After a potentially large number of intermediate steps, we need to send a reply
                    back on the same socket.  Call write_object(obj, key) to send it back on the
                    correct socket.

                    If this is not your behavior, ignore this param.
        """
        raise NotImplemented

    @asyncio.coroutine
    def timed_wake(self):
        """ This is the entry coroutine for periodic (not message driven) action.
        It will be schedule to wake up at a configurable time intervals.

        Note, it must never block.  Any operation that might block must 'yield from'
        something instead.
        """
        pass

    def __init__(self, configname):
        """ Initialize the StreamProcessor superclass, getting all of the IO and
        helper functions from the MavenConfig structure.  It creates the StreamProcess,
        but does not yet make network connections.

        :param configname: the name of the instance to pull config parameters
        """

        # This section reads the config file and sets up network connections
        if not configname:
            raise MC.InvalidConfig("Stream parser needs a config entry")
        try:
            self.configname = configname
            if configname not in MC.MavenConfig:
                raise MC.InvalidConfig(configname + " is not in the MavenConfig map.")
            config = MC.MavenConfig[configname]

            try:
                readertype = config.get(CONFIG_READERTYPE, None)
                readername = config.get(CONFIG_READERNAME, None)
                writertype = config[CONFIG_WRITERTYPE]
                writernames = config.get(CONFIG_WRITERNAME, None)
                self.default_write_key = config.get(CONFIG_DEFAULTWRITEKEY, None)
                try:
                    self.dynamic_writer = config[CONFIG_WRITERDYNAMICKEY]
                    self.has_dynamic_writer = True
                except KeyError:
                    self.has_dynamic_writer = False
                if not type(writernames) is list:
                    writernames = [writernames]
                parsertype = config.get(CONFIG_PARSERTYPE, CONFIGVALUE_IDENTITYPARSER)
                parsername = config.get(CONFIG_PARSERNAME, None)
                self.wakeup = config.get(CONFIG_WAKESECONDS, None)
            except KeyError:
                raise MC.InvalidConfig(configname + " did not have sufficient parameters.")

            # We have the names and types of the sub-modules, now instantiate them
            try:
                # We need to create a parser factory that knows what the loop is, but we don't have
                # the loop yet.  The factory_factory takes a loop, and creates a parser_factory
                # suitable for use by asyncio.create_server: a function with no arguments that
                # creates a new parser object.
                # The parser's arguments are it's name (for config stuff if any, a read
                # coroutine function to schedule a new read, a function to put a new read
                # coroutine instance on the loop
                self.parser_factory_factory = \
                    lambda loop: lambda: _parser_map[parsertype](parsername, self.read_object,
                                                                 loop, (self._register_writer,
                                                                        self.unregister_writer))

            except KeyError:
                raise MC.InvalidConfig("Invalid parser type for " + configname + ": " + parsertype)

            # Create the reader, passing it it's name and the parser_factory_factory which takes
            # messages, buffers and chunks them if needed, and parses them into objects
            try:
                self.reader = _reader_map[readertype](readername, self.parser_factory_factory)
            except KeyError:
                raise MC.InvalidConfig("Invalid reader type for " + configname + ": " + readertype)

            # Create the writer(s)
            try:
                self.writers = {}
                for writername in writernames:
                    w = _writer_map[writertype](writername)
                    self.writers[w.writer_key] = w
            except KeyError:
                raise MC.InvalidConfig("Invalid writer type for " + configname + ": " + writertype)

            if self.wakeup:
                try:
                    self.wakeup = float(self.wakeup)
                except ValueError:
                    raise MC.InvalidConfig("Wakup time must be int, is " + str(self.wakeup))

        except Exception as e:
            ML.ERROR("MC.InvalidConfig in " + self.configname)
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
        self.loop = loop
        self.closed = False
        if self.wakeup:
            self.next_sleep = None
            asyncio.Task(self.wake_up_alarm(), loop=loop)
        for w in self.writers.values():
            w.schedule(loop)
        return self.reader.schedule(loop)

    def write_object(self, obj, writer_key=None, port=None):
        """ write_object is used by the stream processing logic to send a message to
            the configured next step.
        :param obj: the object to write on the output channel
        """
        if not port:
            # print('writer key passed in as '+str(writer_key))
            if not writer_key:
                writer_key = self.default_write_key
                # print('set writer_key to '+str(writer_key))
            try:
                w = self.writers[writer_key]
                # print('set w to '+str(w))
            except KeyError:
                # print('no such writer key in writers')
                try:
                    w = _global_writers[writer_key]
                    # print('set w = '+str(w))
                except KeyError:
                    w = self.writers[None]
                    # print('no such default, setting based on None: '+str(w))
            w.write_object(obj)
        else:
            return self.write_object_direct(obj, writer_key, port)

    @asyncio.coroutine
    def write_object_direct(self, obj, host, port):
        ML.DEBUG(str((host, port)))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        yield from self.loop.sock_connect(s, (host, port))
        s.setblocking(False)
        s.sendall(obj)
        s.close()

    def _register_writer(self, transport):
        if self.has_dynamic_writer:
            global _global_writers
            w = _global_writers[self.dynamic_writer]._register_new(transport)
            if w:
                _global_writers[w.writer_key] = w
                return w.writer_key
            else:
                return _global_writers[self.dynamic_writer].writer_key
        return None

    def unregister_writer(self, key):
        if self.has_dynamic_writer:
            global _global_writers
            if not key == self.dynamic_writer:
                # ML.DEBUG("removing " + str(key) + " from "+str(_global_writers))
                try:
                    # print('unregistering '+key+' from '+str(_global_writers))
                    _global_writers.pop(key).close()
                except KeyError:
                    pass
            else:
                _global_writers[key]._unregister()

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


class ReEstablishProtocol(asyncio.Protocol):
    def __init__(self, loop, transport_cb, host=None, port=None, ssl=None, server_hostname=None,
                 protocol_factory=None):
        # print("initializing reestablish protocol")
        self.host = host
        self.port = port
        self.ssl = ssl
        self.server_hostname = server_hostname
        self.loop = loop
        self.transport_cb = transport_cb
        self.protocol_factory = protocol_factory
        self.reader = None

    def factory(self):
        if self.protocol_factory:
            self.reader = self.protocol_factory(self.loop)()
        return self

    @asyncio.coroutine
    def connect(self):
        # print("in connect")
        sleeptime = .1
        while sleeptime:
            try:
                yield from self.loop.create_connection(self.factory, host=self.host,
                                                       port=self.port, ssl=self.ssl,
                                                       server_hostname=self.server_hostname)

                sleeptime = 0
            except:
                sleeptime = sleeptime * 2
                if sleeptime > 2:
                    sleeptime = 4
                    # traceback.print_exc()
                # print("trying again after sleeping for "+str(sleeptime))
                yield from asyncio.sleep(sleeptime, self.loop)

    def connection_made(self, transport):
        # print("connecting made - registering it")
        self.transport_cb(transport)
        if self.reader:
            self.reader.connection_made(transport)

    def connection_lost(self, exc):
        # print("connection lost")
        if self.reader:
            self.reader.connection_lost(exc)
        self.reader = None
        if self.transport_cb(None):  # returns true iff the connection should start again
            # print("scheduling an attempt to re-establish")
            asyncio.Task(self.connect())

    def data_received(self, data):
        if self.reader:
            self.reader.data_received(data)

    def eof_received(self):
        if self.reader:
            self.reader.eof_received()


class _SocketServerReader():
    # Starts a server to read data from a socket and pass it to the stream processor

    def __init__(self, configname, parser_factory_factory):
        # store initialization arguments, and look up the config map
        self.parser_factory_factory = parser_factory_factory
        self.configname = configname
        if configname not in MC.MavenConfig:
            raise MC.InvalidConfig("some real error")
        config = MC.MavenConfig[configname]
        # get real parameters here, throwing errors if necessary ones are missing
        try:
            self.host = config.get(CONFIG_HOST, None)
            self.port = config[CONFIG_PORT]
        except KeyError as e:
            raise MC.InvalidConfig("SocketReader " + configname + " missing: " + e.args[0])

    def schedule(self, loop):
        self.loop = loop
        # start a listening server which creates a new instance of the parser for each connection
        server = asyncio.Task(loop.create_server(self.parser_factory_factory(loop),
                                                 host=self.host, port=self.port), loop=loop)
        self.server = loop.run_until_complete(server)
        return self.server

    def close(self):
        self.server.close()


class _SocketQueryReader():
    def __init__(self, configname, parser_factory_factory):
        self.parser_factory_factory = parser_factory_factory
        self.configname = configname
        if configname not in MC.MavenConfig:
            raise MC.InvalidConfig("some real error")
        config = MC.MavenConfig[configname]
        # get real parameters here, throwing errors if necessary ones are missing
        try:
            self.host = config.get(CONFIG_HOST, None)
            self.port = config[CONFIG_PORT]
            self.ondisconnect = config.get(CONFIG_ONDISCONNECT, CONFIGVALUE_DISCONNECTIGNORE)
        except KeyError as e:
            raise MC.InvalidConfig("SocketReader " + configname + " parameter: " + e.args[0])
        self.closed = False

    def schedule(self, loop):
        self.loop = loop
        # start a listening server which creates a new instance of the parser for each connection
        protocol = ReEstablishProtocol(loop, self.set_transport, host=self.host, port=self.port,
                                       protocol_factory=self.parser_factory_factory)
        self.server = asyncio.Task(protocol.connect())
        loop.run_until_complete(asyncio.sleep(.01))
        return self.server

    def set_transport(self, transport):
        return self.ondisconnect == CONFIGVALUE_DISCONNECTRESTART and not self.closed

    def close(self):
        self.closed = True
        self.server.cancel()


class _RabbitReader():
    # Starts a server to read data from RabbitMQ and pass it to the stream processor

    def __init__(self, configname, parser_factory_factory):

        # store initialization arguments, and look up the config map
        self.parser_factory_factory = parser_factory_factory
        self.configname = configname
        self.rabbit_listener_thread_pool = None
        if configname not in MC.MavenConfig:
            raise MC.InvalidConfig("some real error")
        config = MC.MavenConfig[configname]

        # get real parameters here, throwing errors if necessary ones are missing
        try:
            self.host = config[CONFIG_HOST]
            self.queue = config[CONFIG_QUEUE]
            self.exchange = config[CONFIG_EXCHANGE]
            self.incoming_key = config[CONFIG_KEY]
        except KeyError as e:
            raise MC.InvalidConfig("RabbitReader " + configname + " parameter: " + e.args[0])

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
            ML.INFO("CAUGHT EXCEPTION" + e.args[0])

    def close(self):
        try:
            # rabbit in the other thread has some odd behavior when closing
            # (chan.wait() is executing.  For now this seems to work
            self.conn.close()
        except IOError:
            pass
        self.rabbit_listener_pool.shutdown(wait=False)


class _ExplicitReader():
    """ No server is started.  Instead of reading data from the network,
    this class takes its input from a function call.
    Useful mostly for testing purposes
    """
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

    def close(self):  # nothing to close here
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
        self.timeout = None
        if configname in MC.MavenConfig:
            config = MC.MavenConfig[configname]
            self.timeout = config.get(CONFIG_PARSERTIMEOUT, None)

        self.read_fn = read_fn  # the coroutine to schedule with the parsed object
        self.loop = loop
        self.map_fn = map_fn  # the function turning bytes into an object
        self.register_fn, self.unregister_fn = register_fn
        self.registered_key = None
        self.transport = None
        self.update_last_activity()

    def update_last_activity(self):
        self.last_activity = time.time()
        if self.timeout:
            asyncio.Task(self.check_timeout(), loop=self.loop)

    @asyncio.coroutine
    def check_timeout(self):
        yield from asyncio.sleep(self.timeout)
        if time.time() - self.last_activity >= self.timeout:
            if self.transport:
                self.transport.close()

    def connection_made(self, transport):
        self.update_last_activity()
        if self.register_fn:
            self.transport = transport
            self.registered_key = self.register_fn(transport)

    def data_received(self, data):
        self.update_last_activity()
        # create the coroutine to process the data
        coro = self.read_fn(self.map_fn(data), self.registered_key)
        # because this might not be in the main thread use call_soon_threadsafe
        self.loop.call_soon_threadsafe(MappingParser.create_task, coro, self.loop)

    def connection_lost(self, _):
        # ML.DEBUG("connection lost")
        self.close()

    def close(self):
        if self.registered_key:
            self.unregister_fn(self.registered_key)
        if self.transport:
            self.transport.close()

    def create_task(coro, loop):
        # only called with loop.call_soon_threadsafe, will be called in the main loop
        asyncio.Task(coro, loop=loop)


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


def pickle_stream(buf):
    ret = []
    try:
        while len(buf):
            # start parsing pickle op codes from the stream
            g = pickletools.genops(buf)
            for x in g:
                l = x[2]
            # we finished an object, append it to the list and adjust the buffer
            ret.append(pickle.loads(buf[:l + 1]))
            buf = buf[(l + 1):]
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

    def data_received(self, data):
        self.update_last_activity()
        self.buf = self.buf + data  # append the data to the buffer
        ret, self.buf = pickle_stream(self.buf)  # grab complete objects at the buffer's head
        for obj in ret:  # schedule each of the complete objects for processing by read_object
            coro = self.read_fn(self.map_fn(obj), self.registered_key)
            self.loop.call_soon_threadsafe(MappingParser.create_task, coro, self.loop)


#############################
# Network Writers
#############################


class _BaseWriter():
    def __init__(self, configname, require_config=True):
        self.configname = configname
        try:
            self.config = MC.MavenConfig[configname]
            self.writer_key = self.config.get(CONFIG_WRITERKEY, None)
            self.ondisconnect = self.config.get(CONFIG_ONDISCONNECT, CONFIGVALUE_DISCONNECTIGNORE)
        except:
            if require_config:
                raise MC.InvalidConfig("some real error")
            else:
                self.writer_key = None

    def _register_new(self, obj):
        raise Exception("Cannot register a dynamic writer for obj " + str(type(self)))

    def write_object(self, obj, host, port):
        raise NotImplemented()

    def _unregister(self):
        pass


class _SocketClientWriter(_BaseWriter):
    # Connects to a remote server over a socket to write its data

    def __init__(self, configname):
        _BaseWriter.__init__(self, configname)
        try:
            # get real parameters here
            self.host = self.config[CONFIG_HOST]
            self.port = self.config[CONFIG_PORT]
            self.writer_key = self.config.get(CONFIG_WRITERKEY, None)
            self.ondiconnect = self.config.get(CONFIG_ONDISCONNECT, CONFIGVALUE_DISCONNECTIGNORE)
        except KeyError as e:
            raise MC.InvalidConfig("SocketReader " + configname + " parameter: " + e.args[0])
        self.closed = False
        self.transport = None

    def write_object(self, obj):
        if self.transport:
            self.transport.write(obj)
        else:
            ML.INFO(str(obj))
            raise StreamProcessorException("no transport active to write on")

    def schedule(self, loop):
        self.loop = loop
        protocol = ReEstablishProtocol(loop, self.set_transport, host=self.host, port=self.port)
        loop.run_until_complete(asyncio.Task(protocol.connect()))

    def set_transport(self, transport):
        self.transport = transport
        return self.ondisconnect == CONFIGVALUE_DISCONNECTRESTART and not self.closed

    def close(self):
        self.closed = True
        self.transport.close()


class _SocketReplyWriter(_BaseWriter):

    counter = 1

    def __init__(self, configname, transport=None):
        if transport:
            self.transport = transport
            self.writer_key = "writer:" + str(_SocketReplyWriter.counter)
            _SocketReplyWriter.counter += 1
        else:
            _BaseWriter.__init__(self, configname)
            self.transport = None
        # self.last_writer = None
        global _global_writers
        _global_writers[self.writer_key] = self
        # ML.DEBUG('reply writer created: ' + str(self.writer_key))

    def schedule(self, loop):
        # ML.DEBUG('scheduled reply writer')
        pass

    def write_object(self, obj):
        ML.DEBUG(('writing object %s: ' % self.writer_key) + str(obj))
        if not self.transport:
            # if not self.last_writer:
            raise StreamProcessorException("SocketReplyWriter needs a socket to reply on!")
            # else:
            #    self.last_writer.write_object(obj)
        else:
            self.transport.write(obj)

    def close(self):
        # ML.DEBUG('closing writer')
        if self.transport:
            self.transport.write_eof()
            self.transport.close()
            self.transport = None

    def _register_new(self, obj):
        self.last_writer = _SocketReplyWriter(self.configname, obj)
        return self.last_writer


class _SocketQueryWriter(_BaseWriter):
    def __init__(self, configname):
        _BaseWriter.__init__(self, configname)
        self.transport = None
        global _global_writers
        _global_writers[self.writer_key] = self

    def schedule(self, loop):
        pass

    def write_object(self, obj):
        if not self.transport:
            raise Exception("SocketReplyWriter needs a socket to reply on!")
        self.transport.write(obj)

    def close(self):
        self.transport = None
        pass

    def _register_new(self, obj):
        self.transport = obj
        return None

    def _unregister(self):
        self.transport = None


class _RabbitWriter(_BaseWriter):
    def __init__(self, configname):
        _BaseWriter.__init__(self, configname)
        try:
            # get real parameters here
            self.host = self.config[CONFIG_HOST]
            self.exchange = self.config[CONFIG_EXCHANGE]
            self.incoming_key = self.config[CONFIG_KEY]
            self.writer_key = self.config.get(CONFIG_WRITERKEY, None)
        except KeyError as e:
            raise MC.InvalidConfig("RabbitWriter " + configname + " parameter: " + e.args[0])

    def schedule(self, loop):
        try:
            self.conn = amqp.Connection(self.host)
            self.chan = self.conn.channel()

            if self.exchange == 'fanout_evaluator':
                self.chan.exchange_declare(exchange=self.exchange,
                                           type='fanout')
        except:
            traceback.print_exc()
            raise

    def write_object(self, obj):
        # ML.DEBUG("rabbit writing obj: "+str(obj))
        message = amqp.Message(pickle.dumps(obj))
        self.chan.basic_publish(message, exchange=self.exchange,
                                routing_key=self.incoming_key)

    def close(self):
        self.chan.close()
        self.conn.close()


class _ExplicitWriter(_BaseWriter):
    def __init__(self, configname):
        _BaseWriter.__init__(self, configname, require_config=False)
        self.count = 0

    def write_object(self, obj):
        ML.PRINT(obj)
        # self.count += 1
        # if self.count % 1000 == 0:
        #    print("received %d" % self.count)

    def schedule(self, loop):
        pass

    def close(self):
        pass

#  Mapping from reader types in the config file to the classes that handle them
_reader_map = {
    CONFIGVALUE_THREADEDRABBIT: _RabbitReader,
    CONFIGVALUE_ASYNCIOSERVERSOCKET: _SocketServerReader,
    CONFIGVALUE_EXPLICIT: _ExplicitReader,
    CONFIGVALUE_ASYNCIOSOCKETQUERY: _SocketQueryReader,
}

#  Mapping from writer types in the config file to the classes that handle them
_writer_map = {
    CONFIGVALUE_THREADEDRABBIT: _RabbitWriter,
    CONFIGVALUE_ASYNCIOCLIENTSOCKET: _SocketClientWriter,
    CONFIGVALUE_EXPLICIT: _ExplicitWriter,
    CONFIGVALUE_ASYNCIOSOCKETREPLY: _SocketReplyWriter,
    CONFIGVALUE_ASYNCIOSOCKETQUERY: _SocketQueryWriter,
}

#  Mapping from parser types in the config file to the classes that handle them
_parser_map = {
    CONFIGVALUE_IDENTITYPARSER: _IdentityParser,
    CONFIGVALUE_UNPICKLEPARSER: _UnPickleParser,
    CONFIGVALUE_UNPICKLESTREAMPARSER: _UnPickleStreamParser,
}
