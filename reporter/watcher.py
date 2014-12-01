import asyncio
import json
import utils.streaming.stream_processor as SP
import utils.streaming.rpc_processor as RP
import maven_config as MC
from reporter.stats_interface import StatsInterface
import utils.streaming.webservices_core as WC
from utils.streaming.http_svcs_wrapper import http_service
import utils.streaming.http_responder as HTTP


class WatcherWebService:

    def __init__(self, statsinterface):
        self.si = statsinterface

    @http_service(['GET'], '(.*)', None, None, None)
    def stats(self, _header, _body, context, matches, _key):
        path = matches[0]
        minutes = yield from self.si.minutestats(path)
        hours = yield from self.si.hourstats(path)
        days = yield from self.si.daystats(path)
        return HTTP.OK_RESPONSE, json.dumps({'minutes': minutes, 'hours': hours, 'days': days}), None


def main():

    rpc_server_stream_processor = 'rpc_server'
    http_server = 'http_server'
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
            SP.CONFIG_HOST: 'localhost',
            SP.CONFIG_PORT: '54320',
        },
        http_server: {
            SP.CONFIG_PORT: '54321',
        },
    }
    MC.MavenConfig.update(MavenConfig)
    loop = asyncio.get_event_loop()

    rpc = RP.rpc(rpc_server_stream_processor)
    rpc.schedule(loop)
    si = StatsInterface()
    rpc.register(si)

    web_scvs = WC.WebserviceCore(http_server)
    web_scvs.schedule(loop)
    web_scvs.register_services(WatcherWebService(si))
    loop.run_forever()

main()
