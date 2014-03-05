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
#from clientApp.api import cliPatient as PT
import app.utils.streaming.stream_processor as SP
import maven_config as MC
import asyncio


def main(loop):
    rabbithandler = 'receiver socket'

    MavenConfig = {
        rabbithandler:
        {
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
            SP.CONFIG_READERNAME: rabbithandler+".Reader",
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
            SP.CONFIG_WRITERNAME: rabbithandler+".Writer",
            SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_IDENTITYPARSER,

        },
        rabbithandler+".Reader":
        {
            SP.CONFIG_HOST:'localhost',
            SP.CONFIG_QUEUE:'incoming_cost_evaluator_work_queue',
            SP.CONFIG_EXCHANGE:'maven_exchange',
            SP.CONFIG_KEY:'incomingcost'
        },

        rabbithandler+".Writer":
        {
            SP.CONFIG_HOST:'localhost',
            SP.CONFIG_QUEUE:'aggregator_work_queue',
            SP.CONFIG_EXCHANGE:'maven_exchange',
            SP.CONFIG_KEY:'aggregate'
        },
    }

    MC.MavenConfig = MavenConfig
    sp_message_handler = CostTrackerInputOutput(rabbithandler)
    sp_message_handler.schedule(loop)

    try:
        loop.run_forever()

    except KeyboardInterrupt:
        sp_message_handler.close()
        loop.close()

class CostTracker(BE.BaseEvaluator):

    #patient = PT()
    encounter_proc_orders = []
    encounter_med_orders = []
    encounter_lab_orders = []
    encounter_orders_and_cost = [{'order': 15}]
    encounter_cost = 980.26

    def __init__(self):
        BE.BaseEvaluator.__init__(self)
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


class CostTrackerInputOutput(SP.StreamProcessor):

    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)

    @asyncio.coroutine
    def read_object(self, obj, _):
        self.write_object(obj)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    main(loop)