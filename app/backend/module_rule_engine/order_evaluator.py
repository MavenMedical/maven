#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
# AUTHOR: Aidan Fowler
# DESCRIPTION: Order Evaluator: The only method in this class that should be called is evaluate_object.
# The method should be passed an order object and will evaluate which rules apply to the order
# Then return the matching orders in a response object
# ASSUMES: There is a table in the database called ruleTest.rules with columns specified in /mave/app/schema/createDb.sql
# SIDE EFFECTS: None, queries in this file should never update the database
# LAST MODIFIED FOR JIRA ISSUE: MAV-40 Monday February th
#*************************************************************************
#TODO add support for medications, currently we check rules by CPT codes which only allows us to check procedures
import app.backend.module_rule_engine.base_evaluator as BE
import app.backend.module_rule_engine.order_response_object as RO
from app.backend.module_rule_engine.databaseUtils import database_connect, query_database
from app.backend.module_rule_engine.engine import RuleEngine
from app.backend.module_rule_engine.rule_engine_logger import Logger


class OrderEvaluator(BE.BaseEvaluator):
    #The EvaluateOrder class extends the BaseEvaluator Class

    def __init__(self):
        #Connect to the database and set a cursor for the class, we only need the cursor because we will not be editing the database
        self.cursor = database_connect.connectToDb()
        self.Logger = Logger
        self.RE = RuleEngine(self.cursor,self.Logger)

    def evaluate_object(self,obj):
        response_messages = []
        #Find the rules with matching CPT codes, send these matches to rule_engine with the order object
        matches = self.find_matching_rules(obj.d['CPT'])
        for match in matches:
            self.Logger.log("\nEvaluating rule with matching CPT: %s"%match[0])
            eval_result = self.RE.evaluate_match(match,obj.d)
            if (eval_result != None):
                #If the result of the evaluation is a match, add the rule to the response message
                response_messages.append(eval_result)
        self.evaluator_response(obj, response_messages)
        #TODO: use the cost priority instead of 1
        return RO.OrderResponseObject(obj.order_id,1,response_messages)

    def find_matching_rules(self,CPTCode):
        #Query Database to find all rules that are related to the order's CPT Code
        matches = query_database.query_db_multiple("SELECT * FROM ruleTest.rules WHERE orderedCPT = %d;" % CPTCode, self.cursor, Logger)
        self.Logger.log("Matching Rules Count (CPT Match): %d" % len(matches))
        return matches

    def write_object(self,obj):
        #Overriding write object, for now just print out the response messages
        print("\nViolated Rules:\n")
        for response in obj[1]:
            print("%s\n"%response)
        print("Done Evaluating Order")


