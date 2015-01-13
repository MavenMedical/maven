import asyncio
import utils.streaming.stream_processor as SP
import utils.streaming.rpc_processor as RP
import maven_config as MC
from reporter.stats_interface import StatsInterface
import utils.streaming.webservices_core as WC
from utils.streaming.http_svcs_wrapper import http_service
import utils.streaming.http_responder as HTTP
from datetime import datetime


class WatcherWebService:

    def __init__(self, statsinterface):
        self.si = statsinterface
        self.dob = datetime.now().strftime('%a, %B %d %H:%M')

    @classmethod
    def makerow(self, prefix, title, data):
        titlelink = '<a href="%s/%s">/%s</a>' % (prefix, title, title)
        return '<tr><td>' + '</td><td>'.join([titlelink] + list(data)) + '</td></tr>'

    @classmethod
    def makesection(self, prefix, title, data):
        section = """<h3>%s</h3><table><tr><th>Path</th>%s</tr>%s</table>"""
        times = map(lambda x: x['stoptime'].strftime('%a %d %H:%M'), data)
        times = '<th>' + '</th><th>'.join(times) + '</th>'
        formatteddata = ''
        children = set()
        children.update(*[d['children'].keys() for d in data])
        formatteddata = self.makerow(prefix, '', map(lambda x: str(x['self']), data))
        formatteddata += '\n'.join([self.makerow(prefix, child,
                                                 map(lambda x: str(x['children'].get(child, 0)), data))
                                    for child in children])

        return section % (title, times, formatteddata)

    @http_service(['GET'], '/(.*)', None, None, None)
    def stats(self, _header, _body, context, matches, _key):
        path = matches[0]
        minutes = yield from self.si.minutestats(path)
        hours = yield from self.si.hourstats(path)
        days = yield from self.si.daystats(path)

        frame = "<html><head></head><body> Monitor started on %s <hr> %s %s %s %s</body></html>"
        splitpath = list(filter(lambda x: x, path.split('/')))
        pathsofar = ''
        breadcrumb = ['<a href="/">(root)</a>']
        for path in splitpath:
            pathsofar = pathsofar + '/' + path
            breadcrumb.append('<a href="%s">%s</a> ' % (pathsofar, path))
        breadcrumb = '  '.join(breadcrumb)

        resp = frame % (self.dob, breadcrumb,
                        self.makesection(path, 'Minutes', minutes),
                        self.makesection(path, 'Hours', hours),
                        self.makesection(path, 'Days', days))
        return HTTP.OK_RESPONSE, resp, [b'Content-Type: text/html']


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
            SP.CONFIG_PORT: '54320',
        },
        http_server: {
            SP.CONFIG_PORT: '54321',
            SP.CONFIG_PARSERTIMEOUT: 50,
            'contenttype': 'text/html',
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
