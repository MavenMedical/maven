import psycopg2, asyncio
from app.database_utils.dbconfig import CONNECTION_STRING
import sys
import traceback

import maven_logging as ML

class SocketReadyFuture(asyncio.Future):
    read = True
    write = False

    def __init__(self, is_reader, fileno, loop):
        asyncio.Future.__init__(self)
        self.is_reader = is_reader
        self.loop = loop
        self.fileno = fileno
        if(is_reader):
            loop.add_reader(fileno, SocketReadyFuture.wake_future, self)
        else:
            loop.add_writer(fileno, SocketReadyFuture.wake_future, self)

    def wake_future(self):
        if(self.is_reader):
            self.loop.remove_reader(self.fileno)
        else:
            self.loop.remove_writer(self.fileno)
        self.set_result(None)


class ConnectionPool():

    MAX_CONNECTIONS = 8
    MIN_CONNECTIONS = 2

    # make very sure not to loose the returned connection
    @asyncio.coroutine
    def _get_connection(self):
        #ML.DEBUG("in ConnectionPool._get_connection")
        yield from self.connection_sem.acquire()
        connection = self.ready.pop()
        self.in_use.add(connection)
        ML.DEBUG("reused a connection: (%d, %d, %d)" % (len(self.ready),len(self.in_use), self.pending))
        active = self.pending + len(self.ready) + len(self.in_use)
        if len(self.ready) + self.pending < 1 and active <self. MAX_CONNECTIONS:
            asyncio.Task(self._new_connection(),loop=self.loop)
            self.pending += 1
            ML.DEBUG("launching a new connection task: (%d, %d, %d)" %(len(self.ready),len(self.in_use),self.pending))
        return connection

    def _release_connection(self,connection):
        self.in_use.remove(connection)
        self.ready.append(connection)
        self.connection_sem.release()

    def __init__(self, name, loop):
        #ML.DEBUG("in ConnectionPool.__init__")
        self.ready = []
        self.in_use = set()
        self.loop = loop
        self.mog_cursor = None
        self.pending = self.MIN_CONNECTIONS
        [asyncio.Task(self._new_connection(),loop=loop) for x in range(self.MIN_CONNECTIONS)]
        ML.DEBUG("starting multiple connections")
        self.connection_sem = asyncio.Semaphore(0,loop=loop)
        
        
    @asyncio.coroutine
    def _new_connection(self):
        if(len(self.ready) + len(self.in_use) + self.pending <= self.MAX_CONNECTIONS):
            connection = psycopg2.connect(CONNECTION_STRING, async=1)
            yield from self._wait(connection)
            ML.DEBUG("allocated a new connection")
            self.ready.append(connection)
            self.connection_sem.release()
        self.pending -= 1
        

    @asyncio.coroutine
    def _wait(self, connection):
        #ML.DEBUG("in ConnectionPool.wait")
        try:
            while True:
                state = connection.poll()
                if state == psycopg2.extensions.POLL_OK:
                    break
                elif state == psycopg2.extensions.POLL_WRITE:
                    yield from SocketReadyFuture(SocketReadyFuture.write, connection.fileno(), self.loop)
                elif state == psycopg2.extensions.POLL_READ:
                    yield from SocketReadyFuture(SocketReadyFuture.read, connection.fileno(), self.loop)
            else:
                raise psycopg2.OperationalError("poll() returned %s" % state)
        except Exception:
            print(">>>>>>>>>>>>>>>>ERROR HERE<<<<<<<<<<<<<<<<<")
            traceback.print_exc(file=sys.stdout)
            sys.stdout.flush()
            #yield from err

    @asyncio.coroutine
    def execute(self, str, extra=None):
        ML.DEBUG('about to execute %s' % (str.split(' ', 1)[0]))
        conn = yield from self._get_connection()
        try: 
            cur = conn.cursor()
        #ML.DEBUG("got a cursor")
            if extra:
                cur.execute(str,extra)
            else:
                cur.execute(str)
            result = yield from self._wait(conn)
            ML.DEBUG("finish execution")
            return cur
        finally:
            self._release_connection(conn)

    def execute_and_close(self, str, extra=None):
        cur = yield from self.execute(str,extra)
        cur.close()

    def iterate_and_print(self,cur):
        ML.DEBUG("about to iterate for cursor %s" % str(cur))
        for x in cur:
#            ML.DEBUG("an iteration for cursor %s" % str(cur))
            pass
        ML.DEBUG("done iterating %s" % str(cur))
        
    def close(self):
        for conn in self.ready:
            conn.close()
        for conn in self.in_use:
            conn.close()

    @asyncio.coroutine
    def mogrify_cursor(self):
        if self.mog_cursor == None:
            conn = yield from self._get_connection()
            try:
                self.mog_cursor = conn.cursor()
            finally:
                self._release_connection(conn)
        print("returning mogrify cursor %s" % str(self.mog_cursor))
        return self.mog_cursor

@asyncio.coroutine
def db_main(loop, id, conn):
    try: 
        yield from conn.execute_and_close('drop table TomTest'+id)
    except psycopg2.ProgrammingError:
        pass
    yield from conn.execute_and_close('create table TomTest'+id+' (id serial PRIMARY KEY, num integer, data varchar);')
    rows=[]
    for i in range(100000):
        rows.append((i, 'string %d' % i))
    mog_cursor = yield from conn.mogrify_cursor()
    args_str = b','.join(mog_cursor.mogrify("%s", (x, )) for x in rows)
    yield from conn.execute_and_close("INSERT INTO tomtest"+id+" (num, data) VALUES "+args_str.decode("utf-8"))
    cur = yield from conn.execute('select * from TomTest'+id)
    conn.iterate_and_print(cur)
    cur.close()
    cur = yield from conn.execute('select * from TomTest'+id)
    conn.iterate_and_print(cur)
    cur.close()
    cur = yield from conn.execute('select * from TomTest'+id)
    conn.iterate_and_print(cur)
    cur.close()

@asyncio.coroutine
def process(loop,  id, conn):
    for x in range(3):
        print("hello from %s" % id)
        yield from db_main(loop, id, conn)
        print("%s sleeping" % id)
        yield from asyncio.sleep(.5)
        print("%s woke up" % id)


def async_main():
    loop = asyncio.get_event_loop()
    print(loop)
    conn = ConnectionPool('test conn pool', loop)

    tasks = [asyncio.Task(process(loop,x,conn)) for x in ['p1','p2', 'p3', 'p4', 'p5', 'p6', 'p7']]
    #tasks = [asyncio.Task(x) for x in [process(loop,f,'p1')]]
    print("Starting loop")
    loop.run_until_complete(asyncio.wait(tasks))

async_main()


#########
# statistics:
#
# drop table can be expensive
#
# create table is about 40ms
#
# insert is about 7ms + 1ms/200 objects inserted (string parsing to set up the call is more expensive)
# 
# select is about 2ms + 1ms/2000 objects
# iterating is faster than the select
