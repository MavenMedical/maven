#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:   This composition_evaluator.py contains the classes required to process a
#               FHIR Composition object through Maven Sleuth Rule Engine.
#
#
#
#************************
#ASSUMES:
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-96
#*************************************************************************
from app.backend.module_RE.base_evaluator import BaseEvaluator as BE
import asyncio
import app.utils.streaming.stream_processor as SP
from app.utils.database.database import AsyncConnectionPool,SingleThreadedConnection, MappingUtilites
import maven_config as MC
import maven_logging as ML
import pickle
from clientApp.api.api import Composition


class CompositionEvaluator(SP.StreamProcessor):

    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)
        self.conn = AsyncConnectionPool('EvaluatorConnectionPool')

    @asyncio.coroutine
    def read_object(self, obj, _):
        composition = pickle.loads(obj)
        rules = yield from self.get_matching_sleuth_rules(composition)
        ML.PRINT("Herro")

    @asyncio.coroutine
    def get_matching_sleuth_rules(self, composition):
        orders = composition.get_encounter_orders()
        customer_id = composition.customer_id
        applicable_sleuth_rules = []
        DBMapper = MappingUtilites()
        for order in orders:
            order_details = composition.get_proc_supply_details(order)

            for detail in order_details:
                column_map = ["sleuth_rule.rule_details"]
                columns = DBMapper.select_rows_from_map(column_map)
                cur = yield from self.conn.execute_single("select %s from sleuth_rule where cpt_trigger='%s' and customer_id=%s" % (columns, detail[0], customer_id))
                for result in cur:
                    applicable_sleuth_rules.append(result)

        return applicable_sleuth_rules

    @asyncio.coroutine
    def evaluate_object(self, composition):
        raise NotImplementedError


    def evaluator_response(self, obj, response):
        raise NotImplementedError


def run_composition_evaluator():

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
        'EvaluatorConnectionPool': {
            AsyncConnectionPool.CONFIG_CONNECTION_STRING:
            ("dbname=%s user=%s password=%s host=%s port=%s" % ('maven', 'maven', 'temporary', 'localhost', '5432')),
            AsyncConnectionPool.CONFIG_MIN_CONNECTIONS: 2,
            AsyncConnectionPool.CONFIG_MAX_CONNECTIONS: 4
        },
    }

    MC.MavenConfig = MavenConfig

    loop = asyncio.get_event_loop()
    sp_message_handler = CompositionEvaluator(rabbithandler)
    sp_message_handler.schedule(loop)

    try:
        loop.run_forever()

    except KeyboardInterrupt:
        sp_message_handler.close()
        loop.close()

if __name__ == '__main__':
    run_composition_evaluator()