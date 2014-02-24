import psycopg2, asyncio
from app.database_utils.dbconfig import CONNECTION_STRING
import sys
import traceback

import maven_logging as ML
ML.DEBUG=ML.stdout_log_with_time

con_id = 0
cur_id = 0


class SocketReadyFuture(asyncio.Future):
    final read = True, write = False

    def __init__(self,is_reader, fileno, loop):
        asyncio.Future.__init__(self)
        self.is_reader = is_reader
        self.loop = loop
        self.fileno = fileno
        if(is_reader):
            loop.add_reader(fileno, wake_future, self)
        else:
            loop.add_writer(fileno, wake_future, self)

    def wake_future(self):
        if(self.is_reader):
            self.loop.remove_reader(self.fileno)
        else:
            self.loop.remove_writer(self.fileno)
        self.set_result(None)


#def wake_future(fut):
#    print("in wake_future() %d" % fut.fileno)
#    try:
#        fut.loop.remove_reader(fut.fileno)
#    except Exception:
#        pass
#    try:
#        fut.loop.remove_writer(fut.fileno)
#    except Exception:
#        pass
#    sys.stdout.flush()
#    #if(not fut.done()):
#    fut.set_result(None)
#    print("set the future's results")
#2A    print(fut)


class Connection():

    def __init__(self):
        global con_id
        print("in constructor")
        con_id += 1
        self.cursors = {}

    @asyncio.coroutine
    def connect(self, loop):
        self.loop=loop
        ML.DEBUG("about to connect #%d" % con_id)
        #sys.stdout.flush()
        self.connection = psycopg2.connect(CONNECTION_STRING, async=1)
        ML.DEBUG("connected #%d" % con_id)
        yield from self.wait()


    @asyncio.coroutine
    def wait(self):
        #print("in self.wait()")
        try:
            while True:
                state = self.connection.poll()
                print("state is %d" % state)
                sys.stdout.flush()
                if state == psycopg2.extensions.POLL_OK:
                #print("breaking write away")
                    break
                elif state == psycopg2.extensions.POLL_WRITE:
                #print("process write")
                    fut = asyncio.Future()
                    fut.loop = self.loop
                    fut.fileno =self.connection.fileno()
                    print("created future")
                    self.loop.add_writer(self.connection.fileno(),wake_future,fut)
                    #sem=asyncio.Semaphore()
                    #self.loop.add_writer(self.connection.fileno(),wake_sem,sem)
                    print("yielding")
                    sys.stdout.flush()
                    if not fut.done():
                        yield from fut
                    #yield from asyncio.wait_for(fut)
                    print("disappear")
                    sys.stdout.flush()
                #self.loop.remove_writer(self.connection.fileno())
                elif state == psycopg2.extensions.POLL_READ:
                    fut = asyncio.Future()
                    fut.loop = self.loop
                    fut.fileno =self.connection.fileno()
                    self.loop.add_reader(self.connection.fileno(),wake_future,fut)
                    print("yielding")
                    sys.stdout.flush()
                    if not fut.done():
                        yield from fut
                #self.loop.remove_reader(self.connection.fileno())
                    print("disappear")
                sys.stdout.flush()
            else:
                print("error")
                raise psycopg2.OperationalError("poll() returned %s" % state)
        except Exception:
            print("ERROR HERE")
            traceback.print_exc(file=sys.stdout)
            sys.stdout.flush()
        print("end of the run-on function")


    def get_cursor(self):
        global cur_id
        print("get_cursor")
        cur_id += 1
        ML.DEBUG("creating cursor #%d" % cur_id)
        cur = self.connection.cursor()
        ML.DEBUG("created cursor #%d" % cur_id)
        self.cursors[cur]=cur_id
        return cur

    @asyncio.coroutine
    def execute(self, cur, str, extra=None):
        ML.DEBUG('about to execute %s on %d' % (str.split(' ', 1)[0], self.cursors[cur]))
        if extra:
            cur.execute(str,extra)
        else:
            cur.execute(str)
        yield from self.wait()
        ML.DEBUG('executed on %d' % self.cursors[cur])

    def iterate_and_print(self,cur):
        ML.DEBUG("about to iterate for cursor %d" % self.cursors[cur])
        for x in cur:
#            ML.DEBUG("an iteration for cursor %d" % self.cursors[cur])
            #ML.PRINT("value is " + str(x))
            pass
        ML.DEBUG("done iterating %d" % self.cursors[cur])


@asyncio.coroutine
def db_main(loop):
    print("conn - Connection()")
    conn = Connection()
    #print(1.5)
    print(conn)
    sys.stdout.flush()
    cc=conn.connect(loop)
    print(cc)
    sys.stdout.flush()

    yield from cc
    print(2)
    print(str(conn))
    print(3)
    sys.stdout.flush()
    cur = conn.get_cursor()
    sys.stdout.flush()
    print(cur)
    try: 
        print(3)
        yield from conn.execute(cur,'drop table TomTest')
    except psycopg2.ProgrammingError:
        pass
    yield from conn.execute(cur,'create table TomTest (id serial PRIMARY KEY, num integer, data varchar);')
    
    rows=[]
    #for i in range(10):
    #    rows.append((i, 'string %d' % i))
    #args_str = b','.join(cur.mogrify("%s", (x, )) for x in rows)
    #conn.execute(cur,"INSERT INTO tomtest (num, data) VALUES "+args_str.decode("utf-8"))
    #conn.execute(cur,'select * from TomTest')
    #conn.iterate_and_print(cur)
    for i in range(100000):
        rows.append((i, 'string %d' % i))
    args_str = b','.join(cur.mogrify("%s", (x, )) for x in rows)
    yield from conn.execute(cur,"INSERT INTO tomtest (num, data) VALUES "+args_str.decode("utf-8"))
    yield from conn.execute(cur,'select * from TomTest')
    conn.iterate_and_print(cur)
    cur.close()
    print("current is closed")

@asyncio.coroutine
def process(loop, f, id):
    for x in range(2):
        print("hello from %s" % id)
        yield from db_main(loop)
        print("%s sleeping" % id)
        yield from asyncio.sleep(.5)
        print("%s woke up" % id)
    f.count -=1
    if f.count == 0:
        f.set_result(None)


def async_main():
    loop = asyncio.get_event_loop()
    print(loop)
    f = asyncio.Future()
    tasks = [asyncio.Task(x) for x in [process(loop,f,'p1'),process(loop,f,'p2')]]
    f.count = len(tasks)
    print("Starting loop")
    loop.run_until_complete(f)

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
