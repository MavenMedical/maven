import asyncio
import asyncio.queues
import json
from utils.database.timeout_dict import TimeoutDict
from utils.streaming.http_svcs_wrapper import CONTEXT, http_service
import maven_config as MC
import maven_logging as ML
import utils.streaming.http_responder as HR
from utils.enums import USER_ROLES, NOTIFICATION_STATE

CONFIG_QUEUEDELAY = 'queue delay'

RESPONSE_TEXT = 'TEXT'
RESPONSE_LINK = 'LINK'

logger = ML.get_logger()
ML.set_debug()


class NotificationService():
    def __init__(self, configname, server_endpoint, save_task_fn, loop=None):
        self.config = MC.MavenConfig[configname]
        self.server_endpoint = server_endpoint
        self.user_notify_settings = {}

        def expire_fn(key, value):
            user, customer = key
            for v in [] and value:
                asyncio.Task(save_task_fn(customer, user, 'Notification from Maven',
                                          v))

        self.messages = TimeoutDict(expire_fn, 2)
        self.listeners = {}
        self.queue_delay = self.config.get(CONFIG_QUEUEDELAY, 0)
        self.loop = loop or asyncio.get_event_loop()
        self.save_task_fn = save_task_fn
        # self.send_messages('MAVEN', '1', ['SOME TEXT HERE'])

    @asyncio.coroutine
    def update_customer_users_notification_prefs(self, customer_id):
        user_prefs = yield from self.server_endpoint.persistence.get_users_notify_preferences(customer_id)
        for user_pref in user_prefs:
            self.update_user_notify_prefs(user_pref)

    def update_user_notify_prefs(self, user_pref):
        notify_prefs = {"notify_primary": user_pref["notify_primary"],
                        "notify_secondary": user_pref["notify_secondary"]}
        self.user_notify_settings[(user_pref['user_name'], user_pref['customer_id'])] = notify_prefs

    @http_service(['GET'], '/poll',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: str},
                  {USER_ROLES.notification})
    def get_poll(self, _header, _body, context, _matches, _key):
        ret = []  # build the list of pending messages here.
        key = context[CONTEXT.USER], int(context[CONTEXT.CUSTOMERID])

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
    def send_messages(self, user_name, customer, pat_id, messages, msg_type=None, delivery_method=None):
        key = user_name, int(customer)
        ML.DEBUG(str(key) + ": " + str(messages))

        if delivery_method == NOTIFICATION_STATE.EHR_INBOX.value and msg_type == "followup_task":
            msg_subject = messages.get('msg_subject', 'Reminder from Maven')
            msg_body = messages.get('msg_body', '')
            asyncio.Task(self.save_task_fn(key[1], key[0], msg_subject,
                                           msg_body, patient=pat_id))
            asyncio.Task(self.server_endpoint.update_followup_task_status(messages.get('task_id'), "completed"))
            return True

        elif delivery_method == NOTIFICATION_STATE.DESKTOP.value and msg_type == "followup_task":
            notify_primary = NOTIFICATION_STATE.DESKTOP.value
            notify_secondary = NOTIFICATION_STATE.OFF.value
            msg = "SUBJECT: " + messages['msg_subject'] + "\n" + "MESSAGE: " + messages['msg_body']
            asyncio.Task(self.notify_via_preference(key, [notify_primary, notify_secondary], pat_id, msg))
            asyncio.Task(self.server_endpoint.update_followup_task_status(messages.get('task_id'), "completed"))

        else:
            # Get the user's notification preferences
            notify_primary = self.user_notify_settings.get(key).get("notify_primary")
            notify_secondary = self.user_notify_settings.get(key).get("notify_secondary")

            if notify_primary == NOTIFICATION_STATE.OFF.value:
                return True

            # Try sending via Primary Notification Preference
            asyncio.Task(self.notify_via_preference(key, [notify_primary, notify_secondary], pat_id, messages))
            return True

    @asyncio.coroutine
    def notify_via_preference(self, key, notify_preferences, pat_id, messages):
        preference = notify_preferences[0]
        if preference == NOTIFICATION_STATE.DESKTOP.value:
            for _i in range(2):
                if key in self.listeners:
                    f = self.listeners.pop(key)
                    f.set_result(messages)
                    asyncio.Task(self.server_endpoint.persistence.audit_log(key[0], 'Desktop Alert', key[1], patient=pat_id))
                    return True
                else:
                    yield from asyncio.sleep(5)
            if key in self.listeners:
                f = self.listeners.pop(key)
                f.set_result(messages)
                asyncio.Task(self.server_endpoint.persistence.audit_log(key[0], 'Desktop Alert', key[1], patient=pat_id))
                return True

            ret = yield from self.notify_via_preference(key, notify_preferences[1:], pat_id, messages)
            return ret

        elif preference == NOTIFICATION_STATE.EHR_INBOX.value:
            asyncio.Task(self.save_task_fn(key[1], key[0], 'Notification from Maven',
                                           messages, patient=pat_id))
            asyncio.Task(self.server_endpoint.persistence.audit_log(key[0], 'EHR Inbox Alert', key[1], patient=pat_id))
            return True

    @http_service(['GET'], '/notifypref',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int,
                   CONTEXT.NOTIFY_PRIMARY: str, CONTEXT.NOTIFY_SECONDARY: str},
                  {USER_ROLES.notification})
    @ML.coroutine_trace(logger.debug)
    def post_notify_pref(self, _header, _body, context, _matches, _key):

        customer_id = context.get(CONTEXT.CUSTOMERID, None)
        prov_user_name = context.get(CONTEXT.USER, None)
        notify_primary = context.get(CONTEXT.NOTIFY_PRIMARY, None)
        notify_secondary = context.get(CONTEXT.NOTIFY_SECONDARY, None)

        # Check to make sure the query string contains strings as defined in NOTIFICATION_STATE enums
        is_valid_msg = self.check_notify_pref_message_body(notify_primary, notify_secondary)
        if customer_id and prov_user_name and is_valid_msg:

            is_successful_update = yield from self.server_endpoint.persistence.update_user_notify_preferences(prov_user_name, customer_id, notify_primary, notify_secondary)
            if is_successful_update:
                self.user_notify_settings[(prov_user_name, customer_id)] = {"notify_primary": notify_primary,
                                                                            "notify_secondary": notify_secondary}
                return HR.OK_RESPONSE, json.dumps(['TRUE']), None
            else:
                return HR.BAD_RESPONSE, json.dumps(['FALSE']), None
        else:
            return HR.BAD_RESPONSE, json.dumps(['FALSE']), None

    def check_notify_pref_message_body(self, notify_primary, notify_secondary):

        valid_notification_states = []
        for state in NOTIFICATION_STATE:
            valid_notification_states.append(state.value)

        if set([notify_primary, notify_secondary]).issubset(set(valid_notification_states)):
            return True
        else:
            return False


import app.backend.webservices.authentication as AU


def notification_server(configname, server_endpoint, save_task_fn=None):
    import utils.streaming.webservices_core as WC
    core_scvs = WC.WebserviceCore(configname)
    ns = NotificationService(configname, server_endpoint, save_task_fn=save_task_fn)
    core_scvs.register_services(ns)
    core_scvs.register_services(AU.AuthenticationWebservices(configname, None,
                                                             timeout=60 * 60 * 12))
    return core_scvs, ns.send_messages, ns.update_customer_users_notification_prefs
