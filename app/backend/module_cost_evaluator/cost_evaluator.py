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
#from xml.etree import ElementTree as ET
#from clientApp.api import cliPatient as PT
import app.utils.streaming.stream_processor as SP
from app.utils.database.database import AsyncConnectionPool,SingleThreadedConnection, MappingUtilites
import maven_config as MC
import asyncio
import json
import pickle




class CostEvaluator(SP.StreamProcessor):

    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)


    @asyncio.coroutine
    def read_object(self, obj, _):
        composition = json.loads(obj.decode())
        ord_id_list = []
        for sec in composition['section']:
            if sec['title'] == "Encounter Orders":
                for ord in sec['content']:
                    for id in ord['identifier']:
                        if id['label'] == "CPT":
                            ord_id_list.append(id.value)
                yield from self.evaluate_orders(ord_id_list, composition)
        #self.write_object(obj, writer_key='aggregate')
        #self.write_object(obj, writer_key='logging')
        print("h")

    @asyncio.coroutine
    def evaluate_orders(self, ord_id_list, composition):
        conn = AsyncConnectionPool('test conn pool', self.loop)
        orders_cost_summary = []

        for sec in composition['section']:
            if sec['title'] == "Encounter Orders":
                total_cost = 0.00
                for order in sec['content']:
                    cur = yield from conn.execute_single("select costmap.cost_amt, costmap.billing_code from costmap")
                    for result in cur:
                        order['totalCost'] = float(result[0])

                        for id in order['detail'][0]['identifier']:
                            if id['label'] == "name":
                                orders_cost_summary.append({str(id.value): str(result[0])})
                        total_cost += float(result[0])
                    print(order)
                print(total_cost)
            composition.section.append(orders_cost_summary)
        return composition


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
        'test conn pool': {
            AsyncConnectionPool.CONFIG_CONNECTION_STRING:
            ("dbname=%s user=%s password=%s host=%s port=%s" % ('maven', 'maven', 'temporary', 'localhost', '5432')),
            AsyncConnectionPool.CONFIG_MIN_CONNECTIONS: 4,
            AsyncConnectionPool.CONFIG_MAX_CONNECTIONS: 8
        },
        'test blocking': {
            SingleThreadedConnection.CONFIG_CONNECTION_STRING:
            ("dbname=%s user=%s password=%s host=%s port=%s" % ('maven', 'maven', 'temporary', 'localhost', '5432'))
        }
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