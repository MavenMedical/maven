####################################################################################################
#  Copyright (c) 2014 - Maven Medical
#
#  Description: database connection and query utilities
#  Author: Tom DuBois
#  Description: Database connection pool utility, provides execute() and close() methods
#               There are two subclasses - asynchronous and single threaded
#
# Side Effects:
#  Last Modified: FOR JIRA ISSUE: MAV-70 Wednesday February 19th
#####################################################################################################

import asyncio
from app.database_utils.database import AsyncConnectionPool
import maven_config as MC


@asyncio.coroutine
def db_main(ident, conn):
    """
    :param ident: a string labeling this instance
    :param conn: the AsyncConnectionPool to connect to the database
    """
    yield from conn.execute_and_close('drop table TomTest'+ident)

    yield from conn.execute_and_close('create table TomTest'+ident
                                      +' (id serial PRIMARY KEY, num integer, data varchar);')
    rows = []
    for i in range(100000):
        rows.append((i, 'string %d' % i))
    mog_cursor = yield from conn.mogrify_cursor()
    args_str = b','.join(mog_cursor.mogrify("%s", (x, )) for x in rows)
    yield from conn.execute_and_close("INSERT INTO tomtest"+ident+" (num, data) VALUES "+args_str.decode("utf-8"))
    cur = yield from conn.execute('select * from TomTest'+ident)
    l = []
    for x in cur:
        l.append(x)
    cur.close()


@asyncio.coroutine
def process(loop, ident, conn):
    for x in range(3):
        print("hello from %s" % ident)
        yield from db_main(ident, conn)
        print("%s sleeping" % ident)
        yield from asyncio.sleep(.5)
        print("%s woke up" % ident)


def async_main():
    loop = asyncio.get_event_loop()
    print(loop)
    conn = AsyncConnectionPool('test conn pool', loop)
    tasks = [asyncio.Task(process(loop, x, conn)) for x in ['p1', 'p2', 'p3', 'x']]
    print("Starting loop")
    loop.run_until_complete(asyncio.wait(tasks))

MC.MavenConfig = {
    'test conn pool': {
        AsyncConnectionPool.CONFIG_CONNECTION_STRING:
        ("dbname=%s user=%s password=%s host=%s port=%s" % ('maven', 'maven', 'temporary', 'localhost', '5432')),
        AsyncConnectionPool.CONFIG_MIN_CONNECTIONS: 4,
        AsyncConnectionPool.CONFIG_MAX_CONNECTIONS: 8
    }
}

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
