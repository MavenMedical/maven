import utils.streaming.rpc_processor as RP
import utils.streaming.stream_processor as SP
import asyncio
from maven_config import MavenConfig
from maven_logging import PRINT  # , get_results


class foo:
    def __init__(self, b=None):
        self.x = 1
        self.b = b

    @asyncio.coroutine
    def getX(self,):
        return self.x

    @asyncio.coroutine
    def setX(self, x):
        self.x = x
        if self.b:
            PRINT('yielding from b.times2')
            self.x = yield from self.b.times2(x)
        if x > 40:
            raise Exception('bad x')


class bar():
    @asyncio.coroutine
    def times2(self, x):
        return x * 2


MavenConfig.update({
    'side2': {
        SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETREPLY,
        SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSERVERSOCKET,
        SP.CONFIG_WRITERNAME: 'writer2',
        SP.CONFIG_READERNAME: 'reader2',
        SP.CONFIG_WRITERDYNAMICKEY: 2,
        SP.CONFIG_DEFAULTWRITEKEY: 2,
    },
    'writer2': {
        SP.CONFIG_WRITERKEY: 2,
        },
    'reader2': {
        SP.CONFIG_PORT: '54728',
    },
})


SRPC = RP.rpc('side2')

loop = asyncio.get_event_loop()
SRPC.schedule(loop)


b = SRPC.create_client(bar)
F = foo(b)
SRPC.register(F)


MavenConfig.update({
    'side1': {
        SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETREPLY,
        SP.CONFIG_WRITERNAME: 'writer1',
        SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETQUERY,
        SP.CONFIG_READERNAME: 'reader1',
        SP.CONFIG_WRITERDYNAMICKEY: 1,
        SP.CONFIG_DEFAULTWRITEKEY: 1,
    },
    'writer1': {
        SP.CONFIG_WRITERKEY: 1,
    },
    'reader1': {
        SP.CONFIG_HOST: '127.0.0.1',
        SP.CONFIG_PORT: '54728',
    },
})


CRPC = RP.rpc('side1')

loop = asyncio.get_event_loop()
CRPC.schedule(loop)

f = CRPC.create_client(foo)
B = bar()
CRPC.register(B)


@asyncio.coroutine
def run():
    while True:
        yield from asyncio.sleep(.01)
        x = yield from f.getX()
        # print(x)
        PRINT(x)
        yield from asyncio.sleep(.01)
        yield from f.setX(x + 1)

try:
    loop.run_until_complete(run())
except Exception as e:
    PRINT(e.args[0])
    # print(e.args[0])
