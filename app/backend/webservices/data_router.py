#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:   This file creates a an asynchronous listening server for incoming messages.
#
#************************
#ASSUMES:
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-1
#*************************************************************************
import argparse
import json
import pickle
from utils.streaming import stream_processor as SP
import asyncio
import maven_config as MC
import utils.api.fhir as api
import utils.crypto.authorization_key as AK
ARGS = argparse.ArgumentParser(description='Maven Client Receiver Configs.')
ARGS.add_argument(
    '--emr', action='store', dest='emr',
    default='Epic', help='EMR Name')
args = ARGS.parse_args()


class IncomingMessageHandler(SP.StreamProcessor):

    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)
        self.master_list = ['', '', '', '', '']
        self.object_manager = []

    @asyncio.coroutine
    def read_object(self, obj, key2):
        obj_list = json.loads(obj.decode())
        json_composition = obj_list[0]
        key1 = obj_list[1]
        if json_composition['type'] == "CostEvaluator":
            composition = api.Composition().create_composition_from_json(json_composition)
            composition.maven_route_key = [key1, key2]
            self.write_object(composition, writer_key="CostEval")


class OutgoingMessageHandler(SP.StreamProcessor):

    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)

    @asyncio.coroutine
    def read_object(self, obj, _):
        obj.user = obj.encounter.get_prov_id()
        obj.userAuth = AK.authorization_key(obj.user, 44, 60*60)
        self.write_object(pickle.dumps(obj), writer_key=obj.maven_route_key[1])


def main(loop):

    outgoingtohospitalsmessagehandler = 'responder socket'
    incomingtomavenmessagehandler = 'receiver socket'


    MavenConfig = {
        incomingtomavenmessagehandler:
        {
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSERVERSOCKET,
            SP.CONFIG_READERNAME: incomingtomavenmessagehandler+".Reader",
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
            SP.CONFIG_WRITERNAME: [incomingtomavenmessagehandler+".Writer", incomingtomavenmessagehandler+".Writer_CostEval"],
            SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_IDENTITYPARSER,
            SP.CONFIG_WRITERDYNAMICKEY:1,
        },
        incomingtomavenmessagehandler+".Reader":
        {
            SP.CONFIG_HOST:'127.0.0.1',
            SP.CONFIG_PORT:8090
        },

        incomingtomavenmessagehandler+".Writer":
        {
            SP.CONFIG_HOST:'localhost',
            SP.CONFIG_QUEUE:'incoming_cost_evaluator_work_queue',
            SP.CONFIG_EXCHANGE:'maven_exchange',
            SP.CONFIG_KEY:'incomingcost'
        },
        incomingtomavenmessagehandler+".Writer_CostEval":
        {
            SP.CONFIG_HOST:'localhost',
            SP.CONFIG_QUEUE:'incoming_cost_evaluator_work_queue',
            SP.CONFIG_EXCHANGE:'maven_exchange',
            SP.CONFIG_KEY:'incomingcosteval',
            SP.CONFIG_WRITERKEY:'CostEval'
        },
        outgoingtohospitalsmessagehandler:
        {
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
            SP.CONFIG_READERNAME: outgoingtohospitalsmessagehandler+".Reader",
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETREPLY,
            SP.CONFIG_WRITERNAME: outgoingtohospitalsmessagehandler+".Writer",
            SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_UNPICKLEPARSER,

        },
        outgoingtohospitalsmessagehandler+".Reader":
        {
            SP.CONFIG_HOST:'localhost',
            SP.CONFIG_QUEUE:'aggregator_work_queue',
            SP.CONFIG_EXCHANGE:'maven_exchange',
            SP.CONFIG_KEY:'aggregate',
            #SP.CONFIG_WRITERKEY:'aggregate',
        },

        outgoingtohospitalsmessagehandler+".Writer":
        {
            SP.CONFIG_WRITERKEY:1
        },

    }
    MC.MavenConfig = MavenConfig

    sp_consumer = IncomingMessageHandler(incomingtomavenmessagehandler)
    sp_producer = OutgoingMessageHandler(outgoingtohospitalsmessagehandler)

    reader = sp_consumer.schedule(loop)
    emitter = sp_producer.schedule(loop)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        sp_consumer.close()
        sp_producer.close()
        loop.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    main(loop)
