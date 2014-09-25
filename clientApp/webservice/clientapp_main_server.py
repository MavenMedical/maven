import asyncio
from clientApp.webservice.clientapp_rpc_endpoint import ClientAppEndpoint
import utils.streaming.rpc_processor as RP
import utils.streaming.stream_processor as SP
import maven_config as MC
from maven_logging import TASK

if __name__ == '__main__':
    from app.backend.remote_procedures.server_rpc_endpoint import ServerEndpoint

    rpc_client_stream_processor = 'Client App Manager RPC Stream Processor'

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
    }

    MC.MavenConfig.update(ClientAppManagerConfig)

    loop = asyncio.get_event_loop()
    CLIENT_RPC_SVC = RP.rpc(rpc_client_stream_processor)
    CLIENT_RPC_SVC.schedule(loop)

    server_interface = CLIENT_RPC_SVC.create_client(ServerEndpoint)
    clientapp_endpoint = ClientAppEndpoint(server_interface, loop=loop)
    CLIENT_RPC_SVC.register(clientapp_endpoint)

    @asyncio.coroutine
    def get_customer_configurations():
        while True:
            try:
                yield from server_interface.get_customer_configurations()
                return
            except SP.StreamProcessorException:
                yield from asyncio.sleep(5)
                
    TASK(get_customer_configurations())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()
