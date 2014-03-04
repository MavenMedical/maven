#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:   This python file acts to analyze the cost of orderables that were delivered via message
#               from an EMR.
#
#************************
#ASSUMES:       XML format that is described in the Unit Test for the clientApp api.
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-1
#*************************************************************************

import app.backend.module_rule_engine.base_evaluator as BE
from xml.etree import ElementTree as ET
from clientApp.api import cliPatient as PT





class CostTracker(BE.BaseEvaluator):

    patient = PT()
    encounter_proc_orders = []
    encounter_med_orders = []
    encounter_lab_orders = []
    encounter_orders_and_cost = [{'order': 15}]
    encounter_cost = 980.26

    def __init__(self):
        self.procs_cost = 0
        self.meds_cost = 0
        self.labs_cost = 0
        self.total_cost = 0

    def get_procs_cost(self):
        raise NotImplementedError

    def get_meds_cost(self):
        raise NotImplementedError

    def get_labs_cost(self):
        raise NotImplementedError

    def get_total_cost(self):
        raise NotImplementedError