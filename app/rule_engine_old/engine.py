#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
# AUTHOR: Aidan Fowler
# DESCRIPTION: Rule Evaluation Engine - This is the evaluation engine for matching rules to an order
# The only method that should get called (from the order_processor) is evaluateMatch
# The method takes in a possible match (row of the rules table whose CPT code matches an order's CPT code) as well as
# The order itself. This method returns a map of key value pairs from the matching rule {ruleName: "<name>:, ruleDescription: "<description>", details: "<details>"}
# ASSUMES:
# SIDE EFFECTS: None
# LAST MODIFIED FOR JIRA ISSUE: MAV-40 Wednesday February 12th
#*************************************************************************

class RuleEngine():

    def __init__(self,cursor,Logger):
        #initialize the RuleEngine with a cursor necessary for accessing the database for snomedID ancestry lookup
        self.cursor = cursor
        self.Logger = Logger

    def evaluate_match(self,match,order):

        if len(match) != 11:
            raise Exception("The number of columns in the table must always be 11")

        #Necessary rule values that we will need to compare retrieved from table row
        ruleName = match[0]
        ruleDescription = match[1]
        ruleOrderType = match[2].lower()

        #Auto set ages if the age field(s) are empty
        if (match[4] != ''):
            minAge = match[4]
        else:
            minAge = 0

        if (match[5] != ''):
            maxAge = match[5]
        else:
            maxAge = 1000

        withDx = []
        for dx in match[6].split(','):
            try:
                withDx.append(int(dx))
            except ValueError:
                # we should ignore this error for the case where the list is empty
                self.Logger.log("Trying to add a non int to the snomedId list: %s" % dx)

        withoutDx = []
        for dx in match[7].split(','):
            try:
                withoutDx.append(int(dx))
            except ValueError:
                # we should ignore this error for the case where the list is empty
                self.Logger.log("Trying to add a non int to the snomedId Exclusion List: %s" % dx)

        details = match[8]

        onlyInDept = []
        for dept in match[9].split(','):
            onlyInDept.append(dept)

        notInDept = []
        for dept in match[10].split(','):
            notInDept.append(dept)

        #Dictionary of rule key value pairs to return as a message (keys: rule name, rule description, rule details)
        ruleMatch = {}

        #Check proc or med for correct evaluation path - right now we wil only support proc
        if order['orderType']=='proc':
            #Each check will return true if the rule is possibly a match to the order parameters
            #If a check ever returns false we know that the rule does not apply to the order and we can stop
            #Checking the other parameters and move on to the next possible rule match

            #Immediately throw out all matches that are not of the same order type
            if ruleOrderType != order['orderType']:
                self.Logger.log("Not a match -> Fail Order type check")
                return None

            self.Logger.log("Order Type: Procedure, we support this")

            if (self.check_age(minAge,maxAge,order['age']) == False):
                self.Logger.log("Not a match -> FailAge check")
                return None

            if (self.check_inclusion_dx(withDx,order['snomedIds']) == False):
                self.Logger.log("Not a match -> Fail snomedID inclusion")
                return None

            if (self.check_exclusion_dx(withoutDx,order['snomedIds'])== False):
                self.Logger.log("Not a match -> Fail snomedID exclusion")
                return None

            if (self.check_inclusion_dept(onlyInDept,order['dept']) == False):
                self.Logger.log("Not a match -> Fail dept inclusion check")
                return None

            if (self.check_exclusion_dept(notInDept,order['dept']) == False):
                self.Logger.log("Not a match -> Fail dept exclusion check")
                return None

            # Once we make it to here all the checks have passed and we have found a rule match, we need to send back a message
            self.Logger.log("This Order Is A Match")
            ruleMatch['ruleName']=ruleName
            ruleMatch['ruleDescription'] = ruleDescription
            ruleMatch['details'] = details
            return ruleMatch

        elif order['orderType'] == 'med':
            raise Exception("Currently, the rules engine does not support evaluations for medications")
        else:
            raise Exception("The order type must be a procedure (proc) or medication (med)")

    def check_age(self,minAge,maxAge,orderAge):
        #check that the age is in correct range, if it is not throw out the rule
        if (orderAge <= maxAge and orderAge >= minAge):
            self.Logger.log("Age Check Passed")
            return True
        else:
            return False

    def check_inclusion_dx(self,withDx,orderIds):
        #check the inclusion list, if any of the Dx on the inclusion list are not also in the snomedIds list or ancestors of the orders snomedIds, throw away the rule
        for dx in withDx:
            match = False
            for id in orderIds:
                if dx == id:
                    match = True
                elif (self.check_ancestors(dx,id) == True):
                    match = True
            if match == False:
                return False
            match = False
        self.Logger.log("SnomedID Inclusion Check Passed")
        return True

    def check_exclusion_dx(self,withoutDx,orderIds):
        #check the exclusion list, if any of the Dx on the exclusion list are also in the snomedIds list or ancestors of the orders snomedIds, throw away the rule
        for dx in withoutDx:
            match = False
            for id in orderIds:
                if dx == id:
                    match = True
                elif (self.check_ancestors(dx,id) == True):
                    match = True
            if match == True:
                return False
            match = False
        self.Logger.log("SnomedID Exclusion Check Passed")
        return True

    def check_inclusion_dept(self,onlyInDept,orderDept):
        #check the department inclusion list, if any of the departments on the inclusion equal to the order dept, return true, if not throw out the rule
        print("ONLY IN :",onlyInDept)
        print("ORDER dept:", orderDept)
        match = False
        if (len(onlyInDept) == 1 and onlyInDept[0] == ''):
            match = True
        for dept in onlyInDept:
            if dept == orderDept:
                match = True
        if match == False:
            return False
        else:
            self.Logger.log("Department Inclusion Check Passed")
            return True

    def check_exclusion_dept(self,notInDept,orderDept):
        #If any of the departments on the exclusion list are equal to the order dept, throw out the rule
        if (len(notInDept) == 1 and notInDept[0] == ''):
            return True
        for dept in notInDept:
            if dept == orderDept:
                return False
        self.Logger.log("Department Exclusion Check Passed")
        return True

    def check_ancestors(self,dx,id):
        #Call stored funcion to check if the rule's snomedId is an ancestor of the order's snomedId
        self.cursor.callproc("issnomedchild", [dx,id])
        return self.cursor.fetchone()[0]