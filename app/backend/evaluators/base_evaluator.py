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
import asyncio
import maven_config as MC
from utils.enums import CONFIG_PARAMS
import utils.database.fhir_database as FD
import utils.streaming.stream_processor as SP
from app.backend.evaluators.composition_evaluator import CompositionEvaluator


class BaseEvaluator(SP.StreamProcessor):

    def __init__(self, configname, fhir_persistence):
        SP.StreamProcessor.__init__(self, configname)
        self.fhir_persistence = fhir_persistence

    def evaluate_object(self, obj):
        raise NotImplementedError

    def evaluator_response(self, obj, response):
        self.write_object([obj, response])

    def write_object(obj, key):
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


def run_composition_evaluator():

    rabbithandler = 'rabbitmessagehandler'
    rpc_database_stream_processor = 'Client to Database RPC Stream Processor'

    MavenConfig = {
        rabbithandler:
            {
                SP.CONFIG_READERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
                SP.CONFIG_READERNAME: rabbithandler + ".Reader",
                SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
                SP.CONFIG_WRITERNAME: [rabbithandler + ".Writer", rabbithandler + ".Writer2", rabbithandler + ".WriterCost"],
                SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_IDENTITYPARSER,

                },
        rabbithandler + ".Reader":
            {
                SP.CONFIG_HOST: 'localhost',
                SP.CONFIG_QUEUE: 'incoming_path_evaluator_work_queue',
                SP.CONFIG_EXCHANGE: 'maven_exchange',
                SP.CONFIG_KEY: 'incomingpatheval'
            },

        rabbithandler + ".Writer":
            {
                SP.CONFIG_HOST: 'localhost',
                SP.CONFIG_QUEUE: 'aggregator_work_queue',
                SP.CONFIG_EXCHANGE: 'maven_exchange',
                SP.CONFIG_KEY: 'aggregate',
                SP.CONFIG_WRITERKEY: 'aggregate',
                },

        rabbithandler + ".Writer2":
            {
                SP.CONFIG_HOST: 'localhost',
                SP.CONFIG_QUEUE: 'logger_work_queue',
                SP.CONFIG_EXCHANGE: 'fanout_evaluator',
                SP.CONFIG_KEY: 'logging',
                SP.CONFIG_WRITERKEY: 'logging',
                },
        rabbithandler + ".WriterCost":
            {
                SP.CONFIG_HOST: 'localhost',
                SP.CONFIG_QUEUE: 'transparent_send_queue',
                SP.CONFIG_EXCHANGE: 'maven_exchange',
                SP.CONFIG_KEY: 'transparent',
                SP.CONFIG_WRITERKEY: 'transparent',
                },
        CONFIG_PARAMS.PERSISTENCE_SVC.value: {FD.CONFIG_DATABASE: rpc_database_stream_processor},
        rpc_database_stream_processor: {
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETREPLY,
            SP.CONFIG_WRITERNAME: rpc_database_stream_processor + '.Writer1',
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETQUERY,
            SP.CONFIG_READERNAME: rpc_database_stream_processor + '.Reader1',
            SP.CONFIG_WRITERDYNAMICKEY: 4,
            SP.CONFIG_DEFAULTWRITEKEY: 4,
            },
        rpc_database_stream_processor + ".Writer1": {
            SP.CONFIG_WRITERKEY: 4,
            },
        rpc_database_stream_processor + ".Reader1": {
            SP.CONFIG_HOST: MC.dbhost,
            SP.CONFIG_PORT: '54729',
            },
        }

    MC.MavenConfig.update(MavenConfig)

    fhir_persistence = FD.FHIRPersistence(CONFIG_PARAMS.PERSISTENCE_SVC.value)

    loop = asyncio.get_event_loop()
    sp_message_handler = CompositionEvaluator(rabbithandler, fhir_persistence)
    sp_message_handler.schedule(loop)

    try:
        loop.run_until_complete(asyncio.Task(fhir_persistence.test()))
        loop.run_forever()

    except KeyboardInterrupt:
        sp_message_handler.close()
        loop.close()

if __name__ == '__main__':
    run_composition_evaluator()
