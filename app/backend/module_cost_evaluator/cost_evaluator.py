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
import app.utils.streaming.stream_processor as SP
from app.utils.database.database import AsyncConnectionPool,SingleThreadedConnection, MappingUtilites
from app.utils.database.fhir_database import PostgresFHIR
import maven_config as MC
import asyncio
import pickle
import clientApp.api.api as api
import maven_logging as ML


class CostEvaluator(SP.StreamProcessor):

    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)
        self.conn = SingleThreadedConnection('CostEvalConnection')
        self.PF = PostgresFHIR()


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
        NEW section to Composition.section labeled "Encounter Cost Breakdown"

        :param composition: FHIR Composition object created using Maven's FHIR API
        """
        encounter_cost_breakdown = []
        total_cost = 0.00

        orders = composition.get_encounter_orders()
        for order in orders:
            order.totalCost = 0.00
            order_details = composition.get_proc_supply_details(order)

            for detail in order_details:
                cur = self.conn.execute("select cost_amt from costmap where billing_code='%s'" % detail[0])
                for result in cur:
                    #detail.append(float(result[0]))
                    order.totalCost += float(result[0])
                    encounter_cost_breakdown.append([detail[1], float(result[0])])

            total_cost += order.totalCost
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
            SingleThreadedConnection.CONFIG_CONNECTION_STRING:
            ("dbname=%s user=%s password=%s host=%s port=%s" % ('maven', 'maven', 'temporary', MC.dbhost, '5432')),

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
