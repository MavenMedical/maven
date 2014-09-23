import asyncio
import asyncio.queues
import json
from utils.database.timeout_dict import TimeoutDict
from utils.streaming.http_svcs_wrapper import CONTEXT, http_service
import maven_config as MC
import maven_logging as ML
import utils.streaming.http_responder as HR
from utils.enums import USER_ROLES  # , NOTIFICATION_STATE

CONFIG_QUEUEDELAY = 'queue delay'

RESPONSE_TEXT = 'TEXT'
RESPONSE_LINK = 'LINK'

logger = ML.get_logger()
ML.set_debug()


class NotificationService():
    def __init__(self, configname, save_task_fn, loop=None):
        self.config = MC.MavenConfig[configname]

        def expire_fn(key, value):
            user, customer = key
            for v in [] and value:
                asyncio.Task(save_task_fn(customer, user, 'Notification from Maven',
                                          v))

        self.messages = TimeoutDict(expire_fn, 2)
        self.listeners = {}
        self.queue_delay = self.config.get(CONFIG_QUEUEDELAY, 0)
        self.loop = loop or asyncio.get_event_loop()
        # self.send_messages('MAVEN', '1', ['SOME TEXT HERE'])

    @http_service(['GET'], '/poll',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: str},
                  {USER_ROLES.notification})
    @ML.coroutine_trace(logger.debug)
    def get_poll(self, _header, _body, context, _matches, _key):
        ret = []  # build the list of pending messages here.
        key = context[CONTEXT.USER], context[CONTEXT.CUSTOMERID]

        if key in self.messages:
            ret = self.messages.pop(key)
        else:
            if key in self.listeners and not self.listeners[key].done():
                f = self.listeners[key]
            else:
                f = asyncio.Future()
                self.listeners[key] = f
            try:
                # wait for a message
                ret = yield from asyncio.wait_for(f, self.queue_delay, loop=self.loop)
            except:
                pass
            finally:
                # wait_for does not cancel the future, so do that explicitly upon any error
                if not f.done():
                    f.cancel()

        return (HR.OK_RESPONSE, json.dumps(ret), None)

    @ML.trace(logger.info)
    def send_messages(self, user_name, customer, messages):
        key = user_name, customer
        ML.DEBUG(str(key) + ": " + str(messages))
        if key in self.listeners:
            f = self.listeners.pop(key)
            f.set_result(messages)
        else:
            self.messages.extend(key, messages)
        return True

import app.backend.webservices.authentication as AU


def notification_server(configname, save_task_fn=None):
    import utils.streaming.webservices_core as WC
    core_scvs = WC.WebserviceCore(configname)
    ns = NotificationService(configname, save_task_fn=save_task_fn)
    core_scvs.register_services(ns)
    core_scvs.register_services(AU.AuthenticationWebservices(configname, None,
                                                             timeout=60 * 60 * 12))
    return core_scvs, ns.send_messages
