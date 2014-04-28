####################################################################################################
#  Copyright (c) 2014 - Maven Medical
#
#  Description: database connection and query utilities
#  Author: Tom DuBois, Aidan Fowler
#  Description: Database connection pool utility, provides execute() and close() methods
#               There are two subclasses - asynchronous and single threaded
#
# Assumes there is a table in the database called RuleTest.rules
# Side Effects:
#  Last Modified: FOR JIRA ISSUE: MAV-70 Wednesday February 26th
#####################################################################################################

import unittest

import asyncio

from utils.database.database import AsyncConnectionPool,SingleThreadedConnection, MappingUtilites
import maven_config as MC


global multiple
multiple = False

class TestAsyncDatabase(unittest.TestCase):

    @asyncio.coroutine
    def db_main(self,ident, conn):
        """
        :param ident: a string labeling this instance
        :param conn: the AsyncConnectionPool to connect to the database
        """
        global multiple

        yield from conn.execute_and_close_single('drop table if exists TomTest'+ident)
        yield from conn.execute_and_close_single('create table TomTest'+ident
                                          +' (id serial PRIMARY KEY, num integer, data varchar);')
        rows = []
        for i in range(10000):
            rows.append((i, 'string %d' % i))
        mog_cursor = yield from conn.mogrify_cursor()
        args_str = b','.join(mog_cursor.mogrify("%s", (x, )) for x in rows)
        yield from conn.execute_and_close_single("INSERT INTO tomtest"+ident+" (num, data) VALUES "+args_str.decode("utf-8"))

        if multiple == False:
            cur = yield from conn.execute_single('select * from TomTest'+ident)
            res = []
            for x in cur:
                res.append(x)
            cur.close()
            self.assertEqual(10000,len(res))

        elif multiple == True:
            queries = []
            queries.append('select * from TomTest'+ident+' where data = \'string 1\'')
            queries.append('select * from TomTest'+ident+' where data = \'string 2\'')
            queries.append('select * from TomTest'+ident+' where data = \'string 3\'')
            queries.append('select * from TomTest'+ident+' where data = \'string 4\'')
            queries.append('select * from TomTest'+ident+' where data = \'string 5\'')
            queries.append('select * from TomTest'+ident+' where data = \'string 6\'')
            cursors = yield from conn.execute_multiple(queries,None,False)
            res = []
            for cur in cursors:
                for x in cur:
                    res.append(x)
                #cur.close()
                #todo i think there is a bug somewhere but cant find it - > if we run this with cur.close() we get the following error
                #todo psycopg2.ProgrammingError: close cannot be used while an asynchronous query is underway
                #todo it seems to me that the cursors should correspond to different connections and this error should not be happening
                #todo NOTE: this is not always replicable, sometimes it takes a few runs of the unit test to come up
            #print("res:",res," ident:",ident)
            self.assertEqual(6,len(res))

    @asyncio.coroutine
    def process(self,loop, ident, conn):
        prints_on = False
        #print("3 Tasks Processing...")
        for x in range(3):
            if prints_on: print("hello from %s" % ident)
            yield from self.db_main(ident, conn)
            if prints_on: print("%s sleeping" % ident)
            yield from asyncio.sleep(.05)
            if prints_on: print("%s woke up" % ident)
            #print("Task Finished")

    def test_async_main(self):
        """This is the test for the async database connection, we create three tasks that run three times.
        Each task updates a table with 10000 values and does some queries on the table"""
        global multiple
        multiple = True
        loop = asyncio.get_event_loop()
        #print(loop)
        conn = AsyncConnectionPool('test conn pool', loop)
        tasks = [asyncio.Task(self.process(loop, x, conn)) for x in ['p1', 'p2', 'p3', 'x']]
        #print("Starting loop")
        loop.run_until_complete(asyncio.wait(tasks))
        multiple = False
        tasks = [asyncio.Task(self.process(loop, x, conn)) for x in ['p1', 'p2', 'p3', 'x']]
        loop.run_until_complete(asyncio.wait(tasks))
        #print ("done with async test")

class TestBlockingDB(unittest.TestCase):
    """These tests check that the single threaded database connection and query work as well as mapping utilites"""

    RULE_TABLE_MAPPING = ("ruleName","ruleDescription","orderType","orderedCPT","minAge","maxAge","withDX","withoutDX","details","onlyInDept","notInDept")
    def testInitializeBlockingDatabase(self):
        db_blocking = SingleThreadedConnection('test blocking')
        self.assertNotEqual(None,db_blocking.connection)

    def testQuery(self):
        db_blocking = SingleThreadedConnection('test blocking')
        db_blocking.execute_and_close("DELETE FROM ruleTest.rules")
        db_blocking.execute_and_close("INSERT INTO ruleTest.rules VALUES ('Rule 1','Description 1','proc',12345,0,200,'11111111','01111111','Details1','dept1','dept2');")

        cursor = db_blocking.execute("SELECT * FROM RuleTest.rules")
        res=[]
        for r in cursor:
            res.append(r)
        cursor.close()

        self.assertEqual(1,len(res))
        map_util = MappingUtilites()
        queryParameters = map_util.select_rows_from_map(self.RULE_TABLE_MAPPING)

        cursor = db_blocking.execute("SELECT %s FROM ruleTest.rules WHERE orderedCPT = 12345" % queryParameters, None)
        res = map_util.generate_result_object(cursor,self.RULE_TABLE_MAPPING)
        cursor.close()

        self.assertEqual(1,len(res))
        self.assertEqual(res[0]["ruleName"],"Rule 1")
        self.assertEqual(res[0]["ruleDescription"],"Description 1")
        self.assertEqual(res[0]["orderType"],"proc")
        self.assertEqual(res[0]["orderedCPT"],"12345")
        self.assertEqual(res[0]["minAge"],"0")
        self.assertEqual(res[0]["maxAge"],"200")
        self.assertEqual(res[0]["withDX"],"11111111")
        self.assertEqual(res[0]["withoutDX"],"01111111")
        self.assertEqual(res[0]["details"],"Details1")
        self.assertEqual(res[0]["onlyInDept"],"dept1")
        self.assertEqual(res[0]["notInDept"],"dept2")
        db_blocking.execute_and_close("INSERT INTO ruleTest.rules VALUES ('Rule 2','Description 2','proc',12345,0,200,'11111111','01111111','Details2','dept1','dept2');")

        cursor = db_blocking.execute("SELECT %s FROM ruleTest.rules WHERE orderedCPT = 12345" % queryParameters, None)
        res = []
        for r in cursor:
            res.append(r)
        cursor.close()

        self.assertEqual(2,len(res))
        db_blocking.execute_and_close("UPDATE ruleTest.rules SET ruleName = 'Rule 3' WHERE ruleName = 'Rule 2';")

        cursor=db_blocking.execute("SELECT ruleName from ruleTest.rules WHERE orderedCPT = 12345 AND ruleName = 'Rule 3';")
        res =[]
        for r in cursor:
            res.append(r)
        self.assertEqual(1,len(res))
        cursor.close()


MC.MavenConfig = {
    'test conn pool': {
        AsyncConnectionPool.CONFIG_CONNECTION_STRING:
        ("dbname=%s user=%s password=%s host=%s port=%s" % ('maven', 'maven', 'temporary', 'localhost', '5432')),
        AsyncConnectionPool.CONFIG_MIN_CONNECTIONS: 4,
        AsyncConnectionPool.CONFIG_MAX_CONNECTIONS: 8
    },
    'test blocking': {
        SingleThreadedConnection.CONFIG_CONNECTION_STRING:
            ("dbname=%s user=%s password=%s host=%s port=%s" % ('maven', 'maven', 'temporary', 'localhost', '5432'))
    }
}

tab = TestAsyncDatabase()
tab.test_async_main()


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
