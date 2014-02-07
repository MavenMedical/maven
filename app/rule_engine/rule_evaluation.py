#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
#__author__='Aidan Fowler'
#************************
#DESCRIPTION: Rule Evaluation Engine Prototype
#************************
#ASSUMES: There is a table in the database called ruleTest.rules with columns specified in /mave/app/schema/createDb.sql
#************************
#SIDE EFFECTS: None, queries in this file should never update the database
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-40 Wednesday February 5th
#*************************************************************************

from databaseUtils import databaseConnect



class EvaluateOrder():

	def __init__(self,dbString):
		self.cursor = databaseConnect.connectToDb(dbString)
	
	def querydb(self,query):
		results = []
		print ("Query: " + query) 
		self.cursor.execute(query)
		for res in self.cursor:
			results.append(res[0])
		return res

	def findMatchingRules(self,OrderObject):
		matches = querydb("SELECT * FROM ruleTest.rules WHERE OrderObject.CPT = orderedCPT")
		print ("Matching rules: ",matches)
		return matches

	def evaluateMatches(matches,OrderObject):
		#todo: 1. Check proc or med for correct evaluation path - right now we wil only suppor proc
		#	   2. For each matching rule, check that the age is in correct range, if it is not   throw out the rule
		#	   3. For each matching rule, check the snomedids, if any are in the exclusion list throw out the rule
		#	   4. For each matching rule, check the snomedids, if none are in the inclusion list throw out the rule
		#	   5. For each matching rule, check that the department is not equal to only in department (if value is not null), if not throw out the rule
		#	   6. For each matchint rule, check that the department is equal to not in department (if value is not null), if not throw out the rule



#some test code 
conn_string = "host='localhost' dbname='maven' user='maven' password='temporary'"
EO = EvaluateOrder(conn_string)

results = []
results.append(('ruleName',EO.querydb("SELECT ruleName FROM ruleTest.rules;")))
results.append(('ruleDescription',EO.querydb("SELECT ruleDescription FROM ruleTest.rules;")))
results.append(('orderType',EO.querydb("SELECT orderType FROM ruleTest.rules;")))
results.append(('orderedCPT',EO.querydb("SELECT orderedCPT FROM ruleTest.rules;")))
results.append(('minAge',EO.querydb("SELECT minAge FROM ruleTest.rules;")))
results.append(('maxAge',EO.querydb("SELECT maxAge FROM ruleTest.rules;")))
results.append(('withDx',EO.querydb("SELECT withDx FROM ruleTest.rules;")))
results.append(('withoutDx',EO.querydb("SELECT withoutDx FROM ruleTest.rules;")))
results.append(('details',EO.querydb("SELECT details FROM ruleTest.rules;")))
results.append(('onlyInDept',EO.querydb("SELECT onlyInDept FROM ruleTest.rules;")))
results.append(('notInDept',EO.querydb("SELECT notInDept FROM ruleTest.rules;")))

print ("\nResults: ")
for result in results:
	print (result)
