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
import app.backend.module_rule_engine.base_evaluator
# no import maven_config needed
import app.backend.module_rule_engine.order_object as OO
import app.backend.module_rule_engine.base_evaluator as BE
from maven_logging import PRINT

te = BE.TestEvaluator()


def write_object(obj):
    PRINT("%s %s" % (obj[0], obj[1]))

te.write_object = write_object

te.evaluate_object("test string")
te.evaluate_object(1)
te.evaluate_object(OO.OrderObject("object id", [6, 7, 8, 9, 10, 11, 12]))

