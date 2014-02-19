##############################################################################
#  Copyright (c) 2014 - Maven Medical
#
#  Description: Unit test for database utilities
#  Author: Aidan Fowler
#  Assumes: The Query Mapping is defined in the app.database_utils.dbconfig file
#  Side Effects:
#  Last Modified: FOR JIRA ISSUE: MAV-70 Monday February 17th
##############################################################################


from app.database_utils.db_utils import DatabaseUtility as DBU
from app.database_utils.dbconfig import RULE_TABLE_MAPPING

import unittest
import time
class TestDatabaseUtils(unittest.TestCase):


    def testConnectDisconnect(self):
        db_utils= DBU()

        #Test that calling connect establishes a connection
        db_utils.connect()
        self.assertNotEqual(None,db_utils.connection)

        #Test that if the connection exists, we can not establish another connection
        with self.assertRaises(RuntimeError):
            db_utils.connect()

        #Test that disconnecting works
        db_utils.disconnect()
        self.assertEqual(None,db_utils.connection)

    def testCursor(self):
        db_utils = DBU()
        db_utils.connect()

        #Test that we can create a cursor
        db_utils.create_cursor()
        self.assertNotEqual(None,db_utils.cursor)

        #Test that if a cursor exists, we can not create another cursor
        with self.assertRaises(RuntimeError):
            db_utils.create_cursor()

        #Test that we destroy cursors properly
        db_utils.destroy_cursor()
        self.assertEqual(None,db_utils.cursor)

        #Test that we can not destroy a cursor if it does not exist
        with self.assertRaises(RuntimeError):
            db_utils.destroy_cursor()

        db_utils.disconnect()

        #Test that we can not create a cursor if the connection is not established
        with self.assertRaises(RuntimeError):
            db_utils.create_cursor()

        #Test that we can not destroy a cursor if the connection is not established
        with self.assertRaises(RuntimeError):
            db_utils.destroy_cursor()


    def testQuery(self):
        db_utils = DBU()
        db_utils.connect()
        db_utils.create_cursor()
        db_utils.query_database_write_blocking("DELETE FROM ruleTest.rules")


        db_utils.query_database_write_blocking("INSERT INTO ruleTest.rules VALUES ('Rule 1','Description 1','proc',12345,0,200,'11111111','01111111','Details1','dept1','dept2');")

        res = db_utils.query_database_read_blocking("SELECT * FROM RuleTest.rules")
        self.assertEqual(1,len(res))

        queryParameters = db_utils.select_rows_from_map(RULE_TABLE_MAPPING)
        res = db_utils.query_database_read_blocking("SELECT %s FROM ruleTest.rules WHERE orderedCPT = 12345" % queryParameters, RULE_TABLE_MAPPING)

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

        db_utils.query_database_write_blocking("INSERT INTO ruleTest.rules VALUES ('Rule 2','Description 2','proc',12345,0,200,'11111111','01111111','Details2','dept1','dept2');")
        res = db_utils.query_database_read_blocking("SELECT %s FROM ruleTest.rules WHERE orderedCPT = 12345" % queryParameters, RULE_TABLE_MAPPING)
        self.assertEqual(2,len(res))

        db_utils.query_database_write_blocking("UPDATE ruleTest.rules SET ruleName = 'Rule 3' WHERE ruleName = 'Rule 2';")
        res = db_utils.query_database_read_blocking("SELECT ruleName from ruleTest.rules WHERE orderedCPT = 12345 AND ruleName = 'Rule 3';")
        self.assertEqual(1,len(res));

