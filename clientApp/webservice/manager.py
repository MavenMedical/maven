# *************************************************************************
# Copyright (c) 2014 - Maven Medical
# ************************
# AUTHOR:
__author__ = 'Yuki Uchino'
# ************************
# DESCRIPTION:
#
#
#
#
# ************************
# ASSUMES:
# ************************
# SIDE EFFECTS:
# ************************
# LAST MODIFIED FOR JIRA ISSUE: MAV-404
# *************************************************************************
import asyncio
from uuid import uuid1
import json
import app.backend.remote_procedures.client_app_manager as CAM
import utils.streaming.rpc_processor as RP
import utils.streaming.stream_processor as SP
import clientApp.webservice.allscripts_client_app as ALLSCRIPTS_CA
from utils.enums import CONFIG_PARAMS
import maven_config as MC


class ClientAppManager():

    def __init__(self, remote_procedures=None, loop=None):
        self.shard_uuid = uuid1()
        self.client_apps = {}
        self.remote_procedures = remote_procedures or Exception("No Remote Procedures Specified for ClientAppManager")
        self.loop = loop or asyncio.get_event_loop()

    @asyncio.coroutine
    def load_client_app_configurations(self):
        customers = yield from self.remote_procedures.get_customer_configurations()
        return [customer for customer in customers if customer.get('config', None)]

    @asyncio.coroutine
    def test_client_app_configuration(self):
        pass

    @asyncio.coroutine
    def start_client_app(self, customer_id, client_config):
        # self.test_client_app_configuration(client_config)
        client_app = ALLSCRIPTS_CA.AllscriptsClientApp(customer_id, client_config, loop=self.loop)
        yield from client_app.run_client_app()


    @asyncio.coroutine
    def stop_client_app(self):
        raise NotImplementedError

    @asyncio.coroutine
    def restart_client_app(self):
        raise NotImplementedError

    @asyncio.coroutine
    def update_client_app_log_settings(self):
        raise NotImplementedError


@asyncio.coroutine
def main(CLIENT_APP_MGR_SVC):

    customer_configs = yield from CLIENT_APP_MGR_SVC.load_client_app_configurations()

    for customer_config in customer_configs:
        if customer_config['customer_id'] == 5:
            config = json.loads(customer_config.get('config'))
            yield from CLIENT_APP_MGR_SVC.start_client_app(customer_config.get('customer_id'), config)

    while True:
        print("Client App Manager Sleeping for 10 seconds")
        yield from asyncio.sleep(10)


if __name__ == '__main__':

    rpc_client_stream_processor = 'Client App Manager RPC Stream Processor'
    rpc_server_stream_processor = 'Client App Manager Server-side RPC Stream Processor'

    ClientAppManagerConfig = {
        rpc_client_stream_processor: {
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETREPLY,
            SP.CONFIG_WRITERNAME: rpc_client_stream_processor + '.Writer1',
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETQUERY,
            SP.CONFIG_READERNAME: rpc_client_stream_processor + '.Reader1',
            SP.CONFIG_WRITERDYNAMICKEY: 2,
            SP.CONFIG_DEFAULTWRITEKEY: 2,
        },
        rpc_client_stream_processor + ".Writer1": {
            SP.CONFIG_WRITERKEY: 2,
        },
        rpc_client_stream_processor + ".Reader1": {
            SP.CONFIG_HOST: '127.0.0.1',
            SP.CONFIG_PORT: '54728',
        },
        rpc_server_stream_processor: {
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETREPLY,
            SP.CONFIG_WRITERNAME: rpc_server_stream_processor + '.Writer2',
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETQUERY,
            SP.CONFIG_READERNAME: rpc_server_stream_processor + '.Reader2',
            SP.CONFIG_WRITERDYNAMICKEY: 2,
            SP.CONFIG_DEFAULTWRITEKEY: 2,
        },
        rpc_server_stream_processor + ".Writer2": {
            SP.CONFIG_WRITERKEY: 2,
        },
        rpc_server_stream_processor + ".Reader2": {
            SP.CONFIG_PORT: '54728',
        },
    }

    MC.MavenConfig.update(ClientAppManagerConfig)

    loop = asyncio.get_event_loop()
    CLIENT_RPC_SVC = RP.rpc(rpc_client_stream_processor)
    CLIENT_RPC_SVC.schedule(loop)
    client_app_mgr_procedure_calls = CLIENT_RPC_SVC.create_client(CAM.ClientAppManagerRemoteProcedureCalls)

    CLIENT_APP_MGR_SVC = ClientAppManager(remote_procedures=client_app_mgr_procedure_calls, loop=loop)

    try:
        asyncio.Task(main(CLIENT_APP_MGR_SVC))
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()