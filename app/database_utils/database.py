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

import psycopg2
import asyncio

import maven_logging as ML
import maven_config as MC


class AsyncConnectionPool():
    """ ConnectionPool subclass supporting parallelism using asyncio and yield from
    Note that execute, execute_no_result, and mogrify_cursor must be called using 'yield from'
    as they are coroutines and not functions.  Every function above them in the call stack must
    also be called with 'yield from' as well.  If your program hangs and you don't know why, that's why

    Note that we can only have one cursor actively interacting with a single connection at a time
    Read the 'Asynchronous support' section of http://initd.org/psycopg/docs/advanced.html
      'Two cursors can’t execute concurrent queries on the same asynchronous connection'
    """

    CONFIG_MIN_CONNECTIONS = 'minimum connections'
    CONFIG_MAX_CONNECTIONS = 'maximum connections'
    CONFIG_CONNECTION_STRING = 'connection string'

    # noinspection PyArgumentList
    def __init__(self, name, loop):
        """ Initialize the AsyncConnectionPool
        :param name: The instance's name (for pulling configuration information out of MC.MavenConfig
        :param loop: The event loop.
        """
        self.name = name

        self.ready = []  # the queue of ready database connections
        # Semaphore (using producer/consumer paradigm) to control waiting for the ready queue
        self.connection_sem = asyncio.Semaphore(0, loop=loop)

        self.in_use = set()  # the set of in use database connections
        self.loop = loop  # the event loop
        self.mog_cursor = None  # keep a cursor around since mogrify isn't static for some reason

        self.MIN_CONNECTIONS = MC.MavenConfig[name][self.CONFIG_MIN_CONNECTIONS]
        self.MAX_CONNECTIONS = MC.MavenConfig[name][self.CONFIG_MAX_CONNECTIONS]
        self.CONNECTION_STRING = MC.MavenConfig[name][self.CONFIG_CONNECTION_STRING]

        # create MIN_CONNECTIONS tasks, each of which will establish a connection to prime the ready queue
        self.pending = self.MIN_CONNECTIONS
        [asyncio.Task(self._new_connection(), loop=loop) for _ in range(self.MIN_CONNECTIONS)]
        ML.DEBUG('starting %d connections' % self.pending)

    # noinspection PyArgumentList
    @asyncio.coroutine
    def execute(self, cmd, extra=None):
        """ Execute a SQL command on a ready connection, returning the cursor associated with it.
        This cursor must be explicitly closed after use

        This function might block, and so it is a coroutine and must be called with 'yield from'
        :param cmd: The sql command to send to the database
        :param extra: any extra arguments to the database
        """

        ML.DEBUG('about to execute %s' % (cmd.split(' ', 1)[0]))
        conn = yield from self._get_connection()  # get a connection, blocking if necessary
        try:
            cur = conn.cursor()
            #ML.DEBUG("got a cursor")
            # Send the command to the database
            if extra:
                cur.execute(cmd, extra)
            else:
                cur.execute(cmd)

            # wait for a result from the database
            yield from self._wait(conn)
            ML.DEBUG("finish execution")
            # the cursor is an iterator through the results, return it
            return cur
        finally:
            self._release_connection(conn)  # put the connection back on the queue

    def execute_and_close(self, cmd, extra=None):
        """ Works the same as execute, only closes the cursor afterward - for statements other than SELECT
        :param cmd: The sql command to send to the database
        :param extra: any extra arguments to the database
        """
        cur = yield from self.execute(cmd, extra)
        cur.close()

    def close(self):
        """ Closes all of the connections managed by this connection pool
        This function most likely needs to be called from a descructor as well as a callback if the event loop closes
        """
        for conn in self.ready:
            conn.close()
        for conn in self.in_use:
            conn.close()

    @asyncio.coroutine
    def mogrify_cursor(self):
        """ A cursor is needed to use the mogrify function.  This is useful for doing a bulk insert
         (see unit tests for an example).  This seems like it should be a static function, but alas, we do it this way.
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
        """ Helper function which gets a ready connection from the queue, or suspends until one is available
        The semaphore MUST always make self.ready's size
        """
        #ML.DEBUG("in ConnectionPool._get_connection")
        # consume one of the connections if available, block otherwise
        yield from self.connection_sem.acquire()
        connection = self.ready.pop()
        self.in_use.add(connection)

        ML.DEBUG("reused a connection: (%d, %d, %d)" % (len(self.ready), len(self.in_use), self.pending))

        # create a new_connection task if the ready queue (+ pending) is empty and there is headroom
        active = self.pending + len(self.ready) + len(self.in_use)
        if len(self.ready) + self.pending < 1 and active < self.MAX_CONNECTIONS:
            asyncio.Task(self._new_connection(), loop=self.loop)
            self.pending += 1
            ML.DEBUG("launching a new connection task: (%d, %d, %d)"
                     % (len(self.ready), len(self.in_use), self.pending))
        return connection

    def _release_connection(self, connection):
        """ Clean up when done with a connection, and wake up any waiting coroutines
        :param connection: a psycopg2, async connection
        """
        self.in_use.remove(connection)
        self.ready.append(connection)
        self.connection_sem.release()

    @asyncio.coroutine
    def _new_connection(self):
        """ Create a new connection to the database, add it to the right queues, and wake up waiting coroutines
        """
        # Double check for headroom to make another connection
        if len(self.ready) + len(self.in_use) + self.pending <= self.MAX_CONNECTIONS:
            # make the connection with async=1, and wait for it to be ready
            connection = psycopg2.connect(self.CONNECTION_STRING, async=1)
            yield from self._wait(connection)
            ML.DEBUG("allocated a new connection")

            # add it to the ready queue, and wake up any waiting coroutine
            self.ready.append(connection)
            self.connection_sem.release()
        # whether or not a new connection is allocated, decrement self.pending
        self.pending -= 1
        
    @asyncio.coroutine
    def _wait(self, connection):
        """ This is the key coroutine to make everything asynchronous.
        It polls the connection to test for doneness, if it's not done, it yields on the
        connection's file descriptor, letting other coroutines run until it's ready.
        :param connection: a psycopg2, async connection
        """
        #ML.DEBUG("in ConnectionPool.wait")
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
