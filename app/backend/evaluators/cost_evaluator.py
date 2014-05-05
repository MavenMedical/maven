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

import pickle

from utils.database.database import SingleThreadedConnection
import asyncio

import utils.streaming.stream_processor as SP
from utils.database.fhir_database import PostgresFHIR as PF
import maven_config as MC
import utils.api.fhir as api


class CostEvaluator(SP.StreamProcessor):

    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)
        self.conn = SingleThreadedConnection('CostEvalConnection')
        self.PF = PF()


    @asyncio.coroutine
    def read_object(self, obj, _):
        composition = pickle.loads(obj)
        self.evaluate_orders(composition)
        self.PF.write_composition_to_db(composition, self.conn)
        self.write_object(composition, writer_key='aggregate')

    def evaluate_orders(self, composition):
        """
        Takes a FHIR Composition object, iterates through the Orders found in the "Encounter Orders"
        Composition.section object, checks the costmap table for the cost-look-up, and then adds a
        NEW section to Composition.section labeled "Encounter Cost Breakdown," which is a list of
        {"order name": 807.13} tuples with order name and the price.

        :param composition: FHIR Composition object created using Maven's FHIR API
        """
        encounter_cost_breakdown = []

        orders = composition.get_encounter_orders()
        for order in orders:
            order.totalCost = 0.00
            order_details = composition.get_proc_supply_details(order)

            for detail in order_details:
                cur = self.conn.execute("select cost_amt from costmap where billing_code='%s'" % detail[0])
                for result in cur:
                    order.totalCost += float(result[0])
                    encounter_cost_breakdown.append([detail[1], float(result[0])])

        composition.section.append(api.Section(title="Encounter Cost Breakdown", content=encounter_cost_breakdown))


def run_cost_evaluator():

    rabbithandler = 'rabbitmessagehandler'
    MavenConfig = {
        rabbithandler:
        {
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
            SP.CONFIG_READERNAME: rabbithandler+".Reader",
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
            SP.CONFIG_WRITERNAME: [rabbithandler+".Writer", rabbithandler+".Writer2"],
            SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_IDENTITYPARSER,

        },
        rabbithandler+".Reader":
        {
            SP.CONFIG_HOST:'localhost',
            SP.CONFIG_QUEUE:'incoming_cost_evaluator_work_queue',
            SP.CONFIG_EXCHANGE:'maven_exchange',
            SP.CONFIG_KEY:'incomingcosteval'
        },

        rabbithandler+".Writer":
        {
            SP.CONFIG_HOST:'localhost',
            SP.CONFIG_QUEUE:'aggregator_work_queue',
            SP.CONFIG_EXCHANGE:'maven_exchange',
            SP.CONFIG_KEY:'aggregate',
            SP.CONFIG_WRITERKEY:'aggregate',
        },

        rabbithandler+".Writer2":
        {
            SP.CONFIG_HOST:'localhost',
            SP.CONFIG_QUEUE:'logger_work_queue',
            SP.CONFIG_EXCHANGE:'maven_exchange',
            SP.CONFIG_KEY:'logging',
            SP.CONFIG_WRITERKEY:'logging',
        },
        'CostEvalConnection': {
            SingleThreadedConnection.CONFIG_CONNECTION_STRING: MC.dbconnection,
            #AsyncConnectionPool.CONFIG_MIN_CONNECTIONS: 2,
            #AsyncConnectionPool.CONFIG_MAX_CONNECTIONS: 4
        },
    }

    MC.MavenConfig = MavenConfig

    loop = asyncio.get_event_loop()
    sp_message_handler = CostEvaluator(rabbithandler)
    sp_message_handler.schedule(loop)

    try:
        loop.run_forever()

    except KeyboardInterrupt:
        sp_message_handler.close()
        loop.close()

if __name__ == '__main__':
    run_cost_evaluator()