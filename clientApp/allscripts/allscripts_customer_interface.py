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
# LAST MODIFIED FOR JIRA ISSUE: MAV-289
# *************************************************************************
import asyncio
import maven_logging as ML
import clientApp.webservice.user_sync_service as US
import clientApp.allscripts.allscripts_scheduler as AS
import utils.web_client.allscripts_http_client as AHC
import clientApp.notification_generator.notification_generator as NG
from utils.enums import CONFIG_PARAMS


CONFIG_API = 'api'
CLIENT_SERVER_LOG = ML.get_logger('clientApp.webservice.allscripts_customer_interface')


class AllscriptsCustomerInterface:

    def __init__(self, customer_id, config, server_interface):
        self.config = config
        self.customer_id = customer_id
        self.server_interface = server_interface
        self.ahc = AHC.allscripts_api(config)
        self.schedulertask = None
        self.usersynctask = None

        # EHR API Polling Service
        EHR_polling_interval = config.get(CONFIG_PARAMS.EHR_API_POLLING_INTERVAL.value, 45)
        EHR_disabled = config.get(CONFIG_PARAMS.EHR_DISABLE_INTEGRATION.value, False)
        self.allscripts_scheduler = AS.scheduler(self, self.customer_id, self.ahc,
                                                 EHR_polling_interval, EHR_disabled)

        # Users and User Sync Service
        user_sync_interval = config.get(CONFIG_PARAMS.EHR_USER_SYNC_INTERVAL.value, 60 * 60)
        self.user_sync_service = US.UserSyncService(self.customer_id, user_sync_interval,
                                                    self.server_interface, self.ahc, EHR_disabled)

        self.notification_generator = NG.NotificationGenerator(config)

        # Register the EHR API Polling Service's "Refresh Active Providers" Function with the User Sync Service
        self.user_sync_service.subscribe(self.allscripts_scheduler.update_active_providers)

        # self.user_sync_service.subscribe(self.notification_users_fn)
        # self.user_sync_service.subscribe(self.allscripts_scheduler.update_active_providers)

    @asyncio.coroutine
    def validate_config(self):
        yield from self.ahc.test_login()

    @asyncio.coroutine
    def start(self):
        # Load the Customer's Users' Notification Preferences
        yield from self.server_interface.update_notify_prefs(self.customer_id)

        self.schedulertask = ML.TASK(self.allscripts_scheduler.run())
        self.usersynctask = ML.TASK(self.user_sync_service.run())

    @asyncio.coroutine
    def update_config(self, config):
        if config == self.config:
            return
        self.config = config
        self.ahc.update_config(self.config)
        self.allscripts_scheduler.update_config(self.config)
        self.user_sync_service.update_config(self.config)
        if not self.config.get(CONFIG_PARAMS.EHR_DISABLE_INTEGRATION.value, False):
            yield from self.server_interface.update_notify_prefs(self.customer_id)

    @asyncio.coroutine
    def notify_user(self, user_name, patient, subject, msg, target):
        try:
            yield from self.ahc.SaveTask(user_name, patient, msg_subject=subject,
                                         message_data=msg, targetuser=target)
            ML.INFO('sending message from %s to %s' % (user_name, target))
        except:
            ML.WARN('failed to send message from %s to %s' % (user_name, target))
            raise

    @asyncio.coroutine
    def handle_evaluated_composition(self, composition):

        CLIENT_SERVER_LOG.debug(("Received Composition Object from the Maven backend engine: ID = %s" % composition.id))
        # ## tom: this has no authentication yet
        # composition.customer_id
        user = composition.author.get_provider_username().upper()
        customer = str(composition.customer_id)
        pat_id = composition.subject.get_pat_id()
        alerts_section = composition.get_section_by_coding(code_system="maven", code_value="alerts")

        if len(alerts_section.content) > 0:
            ML.report('/%s/alert_fired/%s' % (customer, user))
            msg = yield from self.notification_generator.generate_alert_content(composition, 'web', None)
            CLIENT_SERVER_LOG.debug(("Generated Message content: %s" % msg))
            yield from self.server_interface.notify_user(customer, user, pat_id, msg)

    @asyncio.coroutine
    def evaluate_composition(self, composition):
        yield from self.server_interface.evaluate_composition(composition)

    def update_user(self, user_name, state):
        self.user_sync_service.update_active_provider_state(user_name, state)
