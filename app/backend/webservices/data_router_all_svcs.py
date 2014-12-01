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
from utils.enums import CONFIG_PARAMS, USER_ROLES
import utils.database.web_persistence as WP
from app.backend.remote_procedures.server_rpc_endpoint import ServerEndpoint
import asyncio
import maven_config as MC
import utils.crypto.authorization_key as AK
import maven_logging as ML
from maven_logging import TASK
from utils.streaming.http_svcs_wrapper import CONFIG_PERSISTENCE
import utils.streaming.webservices_core as WC
from app.backend.webservices.transparent import TransparentWebservices
from app.backend.webservices.pathways import PathwaysWebservices
import app.backend.webservices.authentication as AU
from app.backend.webservices.patient_mgmt import PatientMgmtWebservices
from app.backend.webservices.user_mgmt import UserMgmtWebservices
from app.backend.webservices.search import SearchWebservices
from app.backend.webservices.administration import AdministrationWebservices
from app.backend.webservices.support import SupportWebservices
from app.backend.webservices.timed_followup import TimedFollowUpService
import app.backend.webservices.notification_service as NS
from reporter.stats_interface import StatsInterface
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

    def __init__(self, configname, client_interface):
        SP.StreamProcessor.__init__(self, configname)
        self.client_interface = client_interface

    @asyncio.coroutine
    def read_object(self, obj, _):
        obj.user = obj.author.get_provider_username()
        obj.userAuth = AK.authorization_key([obj.user, str(obj.customer_id)], 44, 60 * 60)

        if obj.write_key is not None:
            self.write_object(pickle.dumps(obj), writer_key=obj.write_key[1])
        else:
            customer_id = obj.customer_id
            yield from self.client_interface.handle_evaluated_composition(customer_id, obj)


def main(loop):

    outgoingtohospitalsmessagehandler = 'responder socket'
    incomingtomavenmessagehandler = 'receiver socket'
    rpc_server_stream_processor = 'Server-side RPC Stream Processor'
    rpc_database_stream_processor = 'Client to Database RPC Stream Processor'
    rpc_reporter_stream_processor = 'Server to Reporter RPC Stream Processor'
    from clientApp.webservice.clientapp_rpc_endpoint import ClientAppEndpoint

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
            SP.CONFIG_WRITERNAME: [incomingtomavenmessagehandler + ".Writer",
                                   incomingtomavenmessagehandler + ".Writer_CostEval"],
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
        CONFIG_PARAMS.PERSISTENCE_SVC.value: {WP.CONFIG_DATABASE: rpc_database_stream_processor},
        "httpserver":
        {
            SP.CONFIG_HOST: 'localhost',
            SP.CONFIG_PORT: 8087,
            CONFIG_PERSISTENCE: CONFIG_PARAMS.PERSISTENCE_SVC.value,
        },
        'persistence layer': {WP.CONFIG_DATABASE: rpc_database_stream_processor},
        'persistance': {WP.CONFIG_DATABASE: rpc_database_stream_processor},
        'search': {WP.CONFIG_DATABASE: rpc_database_stream_processor},
        CONFIG_PARAMS.NOTIFY_SVC.value:
        {
            SP.CONFIG_HOST: 'localhost',
            SP.CONFIG_PORT: 8092,
            SP.CONFIG_PARSERTIMEOUT: 50,
            NS.CONFIG_QUEUEDELAY: 45,
            "persistence": CONFIG_PARAMS.PERSISTENCE_SVC.value,
            AU.CONFIG_SPECIFICROLE: USER_ROLES.notification.value,
            AU.CONFIG_OAUTH: True,
        },
        CONFIG_PARAMS.FOLLOWUP_SVC.value:
        {
            SP.CONFIG_HOST: 'localhost',
            SP.CONFIG_PORT: 8093,
            CONFIG_PARAMS.FOLLOWUP_SLEEP_INTERVAL.value: 60,
            "persistence": CONFIG_PARAMS.PERSISTENCE_SVC.value,
        },
        rpc_database_stream_processor: {
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETREPLY,
            SP.CONFIG_WRITERNAME: rpc_database_stream_processor + '.Writer1',
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETQUERY,
            SP.CONFIG_READERNAME: rpc_database_stream_processor + '.Reader1',
            SP.CONFIG_WRITERDYNAMICKEY: 3,
            SP.CONFIG_DEFAULTWRITEKEY: 3,
        },
        rpc_database_stream_processor + ".Writer1": {
            SP.CONFIG_WRITERKEY: 3,
        },
        rpc_database_stream_processor + ".Reader1": {
            SP.CONFIG_HOST: MC.dbhost,
            SP.CONFIG_PORT: '54729',
        },
        rpc_reporter_stream_processor: {
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETREPLY,
            SP.CONFIG_WRITERNAME: rpc_reporter_stream_processor + '.Writer1',
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETQUERY,
            SP.CONFIG_READERNAME: rpc_reporter_stream_processor + '.Reader1',
            SP.CONFIG_WRITERDYNAMICKEY: 12,
            SP.CONFIG_DEFAULTWRITEKEY: 12,
        },
        rpc_reporter_stream_processor + ".Writer1": {
            SP.CONFIG_WRITERKEY: 12,
        },
        rpc_reporter_stream_processor + ".Reader1": {
            SP.CONFIG_HOST: MC.reporterhost,
            SP.CONFIG_PORT: '54320',
        },
    }
    MC.MavenConfig.update(MavenConfig)

    persistence = WP.WebPersistence(CONFIG_PARAMS.PERSISTENCE_SVC.value)

    @asyncio.coroutine
    def get_key():
        while True:
            try:
                yield from asyncio.sleep(1)
                bytes = yield from persistence.shared_secret()
                AK.set_secret(bytes)
                return
            except:
                ML.EXCEPTION('Could not get secret from server')

    asyncio.Task(get_key())

    clientapp_rpc = RP.rpc(rpc_server_stream_processor)
    clientapp_rpc.schedule(loop)

    reporter_rpc = RP.rpc(rpc_reporter_stream_processor)
    reporter_rpc.schedule(loop)
    stats_interface = reporter_rpc.create_client(StatsInterface)
    ML.report = lambda s: asyncio.async(stats_interface.insert(str(s)))

    @asyncio.coroutine
    def heartbeat():
        while True:
            try:
                yield from asyncio.sleep(1)
                ML.report('/heartbeat')
            except:
                pass

    asyncio.async(heartbeat())

    sp_consumer = IncomingMessageHandler(incomingtomavenmessagehandler)
    sp_consumer.schedule(loop)

    client_interface = clientapp_rpc.create_client(ClientAppEndpoint)
    server_endpoint = ServerEndpoint(client_interface,
                                     lambda x: sp_consumer.write_object(x, writer_key="CostEval"))
    server_endpoint.persistence.schedule(loop)
    clientapp_rpc.register(server_endpoint)

    sp_producer = OutgoingMessageHandler(outgoingtohospitalsmessagehandler, client_interface)
    sp_producer.schedule(loop)

    core_scvs = WC.WebserviceCore('httpserver', client_interface=client_interface)
    for c in [AU.AuthenticationWebservices, PatientMgmtWebservices,
              UserMgmtWebservices, SearchWebservices,
              TransparentWebservices, PathwaysWebservices,
              AdministrationWebservices, SupportWebservices,
              TimedFollowUpService]:
        core_scvs.register_services(c('httpserver', clientapp_rpc))
    core_scvs.schedule(loop)

    (notification_service,
     notification_fn,
     update_notify_prefs_fn) = NS.notification_server(CONFIG_PARAMS.NOTIFY_SVC.value,
                                                      server_endpoint,
                                                      client_interface.notify_user)
    followup_task_service = TimedFollowUpService(CONFIG_PARAMS.FOLLOWUP_SVC.value, server_endpoint)

    notification_service.schedule(loop)

    server_endpoint.set_notification_function(notification_fn)
    server_endpoint.set_update_notify_prefs_fn(update_notify_prefs_fn)

    try:
        TASK(followup_task_service.run())
        loop.run_forever()
    except KeyboardInterrupt:
        sp_consumer.close()
        sp_producer.close()
        loop.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    main(loop)
