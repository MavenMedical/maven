##############################################################################
#  Copyright (c) 2014 - Maven Medical
#
#
#  Description: Super-class for everything that evaluates rules against an order
#               
#  Author: Tom DuBois 
#  Assumes: 
#  Side Effects: None
#  Last Modified: 
##############################################################################
import app.utils.streaming.stream_processor as SP
from app.utils.database.database import AsyncConnectionPool,SingleThreadedConnection, MappingUtilites
import maven_config as MC
import asyncio
import json
import pickle
import clientApp.api.api as api
import maven_logging as ML
import datetime

class BaseEvaluator(SP.StreamProcessor):
    
    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)
        self.conn = AsyncConnectionPool('EvaluatorConnectionPool')
        pass

    # this class should be overridden
    # parameter is from app.rule_engine.order_object
    def evaluate_object(self, obj):
        # do something
        raise Exception("Unimplemented")

    #when finished, call this function with the response (or explicitly send None)
    def evaluator_response(self, obj, response):
        #this function will log the response, and forward to the next place
        #one idea is to combine an evaluator subclass with the Streaming base class
        #then it calls write_object to send a message to whatever is next
        self.write_object([obj, response])

    def write_object(obj, key):
        # must be overridden.
        # matches write_object in app.utils.streaming.stream_processor
        raise Exception("Unimplemented")


class TestEvaluator(BaseEvaluator):
    
    canned_response = "Test response"

    def __init__(self):
        # there are no databases or rule lists to access, so this is easy
        BaseEvaluator.__init__(self)

    def evaluate_object(self, obj):
        self.evaluator_response(obj, self.canned_response)
        
    def write_object(self, obj):
        print(obj)



