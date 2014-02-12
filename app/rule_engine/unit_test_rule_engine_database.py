##############################################################################
#  Copyright (c) 2014 - Maven Medical
#
#  Description: Test the Database Connection and Rule Engine Test Table ruleTest.rules
#  Author: Aidan Fowler
#  Assumes: The maven database exists and there is a  ruleTest.rules table in it
#  Side Effects: Will clear ruleTest.rules table
#  Last Modified: FOR JIRA ISSUE: MAV-40 Wednesday February 12th
##############################################################################
import unittest
import psycopg2

global conn, cursor
conn=None
cursor = None

class TestRulesEngineDatabase(unittest.TestCase):

    def setUp(self):
        #connect to database, use global connection and cursor
        global cursor, conn
        conn_string = "host='localhost' dbname='maven' user='maven' password='temporary'"
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

    def tearDown(self):
        global conn, cursor
        cursor.execute("DELETE FROM ruleTest.rules;")
        conn.commit()

    def testConnection(self):
        #assert that the connection worked and is not null
        global conn
        self.assertNotEqual(conn, None)

    def testRulesTableSize(self):
        #assert that the number of columns in the table is 11 and that we can not add rows without 11 values
        global cursor,conn
        cursor.execute("DELETE FROM ruleTest.rules")
        insertQuery1 = "INSERT INTO ruleTest.rules VALUES ('Rule 1','Description 1','proc',12345,0,200,'11111111','01111111','Details1','dept1','dept1');"
        cursor.execute(insertQuery1)
        conn.commit()
        cursor.execute("SELECT * FROM ruleTest.rules;")
        table = []
        for res in cursor:
            table.append(res)
        self.assertEqual(11,len(table[0]))

        with self.assertRaises(psycopg2.ProgrammingError):
            cursor.execute("INSERT INTO ruleTest.rules VALUES ('1','2','3',4,5,6,'7','7','a','b','c','d');")


