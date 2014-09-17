# *************************************************************************
# Copyright (c) 2014 - Maven Medical
#
# ************************
# AUTHOR:
__author__ = 'Yuki Uchino'
# ************************
# DESCRIPTION:   This file creates a an asynchronous listening server for incoming messages.
#
# ************************
# ASSUMES:
# ************************
# SIDE EFFECTS:
# ************************
# LAST MODIFIED FOR JIRA ISSUE: MAV-1
# *************************************************************************
import argparse
import pickle
from utils.streaming import stream_processor as SP
import utils.streaming.rpc_processor as RP
from utils.enums import CONFIG_PARAMS
from utils.database.database import AsyncConnectionPool
import utils.database.web_persistence as WP
import app.backend.remote_procedures.client_app as CA_RPC
import app.backend.remote_procedures.client_app_manager as CAM_RPC
import asyncio
import maven_config as MC
import utils.crypto.authorization_key as AK
import maven_logging as ML

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
        # obj_list = json.loads(obj.decode())
        obj_list = pickle.loads(obj)
        composition = obj_list[0]
        key1 = obj_list[1]
        ML.DEBUG(key1)
        # composition = api.Composition().create_composition_from_json(json_composition)
        composition.write_key = [key1, key2]
        self.write_object(composition, writer_key="CostEval")


class OutgoingMessageHandler(SP.StreamProcessor):

    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)

    @asyncio.coroutine
    def read_object(self, obj, _):
        obj.user = obj.author.get_provider_username()
        obj.userAuth = AK.authorization_key([obj.user, str(obj.customer_id)], 44, 60 * 60)
        self.write_object(pickle.dumps(obj), writer_key=obj.write_key[1])


def main(loop):

    outgoingtohospitalsmessagehandler = 'responder socket'
    incomingtomavenmessagehandler = 'receiver socket'
    rpc_server_stream_processor = 'Server-side RPC Stream Processor'

    MavenConfig = {
        rpc_server_stream_processor: {
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETREPLY,
            SP.CONFIG_WRITERNAME: rpc_server_stream_processor + '.Writer2',
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSERVERSOCKET,
            SP.CONFIG_READERNAME: rpc_server_stream_processor + '.Reader2',
            SP.CONFIG_WRITERDYNAMICKEY: 2,
            SP.CONFIG_DEFAULTWRITEKEY: 2,
        },
        rpc_server_stream_processor + '.Writer2': {
            SP.CONFIG_WRITERKEY: 2,
        },
        rpc_server_stream_processor + '.Reader2': {
            SP.CONFIG_HOST: '127.0.0.1',
            SP.CONFIG_PORT: '54728',
        },
        incomingtomavenmessagehandler:
        {
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSERVERSOCKET,
            SP.CONFIG_READERNAME: incomingtomavenmessagehandler + ".Reader",
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
            SP.CONFIG_WRITERNAME: [incomingtomavenmessagehandler + ".Writer", incomingtomavenmessagehandler + ".Writer_CostEval"],
            SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_IDENTITYPARSER,
            SP.CONFIG_WRITERDYNAMICKEY: 1,
        },
        incomingtomavenmessagehandler + ".Reader":
        {
            SP.CONFIG_HOST: '127.0.0.1',
            SP.CONFIG_PORT: 8090
        },

        incomingtomavenmessagehandler + ".Writer":
        {
            SP.CONFIG_HOST: 'localhost',
            SP.CONFIG_QUEUE: 'incoming_cost_evaluator_work_queue',
            SP.CONFIG_EXCHANGE: 'maven_exchange',
            SP.CONFIG_KEY: 'incomingcost'
        },
        incomingtomavenmessagehandler + ".Writer_CostEval":
        {
            SP.CONFIG_HOST: 'localhost',
            SP.CONFIG_QUEUE: 'incoming_cost_evaluator_work_queue',
            SP.CONFIG_EXCHANGE: 'maven_exchange',
            SP.CONFIG_KEY: 'incomingcosteval',
            SP.CONFIG_WRITERKEY: 'CostEval'
        },
        outgoingtohospitalsmessagehandler:
        {
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
            SP.CONFIG_READERNAME: outgoingtohospitalsmessagehandler + ".Reader",
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETREPLY,
            SP.CONFIG_WRITERNAME: outgoingtohospitalsmessagehandler + ".Writer",
            SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_UNPICKLEPARSER,

        },
        outgoingtohospitalsmessagehandler + ".Reader":
        {
            SP.CONFIG_HOST: 'localhost',
            SP.CONFIG_QUEUE: 'aggregator_work_queue',
            SP.CONFIG_EXCHANGE: 'maven_exchange',
            SP.CONFIG_KEY: 'aggregate',
            # SP.CONFIG_WRITERKEY: 'aggregate',
        },

        outgoingtohospitalsmessagehandler + ".Writer":
        {
            SP.CONFIG_WRITERKEY: 1
        },
        CONFIG_PARAMS.PERSISTENCE_SVC.value: {WP.CONFIG_DATABASE: CONFIG_PARAMS.DATABASE_SVC.value, },
        CONFIG_PARAMS.DATABASE_SVC.value:
        {
            AsyncConnectionPool.CONFIG_CONNECTION_STRING: MC.dbconnection,
            AsyncConnectionPool.CONFIG_MIN_CONNECTIONS: 4,
            AsyncConnectionPool.CONFIG_MAX_CONNECTIONS: 8
        },

    }
    MC.MavenConfig = MavenConfig

    client_app_rpc_service = RP.rpc(rpc_server_stream_processor)
    client_app_rpc_service.schedule(loop)

    client_app_RPCs = CA_RPC.ClientAppRemoteProcedureCalls()
    client_app_RPCs.persistence.schedule(loop)
    client_app_rpc_service.register(client_app_RPCs)

    client_app_manager_RPCs = CAM_RPC.ClientAppManagerRemoteProcedureCalls()
    client_app_manager_RPCs.persistence.schedule(loop)
    client_app_rpc_service.register(client_app_manager_RPCs)

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
