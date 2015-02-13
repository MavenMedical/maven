# *************************************************************************
# Copyright (c) 2014 - Maven Medical
#
# ************************
# AUTHOR:
__author__ = 'Tom Dubois, Yuki Uchino'
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
import utils.streaming.http_responder as HR
import clientApp.notification_generator.notification_generator as NG
import utils.streaming.rpc_processor as RP
from utils.api.vista.emr_parser import VistaParser
from utils.enums import CONFIG_PARAMS, USER_ROLES
import app.database.web_persistence as WP
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
from app.backend.webservices.reporting import ReportingWebservices
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


##########################################################################################
##########################################################################################
#####
# Pathway Stream Processors
#####
##########################################################################################
##########################################################################################
class IncomingPathwayMessageHandler(SP.StreamProcessor):

    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)
        self.master_list = ['', '', '', '', '']
        self.object_manager = []

    @asyncio.coroutine
    def read_object(self, obj, key2):
        obj_list = pickle.loads(obj)
        composition = obj_list[0]
        key1 = obj_list[1]
        ML.DEBUG(key1)
        composition.write_key = [key1, key2]
        self.write_object(composition, writer_key="PathEval")


class OutgoingPathwaysMessageHandler(SP.StreamProcessor):

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
            ML.report('/%s/evaluated_composition' % (customer_id,))
            yield from self.client_interface.handle_evaluated_composition(customer_id, obj)


##########################################################################################
##########################################################################################
#####
# Transparent Stream Processors
#####
##########################################################################################
##########################################################################################
class IncomingTransparentMessageHandler(HR.HTTPReader):

    def __init__(self, configname):
        HR.HTTPReader.__init__(self, configname)
        # TODO - Need to change the EMR Parser based on config
        self.emr_msg_parser = VistaParser()

    @asyncio.coroutine
    def read_object(self, obj, key):
        try:
            body = obj[1]
            if not len(body):
                self.write_object(HR.wrap_response(HR.BAD_RESPONSE, b'', None), key)
            else:
                message = body.decode()
                composition = self.emr_msg_parser.create_composition(message)
                composition.write_key = [key]

                # We actually send this to the same composition evaluator that evaluates Pathways
                # The composition evaluator determines what needs to be done and will write back to
                # different read_object() methods in this file so they're handled appropriately (since
                # Transparent handles the delivery of the notification differently than Pathways
                self.write_object(composition, writer_key='PathEval')
        except:
            try:
                self.write_object(HR.wrap_response(HR.ERROR_RESPONSE, b'', None), key)
            except:
                # TODO - maven logging here instead of quietly passing
                pass


class OutgoingTransparentMessageHandler(HR.HTTPWriter):

    def __init__(self, configname, notification_service=None):
        HR.HTTPWriter.__init__(self, configname)
        self.notification_generator = NG.NotificationGenerator(MC.MavenConfig[configname])
        self.notification_service = notification_service

    @asyncio.coroutine
    def format_response(self, obj, _):

        # TODO - Fix hardcoded authentication for Transparent
        obj.userAuth = AK.authorization_key(['YUKIU', str(obj.customer_id)], 44, 60 * 60)
        # obj.userAuth = AK.authorization_key([obj.author.get_provider_username(), str(obj.customer_id)], 44, 60 * 60)

        notifications = yield from self.notification_generator.generate_alert_content(obj, 'vista', None)
        alert_notification_content = ""
        if notifications is not None and len(notifications) > 0:
            for notification_body in notifications:
                alert_notification_content += str(notification_body)

        ML.DEBUG("NOTIFY HTML BODY: " + alert_notification_content)

        return (HR.OK_RESPONSE, alert_notification_content, [], obj.write_key[0])


def main(loop):

    outgoingtohospitalsmessagehandler = 'responder socket'
    incomingtomavenmessagehandler = 'receiver socket'
    transparentmessageconsumer = 'transparent consumer socket'
    transparentoutgoingproducer = 'transparent producer socket'
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
            SP.CONFIG_WRITERNAME: [incomingtomavenmessagehandler + ".Writer_CostEval",
                                   incomingtomavenmessagehandler + ".Writer_PathEval"],
            SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_IDENTITYPARSER,
            SP.CONFIG_WRITERDYNAMICKEY: 1,
        },
        incomingtomavenmessagehandler + ".Reader":
        {
            SP.CONFIG_HOST: '127.0.0.1',
            SP.CONFIG_PORT: 8090
        },
        incomingtomavenmessagehandler + ".Writer_PathEval":
        {
            SP.CONFIG_HOST: 'localhost',
            SP.CONFIG_QUEUE: 'incoming_path_evaluator_work_queue',
            SP.CONFIG_EXCHANGE: 'maven_exchange',
            SP.CONFIG_KEY: 'incomingpatheval',
            SP.CONFIG_WRITERKEY: 'PathEval'
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
            SP.CONFIG_KEY: 'pathwaysoutgoing',
        },

        outgoingtohospitalsmessagehandler + ".Writer":
        {
            SP.CONFIG_WRITERKEY: 1
        },
        transparentmessageconsumer:
            {
                SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSERVERSOCKET,
                SP.CONFIG_READERNAME: transparentmessageconsumer + ".Reader",
                SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
                SP.CONFIG_WRITERNAME: transparentmessageconsumer + ".Writer",
                SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_IDENTITYPARSER,
                SP.CONFIG_WRITERDYNAMICKEY: 7,
                HR.CONFIG_SSLAUTH: None,
                },
        transparentmessageconsumer + ".Reader":
            {
                SP.CONFIG_HOST: '127.0.0.1',
                SP.CONFIG_PORT: 8088
            },
        transparentmessageconsumer + ".Writer":
        {
            SP.CONFIG_HOST: 'localhost',
            SP.CONFIG_QUEUE: 'incoming_path_evaluator_work_queue',
            SP.CONFIG_EXCHANGE: 'maven_exchange',
            SP.CONFIG_KEY: 'incomingpatheval',
            SP.CONFIG_WRITERKEY: 'PathEval',
        },
        transparentoutgoingproducer:
            {
                SP.CONFIG_READERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
                SP.CONFIG_READERNAME: transparentoutgoingproducer + ".Reader",
                SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETREPLY,
                SP.CONFIG_WRITERNAME: transparentoutgoingproducer + ".Writer",
                SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_UNPICKLEPARSER,
            },
        transparentoutgoingproducer + ".Reader":
            {
                SP.CONFIG_HOST: 'localhost',
                SP.CONFIG_QUEUE: 'transparent_send_queue',
                SP.CONFIG_EXCHANGE: 'maven_exchange',
                SP.CONFIG_KEY: 'transparent',
            },
        transparentoutgoingproducer + ".Writer":
            {
                SP.CONFIG_WRITERKEY: 7
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
            SP.CONFIG_ONDISCONNECT: SP.CONFIGVALUE_DISCONNECTRESTART,
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
            SP.CONFIG_ONDISCONNECT: SP.CONFIGVALUE_DISCONNECTRESTART,
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

    if MC.reporterhost:
        reporter_rpc = RP.rpc(rpc_reporter_stream_processor)
        reporter_rpc.schedule(loop)
        stats_interface = reporter_rpc.create_client(StatsInterface)
        import socket
        hostname = socket.gethostname()
        ML.report = lambda s: asyncio.async(stats_interface.insert(hostname + '/' + str(s)))

        @asyncio.coroutine
        def heartbeat():
            while True:
                try:
                    yield from asyncio.sleep(1)
                    ML.report('/heartbeat')
                except:
                    pass

        asyncio.async(heartbeat())

    sp_consumer = IncomingPathwayMessageHandler(incomingtomavenmessagehandler)
    sp_consumer.schedule(loop)

    transparent_consumer = IncomingTransparentMessageHandler(transparentmessageconsumer)
    transparent_consumer.schedule(loop)

    transparent_producer = OutgoingTransparentMessageHandler(transparentoutgoingproducer)
    transparent_producer.schedule(loop)

    client_interface = clientapp_rpc.create_client(ClientAppEndpoint)
    server_endpoint = ServerEndpoint(client_interface,
                                     lambda x: sp_consumer.write_object(x, writer_key="PathEval"))
    server_endpoint.persistence.schedule(loop)
    clientapp_rpc.register(server_endpoint)

    sp_producer = OutgoingPathwaysMessageHandler(outgoingtohospitalsmessagehandler, client_interface)
    sp_producer.schedule(loop)

    core_scvs = WC.WebserviceCore('httpserver', client_interface=client_interface)
    for c in [AU.AuthenticationWebservices, PatientMgmtWebservices,
              UserMgmtWebservices, SearchWebservices,
              TransparentWebservices, PathwaysWebservices,
              AdministrationWebservices, SupportWebservices,
              TimedFollowUpService, ReportingWebservices]:
        core_scvs.register_services(c('httpserver', clientapp_rpc))
    core_scvs.schedule(loop)

    (notification_service,
     notification_fn,
     update_notify_prefs_fn) = NS.notification_server(CONFIG_PARAMS.NOTIFY_SVC.value,
                                                      server_endpoint,
                                                      client_interface.notify_user,
                                                      client_interface.listening_state)
    followup_task_service = TimedFollowUpService(CONFIG_PARAMS.FOLLOWUP_SVC.value, server_endpoint)

    notification_service.schedule(loop)

    server_endpoint.set_notification_function(notification_fn)
    server_endpoint.set_update_notify_prefs_fn(update_notify_prefs_fn)

    try:
        TASK(followup_task_service.run())
        if MC.wrap_exception:
            ML.wrap_exception()
        loop.run_forever()
    except KeyboardInterrupt:
        sp_consumer.close()
        sp_producer.close()
        loop.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    main(loop)
