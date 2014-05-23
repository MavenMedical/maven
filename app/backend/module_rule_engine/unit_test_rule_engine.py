##############################################################################
#  Copyright (c) 2014 - Maven Medical
#
#  Description: Tests for the rule engine
#  Author: Aidan Fowler
#  Assumes: We can access the local maven database and there is a table called ruleTest.rules
#  Side Effects: Test will destroy whatever data is stored in the ruleTest.rules Table
#  Last Modified: FOR JIRA ISSUE: MAV-40 Wednesday February 12th
##############################################################################
import unittest
import psycopg2
from app.backend.module_rule_engine.order_evaluator import OrderEvaluator
from app.backend.module_rule_engine.engine import RuleEngine
from app.backend.module_rule_engine.order_object import OrderObject

global conn, cursor
conn=None
cursor = None

class TestRulesEngineDatabase(unittest.TestCase):
#There will be two database connections, one is necessary for inserting values into the table so we can test, the other is the normal Evaluate Order connection
    @classmethod
    def setUpClass(cls):
        #connect to database, use global connection and cursor
        global cursor, conn
        conn_string = "host='localhost' dbname='maven' user='maven' password='temporary'"
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        #Initialize Order Evaluator, Rule Engine, and set up logging,
        cls.OE = OrderEvaluator()
        cls.OE.Logger.setLogging(True)
        cls.RE = RuleEngine(cursor,cls.OE.Logger)

    def tearDown(self):
        self.clear()

    def clear(self):
        global conn, cursor
        cursor.execute("DELETE FROM ruleTest.rules;")
        conn.commit()

    def testConnection(self):
        print("\nTest Connection")
        #assert that the connection worked and is not null
        self.assertNotEqual(self.OE.cursor, None)

    # This section of tests unit tests the checks the internal methods that the rule engine uses

    def testAgePositive(self):
        print("\nTest Age Logic 1")
        #Test that the age logic works for good input'
        self.assertEqual(True, self.RE.check_age(0,200,50))
        self.assertEqual(True, self.RE.check_age(0,200,0))
        self.assertEqual(True, self.RE.check_age(0,200,200))
        self.assertEqual(True, self.RE.check_age(0,200,1))
        self.assertEqual(True, self.RE.check_age(0,200,199))

    def testAgeNegative(self):
        print("\nTest Age Logic 2")
        #Test that the age logic works for bad input
        self.assertEqual(False, self.RE.check_age(0,200,-1))
        self.assertEqual(False, self.RE.check_age(0,200,201))

    def testSnomedInclusionPositive(self):
        print("\nTest SnomedId Logic 1")
        #Test that the snomed inclusion logic works for good input
        self.assertEqual(True, self.RE.check_inclusion_dx([11111111],[11111111]))
        self.assertEqual(True, self.RE.check_inclusion_dx([11111111],[11111111,22222222]))
        self.assertEqual(True, self.RE.check_inclusion_dx([11111111,22222222],[11111111,22222222]))
        self.assertEqual(True, self.RE.check_inclusion_dx([11111111,22222222,33333333],[11111111,22222222,33333333]))
        self.assertEqual(True, self.RE.check_inclusion_dx([],[11111111]))

    def testSnomedInclusionNegative(self):
        print("\nTest SnomedId Logic 2")
        #Test that the snomed inclusion logic works for bad input
        self.assertEqual(False, self.RE.check_inclusion_dx([11111111],[]))
        self.assertEqual(False, self.RE.check_inclusion_dx([11111111],[22222222]))
        self.assertEqual(False, self.RE.check_inclusion_dx([11111111,22222222],[11111111]))
        self.assertEqual(False, self.RE.check_inclusion_dx([11111111,22222222,33333333],[11111111,33333333]))

    def testSnomedExclusionPositive(self):
        print("\nTest SnomedId Logic 3")
        #Test that the snomed exclusion logic works for good input
        self.assertEqual(True, self.RE.check_exclusion_dx([],[11111111]))
        self.assertEqual(True, self.RE.check_exclusion_dx([22222222],[11111111]))

    def testSnomedExclusionNegative(self):
        print("\nTest SnomedId Logic 4")
        #Test that the snomed exclusion logic works for bad input
        self.assertEqual(False, self.RE.check_exclusion_dx([11111111],[11111111]))
        self.assertEqual(False, self.RE.check_exclusion_dx([11111111],[11111111,22222222]))
        self.assertEqual(False, self.RE.check_exclusion_dx([11111111],[22222222,11111111]))
        self.assertEqual(False, self.RE.check_exclusion_dx([11111111,22222222],[22222222]))

    def testDeptInclusionPositive(self):
        print("\nTest Dept Logic 1")
        #Test that the department inclusion logic works for good input
        self.assertEqual(True, self.RE.check_inclusion_dept(['ABC'],'ABC'))
        self.assertEqual(True, self.RE.check_inclusion_dept([''],'ABC'))
        self.assertEqual(True, self.RE.check_inclusion_dept(['ABC','DEF','HIG'],'HIG'))

    def testDepInclusionNegative(self):
        print("\nTest Dept Logic 2")
        #Test that the department inclusion logic works for bad input
        self.assertEqual(False, self.RE.check_inclusion_dept(['ABC'],'CBA'))
        self.assertEqual(False, self.RE.check_inclusion_dept(['ABC','DEF','HIG'],'CBA'))
        self.assertEqual(False, self.RE.check_inclusion_dept(['ABC'],''))

    def testDeptExclusionPositive(self):
        print("\nTest Dept Logic 3")
        #Test that the department exclusion logic works for good input
        self.assertEqual(True, self.RE.check_exclusion_dept(['ABC'],'CBA'))
        self.assertEqual(True, self.RE.check_exclusion_dept([''],'CBA'))
        self.assertEqual(True, self.RE.check_exclusion_dept([''],''))
        self.assertEqual(True, self.RE.check_exclusion_dept(['ABC','DEF','HIG'],''))
        self.assertEqual(True, self.RE.check_exclusion_dept(['ABC','DEF','HIG'],'CBA'))

    def testDeptExclusionNegative(self):
        print("\nTest Dept Logic 4")
        #Test that the department exclusion logic works for bad input
        self.assertEqual(False, self.RE.check_exclusion_dept(['ABC'],'ABC'))
        self.assertEqual(False, self.RE.check_exclusion_dept(['ABC','DEF','GHI'],'ABC'))
        self.assertEqual(False, self.RE.check_exclusion_dept(['ABC','DEF','GHI'],'GHI'))



    def testRuleEngineAge(self):
        #This tests that the correct logic gets followed for different ages
        print("\nTest Engine -> Age")
        global cursor, conn
        self.clear()

        #Rule Name, Rule Description, Order Type, CPT Code, Min Age, Max Age, Inclusion ID(s), Exclusion ID(s), Details, Inclusion Dept, Exlusion Dept
        insertQuery1 = "INSERT INTO ruleTest.rules VALUES ('Rule 1','Description 1','proc',12345,0,200,'11111111','01111111','Details1','dept1','dept2');"
        insertQuery2 = "INSERT INTO ruleTest.rules VALUES ('Rule 2','Description 2','proc',12345,0,10,'11111111','01111111','Details2','dept1','dept2');"
        cursor.execute(insertQuery1)
        cursor.execute(insertQuery2)
        conn.commit()

        #should be 2 matches
        order = OrderObject(1,['proc',12345,10,[11111111],'dept1'])
        evalResult = self.OE.evaluate_object(order).text()
        self.assertEqual(2,len(evalResult))

        #should be 2 matches
        order = OrderObject(1,['proc',12345,0,[11111111],'dept1'])
        evalResult = self.OE.evaluate_object(order).text()
        self.assertEqual(2,len(evalResult))

        #shold be 1 matches
        order = OrderObject(1,['proc',12345,200,[11111111],'dept1'])
        evalResult = self.OE.evaluate_object(order).text()
        self.assertEqual(1,len(evalResult))

        #shold be 0 matches
        order = OrderObject(1,['proc',12345,201,[11111111],'dept1'])
        evalResult = self.OE.evaluate_object(order).text()
        self.assertEqual(0,len(evalResult))

        #shold be 0 matches
        order = OrderObject(1,['proc',12345,-1,[11111111],'dept1'])
        evalResult = self.OE.evaluate_object(order).text()
        self.assertEqual(0,len(evalResult))

    def testRuleEngineCPT(self):
        #This tests that the rule matching based on CPT code works
        print("\nTest Engine -> CPT")
        global cursor, conn
        self.clear()

        #Rule Name, Rule Description, Order Type, CPT Code, Min Age, Max Age, Inclusion ID(s), Exclusion ID(s), Details, Inclusion Dept, Exlusion Dept
        insertQuery1 = "INSERT INTO ruleTest.rules VALUES ('Rule 1','Description 1','proc',12345,0,200,'11111111','01111111','Details1','dept1','dept2');"
        insertQuery2 = "INSERT INTO ruleTest.rules VALUES ('Rule 2','Description 2','med',12345,0,200,'11111111','01111111','Details2','dept1','dept2');"
        insertQuery3 = "INSERT INTO ruleTest.rules VALUES ('Rule 3','Description 3','proc',12345,0,200,'11111111','01111111','Details3','dept1','dept2');"
        insertQuery4 = "INSERT INTO ruleTest.rules VALUES ('Rule 4','Description 4','proc',12346,0,200,'11111111','01111111','Details4','dept1','dept2');"
        cursor.execute(insertQuery1)
        cursor.execute(insertQuery2)
        cursor.execute(insertQuery3)
        cursor.execute(insertQuery4)
        conn.commit()
        order = OrderObject(1,['proc',12345,10,[11111111,22222222],'dept1'])

        #Check that we get the correct evaluation for the above order (2 matches)
        evalResult = self.OE.evaluate_object(order).text()
        self.assertEqual(2,len(evalResult))

        order = OrderObject(1,['proc',1234,10,[11111111,22222222],'dept1'])
        #Check that we get the correct evaluation for the above order (0 matches)
        evalResult = self.OE.evaluate_object(order).text()
        self.assertEqual(0,len(evalResult))

    def testRuleEngineInclusionIds(self):
        #This test that the evaluation works from start to end, specifically testing the Inclusion ID principle
        print("\nTest Engine -> Inclusion Ids")
        global cursor, conn
        self.clear()

        #Rule Name, Rule Description, Order Type, CPT Code, Min Age, Max Age, Inclusion ID(s), Exclusion ID(s), Details, Inclusion Dept, Exlusion Dept
        insertQuery1 = "INSERT INTO ruleTest.rules VALUES ('Rule 1','Description 1','proc',12345,0,200,'11111111','01111111','Details1','dept1','dept2');"
        insertQuery2 = "INSERT INTO ruleTest.rules VALUES ('Rule 2','Description 2','proc',12345,0,200,'11111111,22222222','01111111','Details2','dept1','dept2');"
        insertQuery3 = "INSERT INTO ruleTest.rules VALUES ('Rule 3','Description 3','proc',12345,0,200,'11111111, 22222222','01111111','Details3','dept1','dept2');"
        insertQuery4 = "INSERT INTO ruleTest.rules VALUES ('Rule 4','Description 4','proc',12345,0,200,'','01111111','Details4','dept1','dept2');"
        cursor.execute(insertQuery1)
        cursor.execute(insertQuery2)
        cursor.execute(insertQuery3)
        cursor.execute(insertQuery4)
        conn.commit()

        #should match rule 1 and 4
        order = OrderObject(1,['proc',12345,10,[11111111],'dept1'])
        evalResult = self.OE.evaluate_object(order).text()
        self.assertEqual(2,len(evalResult))

        #shold match all 4 rules
        order = OrderObject(1,['proc',12345,10,[11111111,22222222],'dept1'])
        evalResult = self.OE.evaluate_object(order).text()
        self.assertEqual(4,len(evalResult))

        #should match all 4 rules
        order = OrderObject(1,['proc',12345,10,[11111111,22222222,33333333],'dept1'])
        evalResult = self.OE.evaluate_object(order).text()
        self.assertEqual(4,len(evalResult))

    def testRuleEngineExclusionIds(self):
        #This test that the evaluation works from start to end, specifically testing the Exclusion ID principle
        print("\nTest Engine -> Exclusion IDs")
        global cursor, conn
        self.clear()

        #Rule Name, Rule Description, Order Type, CPT Code, Min Age, Max Age, Inclusion ID(s), Exclusion ID(s), Details, Inclusion Dept, Exlusion Dept
        insertQuery1 = "INSERT INTO ruleTest.rules VALUES ('Rule 1','Description 1','proc',12345,0,200,'11111111','31111111','Details1','dept1','dept2');"
        insertQuery2 = "INSERT INTO ruleTest.rules VALUES ('Rule 2','Description 2','proc',12345,0,200,'11111111','','Details2','dept1','dept2');"
        insertQuery3 = "INSERT INTO ruleTest.rules VALUES ('Rule 3','Description 3','proc',12345,0,200,'11111111','21111111,22222222','Details3','dept1','dept2');"
        insertQuery4 = "INSERT INTO ruleTest.rules VALUES ('Rule 4','Description 4','proc',12345,0,200,'11111111','21111111, 22222222','Details4','dept1','dept2');"
        cursor.execute(insertQuery1)
        cursor.execute(insertQuery2)
        cursor.execute(insertQuery3)
        cursor.execute(insertQuery4)
        conn.commit()

        #Should match all 4 rules
        order = OrderObject(1,['proc',12345,10,[11111111],'dept1'])
        evalResult = self.OE.evaluate_object(order).text()
        self.assertEqual(4,len(evalResult))

        #Should match 2 rules
        order = OrderObject(1,['proc',12345,10,[11111111,22222222],'dept1'])
        evalResult = self.OE.evaluate_object(order).text()
        self.assertEqual(2,len(evalResult))

        #Should match 1 rules
        order = OrderObject(1,['proc',12345,10,[11111111,22222222,31111111],'dept1'])
        evalResult = self.OE.evaluate_object(order).text()
        self.assertEqual(1,len(evalResult))


    def testRuleEngineInclusionDept(self):
        #This test that the evaluation works from start to end, specifically testing the Inclusion Dept
        print("\nTest Engine -> Inclusion Dept")
        global cursor, conn
        self.clear()

        insertQuery1 = "INSERT INTO ruleTest.rules VALUES ('Rule 1','Description 1','proc',12345,0,200,'11111111','12222222','Details1','dept1,dept3,dept4','dept2');"
        insertQuery2 = "INSERT INTO ruleTest.rules VALUES ('Rule 2','Description 2','proc',12345,0,200,'11111111','12222222','Details2','dept2','');"
        cursor.execute(insertQuery1)
        cursor.execute(insertQuery2)
        conn.commit()

        #Should match 1 rule
        order = OrderObject(1,['proc',12345,10,[11111111],'dept1'])
        evalResult = self.OE.evaluate_object(order).text()
        self.assertEqual(1,len(evalResult))

        #Should match 1 rule
        order = OrderObject(1,['proc',12345,10,[11111111],'dept2'])
        evalResult = self.OE.evaluate_object(order).text()
        self.assertEqual(1,len(evalResult))

        #Should match 1 rule
        order = OrderObject(1,['proc',12345,10,[11111111],'dept4'])
        evalResult = self.OE.evaluate_object(order).text()
        self.assertEqual(1,len(evalResult))

        #Should match 0 rules
        order = OrderObject(1,['proc',12345,10,[11111111],''])
        evalResult = self.OE.evaluate_object(order).text()
        self.assertEqual(0,len(evalResult))


    def testRuleEngineExclusionDept(self):
        #This test that the evaluation works from start to end, specifically testing the Exclusion Dept
        print("\nTest Engine -> Exclusion Dept")
        global cursor, conn
        self.clear()

        insertQuery1 = "INSERT INTO ruleTest.rules VALUES ('Rule 1','Description 1','proc',12345,0,200,'11111111','12222222','Details1','dept1','dept2,dept4,dept5');"
        insertQuery2 = "INSERT INTO ruleTest.rules VALUES ('Rule 2','Description 2','proc',12345,0,200,'11111111','12222222','Details2','dept2,dept6','dept3');"
        insertQuery3 = "INSERT INTO ruleTest.rules VALUES ('Rule 2','Description 2','proc',12345,0,200,'11111111','12222222','Details2','','dept3,dept6');"
        cursor.execute(insertQuery1)
        cursor.execute(insertQuery2)
        cursor.execute(insertQuery3)
        conn.commit()

        #Should match 2 rules
        order = OrderObject(1,['proc',12345,10,[11111111],'dept1'])
        evalResult = self.OE.evaluate_object(order).text()
        self.assertEqual(2,len(evalResult))

        #Should match 2 rules
        order = OrderObject(1,['proc',12345,10,[11111111],'dept2'])
        evalResult = self.OE.evaluate_object(order).text()
        self.assertEqual(2,len(evalResult))

        #Should match 0 rules
        order = OrderObject(1,['proc',12345,10,[11111111],'dept3'])
        evalResult = self.OE.evaluate_object(order).text()
        self.assertEqual(0,len(evalResult))

        #Should match  1 rule
        order = OrderObject(1,['proc',12345,10,[11111111],'dept6'])
        evalResult = self.OE.evaluate_object(order).text()
        self.assertEqual(1,len(evalResult))


    def testAncestor(self):
        #This tests that snomed ancestors are also checked when we are trying to match snomed inclusion and exlusion principles
        print("\nTest Engine -> SnomedID Ancestors")
        global cursor, conn
        self.clear()


        #Test child of ancestor true
        cursor.callproc("issnomedchild", ["118932009","95345008"])
        res = cursor.fetchone()[0]
        self.assertEqual(True,res)

        #Test non-child of ancestor false
        cursor.callproc("issnomedchild", ["118932009","95345007"])
        res = cursor.fetchone()[0]
        self.assertEqual(False,res)

        insertQuery1 = "INSERT INTO ruleTest.rules VALUES ('Rule 1','Description 1','proc',12345,0,200,'118932009','12222222','Details1','dept1','dept2');"
        insertQuery2 = "INSERT INTO ruleTest.rules VALUES ('Rule 2','Description 2','proc',12345,0,200,'118932009','118932009','Details2','dept1','dept2');"
        cursor.execute(insertQuery1)
        cursor.execute(insertQuery2)
        conn.commit()

        #Should match the one rule
        order = OrderObject(1,['proc',12345,10,[95345008],'dept1'])
        evalResult = self.OE.evaluate_object(order).text()
        self.assertEqual(1,len(evalResult))

        #Should match no rules
        order = OrderObject(1,['proc',12345,10,[95345007],'dept1'])
        evalResult = self.OE.evaluate_object(order).text()
        self.assertEqual(0,len(evalResult))

