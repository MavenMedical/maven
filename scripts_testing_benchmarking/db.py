import psycopg2, asyncio
from app.database_utils.dbconfig import CONNECTION_STRING

import maven_logging as ML
ML.DEBUG=ML.stdout_log_with_time

con_id = 0
cur_id = 0

class Connection():

    def __init__(self):
        global con_id
        con_id += 1
        ML.DEBUG("about to connect #%d" % con_id)
        self.connection = psycopg2.connect(CONNECTION_STRING, async=1)
        ML.DEBUG("connected #%d" % con_id)
        self.connection.set_session(autocommit=True)
        self.cursors = {}

    def get_cursor(self):
        global cur_id
        cur_id += 1
        ML.DEBUG("creating cursor #%d" % cur_id)
        cur = self.connection.cursor()
        ML.DEBUG("created cursor #%d" % cur_id)
        self.cursors[cur]=cur_id
        return cur

    def execute(self, cur, str, extra=None):
        ML.DEBUG('about to execute %s on %d' % (str.split(' ', 1)[0], self.cursors[cur]))
        if extra:
            cur.execute(str,extra)
        else:
            cur.execute(str)
        ML.DEBUG('executed on %d' % self.cursors[cur])

    def iterate_and_print(self,cur):
        ML.DEBUG("about to iterate for cursor %d" % self.cursors[cur])
        for x in cur:
#            ML.DEBUG("an iteration for cursor %d" % self.cursors[cur])
            #ML.PRINT("value is " + str(x))
            pass
        ML.DEBUG("done iterating %d" % self.cursors[cur])


def db_main():
    conn = Connection()
    cur = conn.get_cursor()
    try: 
        conn.execute(cur,'drop table TomTest')
    except psycopg2.ProgrammingError:
        pass
    conn.execute(cur,'create table TomTest (id serial PRIMARY KEY, num integer, data varchar);')
    
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
    conn.execute(cur,"INSERT INTO tomtest (num, data) VALUES "+args_str.decode("utf-8"))
    conn.execute(cur,'select * from TomTest')
    conn.iterate_and_print(cur)
    cur.close()
    print("current is closed")

@asyncio.coroutine
def process(loop, f, id):
    for x in range(2):
        #print("hello from %s" % id)
        db_main()
        print("%s sleeping" % id)
        yield from asyncio.sleep(.5)
        print("%s woke up" % id)
    f.count -=1
    if f.count == 0:
        f.set_result(None)


def wait_read_socket(fd):
    loop = asyncio.get_event_loop()
    fut = asyncio.Future(loop=loop)
    loop.add_reader(fd, fut.set_result,None)
    print("returning future %s" % str(fut))
    return fut

def wait_write_socket(fd):
    loop = asyncio.get_event_loop()
    print("1")
    fut = asyncio.Future(loop=loop)
    print("2")
    loop.add_writer(fd, fut.set_result,None)
    print("returning future %s" % str(fut))
    return fut
    

def wait_select(conn):
    """Wait until a connection or cursor has data available.                    
                                                                                
    The function is an example of a wait callback to be registered with         
    `~psycopg2.extensions.set_wait_callback()`. This function uses              
    :py:func:`~select.select()` to wait for data available.                     
                                                                                
    """
    import select
    from psycopg2.extensions import POLL_OK, POLL_READ, POLL_WRITE

    print("in supplied wait_select")

    while 1:
        state = conn.poll()
        if state == POLL_OK:
            break
        elif state == POLL_READ:
            select.select([conn.fileno()], [], [])
        elif state == POLL_WRITE:
            select.select([], [conn.fileno()], [])
        else:
            raise conn.OperationalError("bad state from poll: %s" % state)

def local_wait_select(conn):
    """Wait until a connection or cursor has data available.                    
                                                                                
    The function is an example of a wait callback to be registered with         
    `~psycopg2.extensions.set_wait_callback()`. This function uses              
    :py:func:`~select.select()` to wait for data available.                     
                                                                                
    """
    print("in wait select")
    from psycopg2.extensions import POLL_OK, POLL_READ, POLL_WRITE

    while 1:
        state = conn.poll()
        fileno = conn.fileno()
        loop = asyncio.get_event_loop()
        print(loop)
        if state == POLL_OK:
            print("file %d is OK" % fileno)
            break
        elif state == POLL_READ:
            print("file %d trying to read" % fileno)
            fut = wait_read_socket(fileno)
            print("run until completed "+ str(fut))
            loop.run_until_complete(fut)
            print("done run until completed "+ str(fut))
            #yield from fut
            loop.remove_reader(fileno)
        elif state == POLL_WRITE:
            print("file %d trying to write" % fileno)
            fut = wait_write_socket(fileno)
            print("run until completed "+ str(fut))
            loop.run_until_complete(fut)
            print("done run until completed "+ str(fut))
            #yield from fut
            loop.remove_writer(fileno)
        else:
            raise conn.OperationalError("bad state from poll: %s" % state)


def async_main():
    loop = asyncio.get_event_loop()
    print(loop)
    f = asyncio.Future()
    #psycopg2.extensions.set_wait_callback(local_wait_select)
    #psycopg2.extensions.set_wait_callback(wait_select)
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
