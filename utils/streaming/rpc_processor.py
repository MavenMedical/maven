##############################################################################
#  Copyright (c) 2014 - Maven Medical
#
#
#  Description: This file implements remote procedure calls for static
#               objects with asyncio.coroutine functions, and does so
#               on top of the existing stream_processor
#
#  Author: Tom DuBois
#  Assumes: Working stream processor
#  Side Effects: None
##############################################################################

import pickle
import uuid
import functools
import asyncio
import utils.streaming.stream_processor as SP
from maven_config import MavenConfig

"""
CONFIGVALUE_RPCPARSER = 'rpc parser'

def _bytes_to_int16(b):
    return b[0] * 256 + b[1]


def _int16_to_bytes(i):
    return bytes([int(i / 256), i % 256])


# It turns out I don't need this class at all, just use UnPickleParser
class _RPCStreamParser(SP.MappingParser):
    def __init__(self, configname, read_fn, loop, register_fn):
        SP.MappingParser.__init__(self, configname, read_fn, lambda x: x, loop, register_fn)
        # ML.DEBUG("created a new http parser")
        self.buf = b''

    def _next_message(self):
        if len(self.buf) > 2:
            length = _bytes_to_int16(self.buf)
            if len(self.buf) >= 2 + length:
                msg = pickle.loads(self.buf[2:(2+length)])
                self.buf = self.buf[(2+length):]
                return msg
        return None

    def data_received(self, data):
        self.buf += data
        msg = self._next_message()
        while msg:
            coro = self.read_fn(msg, self.registered_key)
            self.loop.call_soon_threadsafe(SP.MappingParser.create_task, coro, self.loop)
            msg = self._next_message()
        pass

    def eof_received(self):
        # ML.DEBUG("EOF")
        return True
"""


class _wrapper:
    """ When a client registers a class, do not instantiate an instance.
        Instead call create_client, and it returns an instance of this class.
        It has the same coroutines as the original class, but executes them
        remotely
    """
    def __init__(self, parent, cls):
        """ This is automatically called from an rpc instance.
            parent is the rpc instance, and cls is the class to create an interface for
        """
        self.parent = parent
        for k, v in cls.__dict__.items():
            # print('evaluating %s, %s, %s' % (k, v, hasattr(v, '__call__')))
            if asyncio.iscoroutinefunction(v):
                self.__dict__[k] = functools.partial(self.wrap, k)
        self.cls = str(cls)

    @asyncio.coroutine
    def wrap(self, k, *args, **kwargs):
        """ Any function call on the client interface will map to here.
            This function marshals the parameters, and sends a message to the server
        """
        u = str(uuid.uuid1())
        v = (u, self.cls, k, args, kwargs)
        msg = pickle.dumps(v)
        fut = asyncio.Future()
        self.parent._send(msg, u, fut)
        yield from fut
        return fut.result()


class rpc(SP.StreamProcessor):
    """ This class creates a full duplex remote procedure call broken on top of
        a stream processor.  This makes it fast and easy to develop complicated
        interfaces quickly and easily.

        The most important limitation is the any class can only have one registered
        instance on the remote machine.
    """

    def __init__(self, configname):
        MavenConfig[configname].update({
            SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_UNPICKLESTREAMPARSER,
        })
        SP.StreamProcessor.__init__(self, configname)
        self.registered = {}
        self.outstanding = {}

    def register(self, obj):
        """ Register an object instance to act as it's classes server object for RPCs
        """
        self.registered[str(obj.__class__)] = obj

    def create_client(self, cls):
        """ Create a client interface matching the coroutine functions of the given class
            Note that the server must have registered an instance of that class for this to work.
        """
        return _wrapper(self, cls)

    def _send(self, msg, uid, fut):
        """ Registers a callback and sends a message to execute an RPC
        :param msg: the pickled message to send
        :param uid: the unique id of the message to send
        :param fut: the future to set when a response comes back
        """
        self.outstanding[uid] = fut
        self.write_object(msg)

    @asyncio.coroutine
    def read_object(self, obj, key):
        """ Got a response from the other side.  Either it's an RPC request
            or an RPC response.  Handle both cases as needed.
        """
        if len(obj) == 2:
            uid, ret = obj
            if uid in self.outstanding:
                fut = self.outstanding.pop(uid)
                if isinstance(ret, Exception):
                    fut.set_exception(ret)
                else:
                    fut.set_result(ret)
        elif len(obj) == 5:
            uid = obj[0]
            try:
                ret = yield from self._execute(*obj)
            except Exception as e:
                ret = e
            msg = pickle.dumps((uid, ret))
            self.write_object(msg, key)

    @asyncio.coroutine
    def _execute(self, uid, cls, fn, args, kwargs):
        """ The client has requested a proceedure call, run it, capture its output
            or exception, and send it back.
        """
        if cls not in self.registered:
            raise Exception('class if not available via rpc')
        s = self.registered[cls]
        if fn not in s.__class__.__dict__:
            raise Exception('class does not expose method via rpc')
        ret = yield from s.__class__.__dict__[fn](s, *args, **kwargs)
        return ret
