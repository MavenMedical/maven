###############################################################################################
#  Copyright (c) 2014 - Maven Medical
#
#  Description: database connection and query utilities
#  Author: Tom DuBois, Aidan Fowler
#  Description: Database connection pool utility, provides execute() and close() methods
#               There are two subclasses - asynchronous and single threaded
#
# Asynchronous:    1. Initialize class AsyncConnectionPool(config name, loop)
#                  2. Single Query (read) execute_single(query, extra parameters, future=None)
#                     Do not set the future if you are doing a single query, returns cursor
#                  3. Single Query (write) execute_and_close_single(query,extra parameters)
#                     This will close the cursor after querying, returns None
#                  4. Multiple Queries (read or write) execute_multiple(query, extra parameters,
#                     close) close is a boolean that determines if we want to close the cursor
#                     and not return results
#
# Single Threaded: 1. Initialize class SingleThreadedConnection(config name)
#                  2. Single Query (select) execute(query,extra parameters=None), returns the
#                     cursor, need to close later
#                  3. Single Query (non-select) execute_and_close(query,extra parameters=None)
#                     returns None, closes cursor
#
# MappingUtilities 1. select_rows_from_map(queryMap) takes in a list of column names, returns
#                     a string for easier query formatting
#                  2. generate_result_object takes in a cursor and list of column names and
#                     creates a mapping from name to result
#
# Side Effects:
#  Last Modified: FOR JIRA ISSUE: MAV-70 Wednesday February 26th
###############################################################################################

import psycopg2
import asyncio
import maven_logging as ML
import maven_config as MC
import traceback
from functools import lru_cache


@lru_cache()
class AsyncConnectionPool():
    """ ConnectionPool subclass supporting parallelism using asyncio and yield from
    Note that execute_single, execute_single_no_result, execute_multiple and
    mogrify_cursor must be called using 'yield from' as they are coroutines and not
    functions.  Every function above them in the call stack must also be called with
    'yield from' as well.  If your program hangs and you don't know why, that's why

    Note that we can only have one cursor actively interacting with a single connection at a time
    Read the 'Asynchronous support' section of http://initd.org/psycopg/docs/advanced.html
          "Two cursors can't execute concurrent queries on the same asynchronous connection"
    """

    CONFIG_MIN_CONNECTIONS = 'minimum connections'
    CONFIG_MAX_CONNECTIONS = 'maximum connections'
    CONFIG_CONNECTION_STRING = 'connection string'

    # noinspection PyArgumentList
    def __init__(self, name, loop=None):
        """ Initialize the AsyncConnectionPool
        :param name: The instance's name for configuration purposes
        :param loop: The event loop.
        """
        self.name = name

        self.ready = []  # the queue of ready database connections
        # Semaphore (using producer/consumer paradigm) to control waiting for the ready queue
        self.connection_sem = asyncio.Semaphore(0, loop=loop)

        self.in_use = set()  # the set of in use database connections
        self.mog_cursor = None  # keep a cursor around since mogrify isn't static for some reason

        self.MIN_CONNECTIONS = MC.MavenConfig[name][self.CONFIG_MIN_CONNECTIONS]
        self.MAX_CONNECTIONS = MC.MavenConfig[name][self.CONFIG_MAX_CONNECTIONS]
        self.CONNECTION_STRINGS = MC.MavenConfig[name][self.CONFIG_CONNECTION_STRING].splitlines()

        # create MIN_CONNECTIONS tasks, each of which will establish a connection to
        # prime the ready queue
        self.pending = self.MIN_CONNECTIONS
        if loop:
            self.schedule(loop)

    def schedule(self, loop):
        self.loop = loop
        tasks = [asyncio.Task(self._new_connection(), loop=loop)
                 for _ in range(self.MIN_CONNECTIONS)]
        ML.INFO('Starting %d connections' % self.pending)
        for t in tasks:
            ML.DEBUG(t)
            if not t.done():
                loop.run_until_complete(t)

    # noinspection PyArgumentList
    @asyncio.coroutine
    def execute_single(self, cmd, extra=None, future=None):
        """ Execute a single SQL command on a ready connection, returning the cursor associated with it.
        This cursor must be explicitly closed after use

        This function might block, and so it is a coroutine and must be called with 'yield from'
        :param cmd: The sql command to send to the database
        :param extra: any extra arguments to the database
        :param future: a future to hold the result if we are calling form multiple_queries
                       otherwise None
        """
        ML.DEBUG('About to execute %s' % str((cmd, extra)))
        ML.INFO('About to execute %s' % str(cmd))
        conn = yield from self._get_connection()  # get a connection, blocking if necessary
        if conn is None:
            ML.ERROR("Error establishing a connection with database")
            raise RuntimeError("You do not have a valid connection to the database")
        try:
            cur = conn.cursor()
            # ML.DEBUG("got a cursor")
            # Send the command to the database
            if extra:
                cur.execute(cmd, extra)
            else:
                cur.execute(cmd)

            # wait for a result from the database
            yield from self._wait(conn)

            # ML.DEBUG("Finish execution")
            # the cursor is an iterator through the results, return it
            if future is not None:
                ML.DEBUG("Setting future for one of multiple queries")
                future.set_result(cur)
            return cur
        except psycopg2.ProgrammingError as e:
            ML.ERROR("Error Querying Database: %s" % e)
            raise RuntimeError("There was an error querying the database")
        finally:
            if conn.closed:
                self.in_use.remove(conn)
                asyncio.Task(self._test_connection())  # see if other connections are dead too
                asyncio.Task(self._new_connection())
            else:
                self._release_connection(conn)  # put the connection back on the queue

    @asyncio.coroutine
    def execute_multiple(self, cmds, extras=None, close=None):
        """Execute multiple SQL commands on ready connections, returning the cursors associated
        with each query.  The cursors must be explicitly closed after use
        This function might block, so it is a coroutine and must be called with 'yield from'
        :param cmds the list of sql commands to send to the database
        :param extra any extra arguments to the database
        :param close: a boolean (or nothing) that determines if we will close the
                      cursors after the queries or return
        the list of cursors (True-> close the cursors, return None, !True -> return the cursors)
        """
        tasks = []
        futures = []
        cursors = []

        if extras is not None:
            if len(cmds) != len(extras):
                ML.ERROR("The length of the commands list is not equal to the length " +
                         "of the extras list")
                raise Exception("The length of the commands list is not equal to the " +
                                "length of the extras list")

        for x in range(len(cmds)):
            future = asyncio.Future()
            if extras is not None:
                tasks.append(asyncio.Task(self.execute_single(cmds[x], extras[x], future)))
            else:  # extras is None:
                tasks.append(asyncio.Task(self.execute_single(cmds[x], None, future)))
            futures.append(future)

        # ML.DEBUG("Sending multiple tasks to event loop and waiting until they all finish")
        yield from asyncio.wait(tasks)
        # ML.DEBUG("All tasks finished and futures set")
        for f in futures:
            if not f.done():
                ML.ERROR("We are trying to get the result of a future that has not completed")
                raise RuntimeError("We can not get the result of a future that has not completed")
            else:
                cursors.append(f.result())

        if close is not None:
            if close:
                ML.DEBUG("Closing cursors, user set close parameter to True")
                for c in cursors:
                    c.close()
                return None
            else:
                ML.DEBUG("Returning cursors, user set close parameter != True")
                return cursors
        else:
            ML.DEBUG("Returning cursors, user did not set a close parameter")
            return cursors

    @asyncio.coroutine
    def execute_and_close_single(self, cmd, extra=None):
        """ Works the same as execute, only closes the cursor afterward - for statements other than SELECT
        :param cmd: The sql command to send to the database
        :param extra: any extra arguments to the database
        """
        # ML.DEBUG("Executing query and closing cursor")
        cur = yield from self.execute_single(cmd, extra)
        if cur is None:
            ML.ERROR("The cursor returned from the query is null")
            raise RuntimeError("The cursor returned from the query is null and cannot be closed")
        cur.close()

    @asyncio.coroutine
    def _test_connection(self):
        if self.ready:
            try:
                cur = yield from self.execute_single('SELECT 1', None)
                cur.close()
            except:
                pass

    def close(self):
        """ Closes all of the connections managed by this connection pool
        This function most likely needs to be called from a descructor as
        well as a callback if the event loop closes
        """
        for conn in self.ready:
            conn.close()
        for conn in self.in_use:
            conn.close()

    @asyncio.coroutine
    def mogrify_cursor(self):
        """ A cursor is needed to use the mogrify function.  This is useful for doing a bulk insert
        (see unit tests for an example).  This seems like it should be a static function,
        but alas, we do it this way.
        """
        if not self.mog_cursor:  # keep a static mog_cursor around
            conn = yield from self._get_connection()  # get the mog_cursor it is None
            try:
                self.mog_cursor = conn.cursor()
            finally:
                self._release_connection(conn)
        return self.mog_cursor

    @asyncio.coroutine
    def _get_connection(self):
        """ Helper function which gets a ready connection from the queue,
        or suspends until one is available
        The semaphore MUST always make self.ready's size
        """

        # ML.DEBUG("In ConnectionPool._get_connection")
        # consume one of the connections if available, block otherwise
        yield from self.connection_sem.acquire()

        if len(self.ready) < 1:
            ML.ERROR("There are no available connections")
            raise RuntimeError("There are no available connections")

        connection = self.ready.pop()
        self.in_use.add(connection)

        # ML.DEBUG("Reused a connection: (%d, %d, %d)" % (len(self.ready), len(self.in_use),
        # self.pending))

        # create a new_connection task if ready queue (+ pending) is empty and there is headroom
        active = self.pending + len(self.ready) + len(self.in_use)
        if len(self.ready) + self.pending < 1 and active < self.MAX_CONNECTIONS:
            asyncio.Task(self._new_connection(), loop=self.loop)
            self.pending += 1
            ML.DEBUG("Launching a new connection task: (%d, %d, %d)"
                     % (len(self.ready), len(self.in_use), self.pending))
        return connection

    def _release_connection(self, connection):
        """ Clean up when done with a connection, and wake up any waiting coroutines
        :param connection: a psycopg2, async connection
        """
        # ML.DEBUG("Releasing Connection")
        self.in_use.remove(connection)
        self.ready.append(connection)
        self.connection_sem.release()

    @asyncio.coroutine
    def _new_connection(self):

        """ Create a new connection to the database, add it to the right queues,
        and wake up waiting coroutines
        """
        # Double check for headroom to make another connection
        if len(self.ready) + len(self.in_use) + self.pending <= self.MAX_CONNECTIONS:
            sleep_time = .1
            while sleep_time:
                try:
                    # make the connection with async=1, and wait for it to be ready
                    ML.DEBUG("trying to connect to %s" % self.CONNECTION_STRINGS[0])
                    connection_string = self.CONNECTION_STRINGS[0]
                    connection = psycopg2.connect(self.CONNECTION_STRINGS[0], async=1)
                    yield from self._wait(connection)
                    ML.INFO("Allocated a new connection")

                    # add it to the ready queue, and wake up any waiting coroutine
                    self.ready.append(connection)
                    self.connection_sem.release()
                    # whether or not a new connection is allocated, decrement self.pending
                    self.pending -= 1
                    sleep_time = 0
                except (psycopg2.DatabaseError, psycopg2.OperationalError):
                    ML.ERROR("The database had an operational error: " + traceback.format_exc())
                    if self.CONNECTION_STRINGS[0] == connection_string:
                        self.CONNECTION_STRINGS.append(self.CONNECTION_STRINGS.pop(0))
                    yield from asyncio.sleep(sleep_time)
                    sleep_time = sleep_time * 2
                    if sleep_time > 4:
                        sleep_time = 4
                except TypeError:
                    # This will catch all errors from which we can never recover.
                    ML.ERROR("The database was unable to connect: " + traceback.format_exc())
                    self.pending -= 1
                except:
                    ML.ERROR("An unexpected error occurred: " + traceback.format_exc())
                    self.pending -= 1
                    raise

    @asyncio.coroutine
    def _wait(self, connection):
        """ This is the key coroutine to make everything asynchronous.
        It polls the connection to test for doneness, if it's not done, it yields on the
        connection's file descriptor, letting other coroutines run until it's ready.
        :param connection: a psycopg2, async connection
        """
        # ML.DEBUG("In ConnectionPool.wait")
        while True:
            state = connection.poll()
            if state == psycopg2.extensions.POLL_OK:
                break
            elif state == psycopg2.extensions.POLL_WRITE:
                yield from AsyncConnectionPool.SocketReadyFuture(AsyncConnectionPool.SocketReadyFuture.write,
                                                                 connection.fileno(), self.loop)
            elif state == psycopg2.extensions.POLL_READ:
                yield from AsyncConnectionPool.SocketReadyFuture(AsyncConnectionPool.SocketReadyFuture.read,
                                                                 connection.fileno(), self.loop)
            else:
                raise psycopg2.OperationalError("poll() returned %s" % state)

    class SocketReadyFuture(asyncio.Future):
        """ Helper class which waits on a socket, then cleans up after itself
        """

        read = True
        write = False

        def __init__(self, is_reader, fileno, loop):
            # Adds self a watcher to the file descriptor fileno
            asyncio.Future.__init__(self)
            self.is_reader = is_reader
            self.loop = loop
            self.fileno = fileno
            if is_reader:
                loop.add_reader(fileno, self.wake_future)
            else:
                loop.add_writer(fileno, self.wake_future)

        def wake_future(self):
            # self.fileno is ready, remove the watcher, and wake up anything waiting on this future
            if self.is_reader:
                self.loop.remove_reader(self.fileno)
            else:
                self.loop.remove_writer(self.fileno)
            self.set_result(None)


class SingleThreadedConnection():
    """ Blocking Database Connection Utility. If you don't need asynchronous database access use
    execute(queryText,extras parameters=None) or
    execute_and_close(queryText, extra parameters=None)
    After you are done querying (execute only), the cursor must be manually closed
    """
    CONFIG_CONNECTION_STRING = 'connection string'

    def __init__(self, name):

        self.name = name
        self.CONNECTION_STRING = MC.MavenConfig[name][self.CONFIG_CONNECTION_STRING]
        self.connection = psycopg2.connect(self.CONNECTION_STRING)
        ML.DEBUG("Initialized single threaded connection to the database")

    def execute(self, query, extras=None):
        """This will query the database with or without extra parameters and return the cursor
        The cursor will need to be manually closed afterward
        """

        if self.connection is None:
            ML.ERROR("You cannot execute a query without being connected to the database")
            raise Exception("You are not connected to the database, check your " +
                            "connection string and try initialize class again")

        cursor = self.connection.cursor()

        if extras:
            cursor.execute(query, extras)
        else:
            cursor.execute(query)
        self.connection.commit()
        return cursor

    def execute_and_close(self, query, extras=None):
        """This private method gets called when we want to execute a query with
        no return values (INSERT, DELETE, UPDATE).  There is no need to close the
        cursor after doing a write query, it is closed before returning None
        """

        if self.connection is None:
            raise RuntimeError("You are not connected to the database, check your " +
                               "connection string and try initialize class again")

        cursor = self.connection.cursor()
        if extras:
            cursor.execute(query, extras)
        else:
            cursor.execute(query)
        self.connection.commit()
        cursor.close()
        return None


class MappingUtilites():
    """Utilities to make writing queries easier and to generate objects based
    on query results and column-name map
    """

    def select_rows_from_map(self, queryMap):
        """This method allows us to generate a list of columns we would like to retrieve
        from a select query map.  All this is really doing is generating a string that is
        a list of the column names we want to retrieve.
        Example: if we have defined our result map as EXAMPLE_MAP = ["col1","col2","col3"],
        this method returns "col1,col2,col3"

        And we can run query:
        execute_read("SELECT %s FROM Table" % select_rows_from_map(EXAMPLE_MAP))
        """
        params = ""
        for x in queryMap:
            if x:
                params = params + x + ","
        return params[:-1]

    def generate_result_object(self, cursor, queryMap):
        """This method allows us to create an object based on the results of a query
        (stored in a cursor) and a mapping to column names, the mapping is a list of
        column names in strings: EXAMPLE_MAP = ["col1","col2","col3"]" if the cursor holds
        res1,res2,res3, this method will generate an object [{'col1':res1,'col2':res2,'col3:res3}]
        """
        results = []
        for res in cursor:
            singleResult = {}
            i = 0
            for value in res:
                singleResult[queryMap[i]] = str(value)
                i += 1
            results.append(singleResult)
        return results
