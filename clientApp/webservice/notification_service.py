import asyncio
import asyncio.queues
import json
from collections import defaultdict
from utils.streaming.http_svcs_wrapper import CONTEXT, http_service, CONFIG_PERSISTENCE
import maven_config as MC
import maven_logging as ML
import utils.streaming.http_responder as HR
from utils.enums import USER_ROLES

CONFIG_QUEUEDELAY = 'queue delay'

RESPONSE_TEXT = 'TEXT'
RESPONSE_LINK = 'LINK'

logger = ML.get_logger()
ML.set_debug()


class NotificationService():
    def __init__(self, configname, loop=None):
        self.config = MC.MavenConfig[configname]
        self.message_queues = defaultdict(asyncio.queues.Queue)
        self.queue_delay = self.config.get(CONFIG_QUEUEDELAY, 0)
        self.loop = loop or asyncio.get_event_loop()

    @http_service(['GET'], '/poll',
                  [CONTEXT.PROVIDER, CONTEXT.CUSTOMERID],
                  {CONTEXT.PROVIDER: str, CONTEXT.CUSTOMERID: str},
                  {USER_ROLES.notification})
    @ML.coroutine_trace(logger.debug)
    def get_poll(self, _header, _body, context, _matches, _key):
        ret = []  # build the list of pending messages here.
        key = context[CONTEXT.PROVIDER], context[CONTEXT.CUSTOMERID]
        queue = self.message_queues[key]
        if not queue.qsize():  # if there are no messages ready to display, wait for one
            f = asyncio.async(queue.get())
            try:
                # wait for a message
                y = yield from asyncio.wait_for(f, self.queue_delay, loop=self.loop)
                ret.append(y)
            except:
                # wait_for does not cancel the future, so do that explicitly upon any error
                f.cancel()
        try:
            while True:  # read and append all available messages on the queue
                logger.debug(("Reading queue"))
                ret.append(queue.get_nowait())
        except:
            pass
        return (HR.OK_RESPONSE, json.dumps(ret), None)

    # @http_service(['GET'], '/posl',
    #              [CONTEXT.PROVIDER, CONTEXT.CUSTOMERID],
    #              {CONTEXT.PROVIDER: str, CONTEXT.CUSTOMERID: str},
    #              {USER_ROLES.notification})
    @ML.coroutine_trace(logger.debug)
    def get_post(self, _header, _body, context, _matches, _key):
        # this function will not work as is
        # key = qs[QS_KEY][0]
        # message = qs['message'][0]
        # self.send_messages(key, [self._convert_message(message)])
        return (HR.OK_RESPONSE, b'', None)

    def _convert_message(self, message):
        m = message.split('\n', 1)
        if len(m) == 2:
            return {
                RESPONSE_TEXT: m[1],
                RESPONSE_LINK: m[0],
                }
        else:
            return {
                RESPONSE_TEXT: message,
                RESPONSE_LINK: 'http://www.google.com',
                }

    @ML.trace(logger.info)
    def send_messages(self, provider, customer, messages=None):
        key = provider, customer
        ML.DEBUG(str(key) + ": " + str(messages))
        if key in self.message_queues:
            if messages:
                for message in messages:
                    self.message_queues[key].put_nowait(message)
                    logger.debug(('new queue size is ' + str(self.message_queues[key].qsize())))
            return True
        else:
            logger.debug('user is not listening')
            return False


def standalone_notification_server(configname):
    import utils.streaming.webservices_core as WC
    from app.backend.webservices.authentication import AuthenticationWebservices
    core_scvs = WC.WebserviceCore(configname)
    core_scvs.register_services(NotificationService(configname))
    core_scvs.register_services(AuthenticationWebservices(configname,
                                                          specific_role=USER_ROLES.notification,
                                                          timeout=60 * 60 * 12))
    return core_scvs


def run():
    import utils.streaming.stream_processor as SP
    import utils.database.web_persistence as WP
    from utils.database.database import AsyncConnectionPool
    import asyncio

    MC.MavenConfig = {
        'notificationserver':
        {
            SP.CONFIG_HOST: 'localhost',
            SP.CONFIG_PORT: 8092,
            SP.CONFIG_PARSERTIMEOUT: 120,
            CONFIG_QUEUEDELAY: 30,
            CONFIG_PERSISTENCE: "persistence layer",
        },
        'persistence layer': {WP.CONFIG_DATABASE: 'webservices conn pool', },
        'webservices conn pool':
        {
            AsyncConnectionPool.CONFIG_CONNECTION_STRING: MC.dbconnection,
            AsyncConnectionPool.CONFIG_MIN_CONNECTIONS: 4,
            AsyncConnectionPool.CONFIG_MAX_CONNECTIONS: 8
        }
    }

    core_scvs = standalone_notification_server('notificationserver')
    event_loop = asyncio.get_event_loop()
    core_scvs.schedule(event_loop)
    event_loop.run_forever()

if __name__ == '__main__':
    run()
