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


CONFIG_API = 'api'
CLIENT_SERVER_LOG = ML.get_logger('clientApp.webservice.allscripts_server')


class AllscriptsCustomerInterface:

    def __init__(self, customer_id, config, server_interface):
        self.config = config
        self.customer_id = customer_id
        self.server_interface = server_interface
        self.ahc = AHC.allscripts_api(config)
        self.schedulertask = None
        self.usersynctask = None

        # Users and User Sync Service
        # self.active_providers = {}
        self.user_sync_service = US.UserSyncService(self.customer_id, config,
                                                    self.server_interface, self.ahc)

        # EHR API Polling Service
        self.allscripts_scheduler = AS.scheduler(self, self.ahc, config)

        # self.user_sync_service.subscribe(self.notification_users_fn)
        # self.user_sync_service.subscribe(self.allscripts_scheduler.update_active_providers)

    @asyncio.coroutine
    def start(self):
        working = yield from self.ahc.GetServerInfo()
        if working:
            self.schedulertask = asyncio.Task(self.allscripts_scheduler.run())
            self.usersynctask = asyncio.Task(self.user_sync_service.synchronize_users())
            return True
        else:
            return False

    @asyncio.coroutine
    def test_and_update_config(self, config):
        # ahc = AHC.allscripts_api(config)
        # working = yield from ahc.GetServerInfo()
        # if working:
        #     self.ahc = ahc
        #     self.schedulertask.cancel()
        #      self.usersynctask.cancel()
        pass

    @asyncio.coroutine
    def notify_user(self, user_name, msg):
        pass

    def update_active_providers(self, active_provider_list):
        self.active_providers = active_provider_list
