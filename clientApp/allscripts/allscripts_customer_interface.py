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
import maven_config as MC
import maven_logging as ML
import clientApp.notification_generator.notification_generator as NG
import clientApp.webservice.notification_service as NS
import clientApp.webservice.user_sync_service as US
import clientApp.allscripts.allscripts_scheduler as AS
import app.backend.remote_procedures.client_app as CA
import utils.web_client.allscripts_http_client as AHC


CONFIG_API = 'api'
CLIENT_SERVER_LOG = ML.get_logger('clientApp.webservice.allscripts_server')


    def update_users(self, active_provider_list):
        self.active_providers = active_provider_list

    def check_notification_policy(self, provider, customer_id):
        key = provider, customer_id
        provider = self.active_providers.get(key)

        if provider.get('state') == USER_STATE.ACTIVE.value and provider.get('ehr_state') == USER_STATE.ACTIVE.value and provider.get('notification_state', None) is not None:
            return True
        else:
            return False


class AllscriptsCustomerInterface:

    def __init__(self, customer_id, config, server_interface):
        self.config = config
        self.customer_id = customer_id
        self.server_interface = server_interface
        self.ahc = AHC.allscripts_api(config)

        # Users and User Sync Service
        # self.active_providers = {}
        # self.user_sync_service = US.UserSyncService(CONFIG_PARAMS.EHR_USER_MGMT_SVC.value,
        #                                             remote_procedures=remote_procedure_calls,
        #                                             loop=loop)

        # EHR API Polling Service
        self.allscripts_scheduler = AS.scheduler(this, self.ahc, config)

        # self.user_sync_service.subscribe(self.notification_users_fn)
        # self.user_sync_service.subscribe(self.allscripts_scheduler.update_active_providers)

    @asyncio.coroutine
    def start(self):
        asyncio.Task(aself.allscripts_scheduler.run())

    @asyncio.coroutine
    def notify_user(self, user_name, msg):
        pass

    def run_client_app(self):

        try:
            asyncio.Task(self.user_sync_service.synchronize_users())
            asyncio.Task(self.allscripts_scheduler.get_updated_schedule())

        except KeyboardInterrupt:
            loop.close()


