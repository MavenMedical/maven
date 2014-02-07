##############################################################################
#  Copyright (c) 2014 - Maven Medical
#
#
#  Description: Test the BaseEvaluator and the stub module TestEvaluator
#               
#  Author: Tom DuBois 
#  Assumes: 
#  Side Effects: None
#  Last Modified: 
##############################################################################
import app.rule_engine.base_evaluator as BE
# no import maven_config needed
import app.rule_engine.order_object as OO

class BaseEvaluator():
    
    # this class should be overridden
    # parameter is from app.rule_engine.order_object
    def evaluate_object(self,obj):
        # do something
        raise Exception("Unimplemented")

    #when finished, call this function with the response (or explicitly send None)
    def evaluator_response(self, obj, response):
        #this function will log the response, and forward to the next place
        #one idea is to combine an evaluator subclass with the Streaming base class
        #then it calls write_object to send a message to whatever is next
        print("logging ("+str(obj)+","+str(response)+")")
        self.write_object([obj,response])

    def write_object(self, obj):
        # must be overridden.
        # matches write_object in app.utils.streaming.stream_processor
        raise Exception("Unimplemented")

class TestEvaluator(BaseEvaluator):
    
    canned_response = "Test response"

    def __init__(self):
        # there are no databases or rule lists to access, so this is easy
        pass

    def evaluate_object(self,obj):
        self.evaluator_response(obj,self.canned_response)
        
    def write_object(self,obj):
        print("%s %s"%(obj[0],obj[1]))
    
te = TestEvaluator()
te.evaluate_object("test string")
te.evaluate_object(1)
te.evaluate_object(OO.OrderObject([6, 7, 8, 9, 10,11,12]))
