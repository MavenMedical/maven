#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
#__author__='Aidan Fowler'
#************************
#DESCRIPTION: Rule Evaluation Engine Prototype
#************************
#ASSUMES: There is a table in the database called ruleTest.rules     
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-40
#*************************************************************************

from databaseUtils import databaseConnect

class EvaluateOrder():

	def __init__(self,dbString):
		self.cursor = databaseConnect.connectToDb(dbString)
	
	def querydb(self,query):
		print ("Query: " + query) 
		self.cursor.execute(query)
		result = self.cursor.fetchone()
		return result

conn_string = "host='localhost' dbname='maven' user='maven' password='temporary'"
EO = EvaluateOrder(conn_string)
results = []
results.append(('ruleName',EO.querydb("SELECT ruleName FROM ruleTest.rules")))
results.append(('ruleDescription',EO.querydb("SELECT ruleDescription FROM ruleTest.rules")))
results.append(('orderType',EO.querydb("SELECT orderType FROM ruleTest.rules")))
results.append(('orderedCPT',EO.querydb("SELECT orderedCPT FROM ruleTest.rules")))
results.append(('minAge',EO.querydb("SELECT minAge FROM ruleTest.rules")))
results.append(('maxAge',EO.querydb("SELECT maxAge FROM ruleTest.rules")))
results.append(('withDx',EO.querydb("SELECT withDx FROM ruleTest.rules")))
results.append(('withoutDx',EO.querydb("SELECT withoutDx FROM ruleTest.rules")))
results.append(('details',EO.querydb("SELECT details FROM ruleTest.rules")))
results.append(('onlyInDept',EO.querydb("SELECT onlyInDept FROM ruleTest.rules")))
results.append(('notInDept',EO.querydb("SELECT notInDept FROM ruleTest.rules")))

print ("\nResults: ")
for result in results:
	print (result)
