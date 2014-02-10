#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
#__author__='Aidan Fowler'
#************************
#DESCRIPTION: Rule Evaluation Engine
#************************
#ASSUMES: There is a table in the database called ruleTest.rules with columns specified in /mave/app/schema/createDb.sql
#************************
#SIDE EFFECTS: None, queries in this file should never update the database
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-40 Monday February 10th
#*************************************************************************

from databaseUtils import databaseConnect
import app.rule_engine.base_evaluator as BE
import app.rule_engine.order_object as OO

global logging
logging = True

class EvaluateOrder(BE.BaseEvaluator):
    #The EvaluateOrder class extends the BaseEvaluator Class

    response_messages = []

    def __init__(self):
        #Connect to the database and set a cursor for the class, we only need the cursor because we will not be editing the database
        self.cursor = databaseConnect.connectToDb()

    def evaluate_object(self,obj):
        #Find the rules with matching CPT codes, send these matches to rule_engine
        matches = self.findMatchingRules(obj.d['CPT'])
        for match in matches:
            self.Log("\nEvaluating rule with matching CPT: %s"%match[0])
            evalResult = self.evaluateMatch(match,obj.d)
            if (evalResult != None):
                #If the result of the evaluation is a match, add the rule to the response message
                self.response_messages.append(evalResult)
        #Super class method
        self.evaluator_response(obj, self.response_messages)
        return self.response_messages

    def write_object(self,obj):
        #Overriding write object for now just print out the response messages
        print("\nViolated Rules:\n")
        for response in obj[1]:
            print("%s\n"%response)
        print("Done Evaluating Order")


    def findMatchingRules(self,CPTCode):
        #Query Database to find all rules that are related to the order's CPT Code
        matches = self.querydb("SELECT * FROM ruleTest.rules WHERE orderedCPT = %d;" % CPTCode)
        self.Log("Matching Rules Count (CPT Match): %d" % len(matches))
        return matches

    def querydb(self,query):
        #Query the database, return all results
        results = []
        self.Log("Query: " + query)
        self.cursor.execute(query)
        for res in self.cursor:
            results.append(res)
        return results

    def evaluateMatch(self,match,order):

        if len(match) != 11:
            raise Exception("The number of columns in the table must always be 11")

        #Necessary rule values that we will need to compare retrieved from table row
        ruleName = match[0]
        ruleDescription = match[1]
        ruleOrderType = match[2].lower()
        minAge = match[4]
        maxAge = match[5]

        withDx = []
        for dx in match[6].split(','):
            withDx.append(int(dx))

        withoutDx = []
        for dx in match[7].split(','):
            withoutDx.append(int(dx))

        details = match[8]
        onlyInDept = match[9]
        notInDept = match[10]

        #Dictionary of rule key value pairs to return as a message (keys: rule name, rule description, rule details)
        ruleMatch = {}

        #Check proc or med for correct evaluation path - right now we wil only support proc
        if order['orderType']=='proc':
            #Each check will retun true if the rule is possibly a match to the order parameters
            #If a check ever returns false we know that the rule does not apply to the order and we can stop
            #Checking the other parameters and move on to the next possible rule match

            #Immediately throw out all matches that are not of the same order type
            if ruleOrderType != order['orderType']:
                self.Log("Not a match -> order type check")
                return None

            print("Order Type: Procedure, we support this")

            if (self.checkAge(minAge,maxAge,order['age']) == False):
                self.Log("Not a match -> age check")
                return None

            if (self.checkInclusionDx(withDx,order['snomedIds']) == False):
                self.Log("Not a match -> Fail snomed inclusion")
                return None

            if (self.checkExclusionDx(withoutDx,order['snomedIds'])== False):
                self.Log("Not a match -> Fail snomed exclusion")
                return None

            if (self.checkInclusionDept(onlyInDept,order['dept']) == False):
                self.Log("Not a match -> Fail in dept")
                return None

            if (self.checkExclusionDept(notInDept,order['dept']) == False):
                self.Log("Not a match -> Fail not in dept")
                return None

            # Once we make it to here all the checks have passed and we have found a rule match, we need to send back a message
            self.Log("This Order Is A Match")
            ruleMatch['ruleName']=ruleName
            ruleMatch['ruleDescription'] = ruleDescription
            ruleMatch['details'] = details
            return ruleMatch

        elif order['orderType'] == 'med':
            raise Exception("Currently, the rules engine does not support evaluations for medications")
        else:
            raise Exception("The order type must be a procedure (proc) or medication (med)")

    def checkAge(self,minAge,maxAge,orderAge):
        #check that the age is in correct range, if it is not throw out the rule
        if (orderAge <= maxAge and orderAge >= minAge):
            self.Log("Age Check Passed")
            return True
        else:
            return False

    def checkInclusionDx(self,withDx,orderIds):
        #Todo: check the parents and children of the snomedIds in the orderIds too... will need to call function in database
        #check the inclusion list, if any of the Dx on the inclusion list are not also in the snomedIds list, throw away the rule
        for dx in withDx:
            match = False
            for id in orderIds:
                if dx == id:
                    match = True
            if match == False:
                return False
            match = False
        self.Log("SnomedID Inclusion Check Passed")
        return True

    def checkExclusionDx(self,withoutDx,orderIds):
        #Todo: check the parents and children of the snomedIds in the orderIds too... will need to call function in database
        #check the exclusion list, if any of the Dx on the exclusion list are also in the snomedIds list, throw away the rule
        for dx in withoutDx:
            match = False
            for id in orderIds:
                if dx == id:
                    match = True
            if match == True:
                return False
            match = False
        self.Log("SnomedID Exclusion Check Passed")
        return True

    def checkInclusionDept(self,onlyInDept,orderDept):
        #check that the order's department is equal to only in department, if not, throw out the rule
        if onlyInDept == orderDept:
            self.Log("Department Inclusion Check Passed")
            return True
        else:
            return False

    def checkExclusionDept(self,notInDept,orderDept):
        #check that the order's department is not equal to not in department, if not, throw out the rule
        if notInDept != orderDept:
            self.Log("Department Exclusion Check Passed")
            return True
        else:
            return False

    def Log(self,message):
        global logging
        if (logging):
            print(message)

    def setLogging(self,command):
        global logging
        if command == True:
            logging = True
        elif command == False:
            logging = False