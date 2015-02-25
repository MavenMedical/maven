# *************************************************************************
# Copyright (c) 2014 - Maven Medical
# ************************
# AUTHOR:
__author__ = 'Yuki Uchino'
# ************************
# DESCRIPTION:
#
# This file runs with the data_router_all_services, but it's interface (over rpc) runs in
# the clientApp.  So the clientApp can remotely call any of these functions, and they will
# execute on the data_router
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
import app.database.web_persistence as WP
import utils.streaming.stream_processor as SP
from utils.enums import CONFIG_PARAMS
import maven_logging as ML


class ServerEndpoint(SP.StreamProcessor):

    def __init__(self, client_interface, comp_eval_writer_fn):

        self.persistence = WP.WebPersistence(CONFIG_PARAMS.PERSISTENCE_SVC.value)
        self.client_interface = client_interface
        self.notification_fn = None
        self.comp_eval_writer_fn = comp_eval_writer_fn
        self.update_notify_user_prefs_fn = None

    def set_update_notify_prefs_fn(self, fn):
        self.update_notify_user_prefs_fn = fn

    @asyncio.coroutine
    def update_notify_prefs(self, customer_id):
        yield from self.update_notify_user_prefs_fn(customer_id)

    @asyncio.coroutine
    def get_users_from_db(self, customer_id):

        desired = {
            WP.Results.userid: 'user_id',
            WP.Results.customerid: 'customer_id',
            WP.Results.provid: 'prov_id',
            WP.Results.username: 'user_name',
            WP.Results.officialname: 'official_name',
            WP.Results.displayname: 'display_name',
            WP.Results.state: 'state',
            WP.Results.ehrstate: 'ehr_state'
        }
        results = yield from self.persistence.customer_specific_user_info(desired,
                                                                          limit=None,
                                                                          customer_id=customer_id)

        # for result in results:
        #    self.client_interface.update_customer(result)
        # return True
        # @Tom I call this from the Allscripts Client Interface (user sync service) and expect the values returned to
        # the function that called it. So I don't think we need to call the clientapp_rpc_endpoint here.
        return results

    @asyncio.coroutine
    def write_user_create_to_db(self, customer_id, provider_info):
        ret = yield from self.persistence.EHRsync_create_user_provider(provider_info)
        return ret

    @asyncio.coroutine
    def write_user_update_to_db(self, customer_id, provider_info):
        yield from self.persistence.EHRsync_update_user_provider(provider_info)

    def set_notification_function(self, fn):
        self.notification_fn = fn

    @asyncio.coroutine
    def notify_user(self, customer_id, user_name, pat_id, msg, msg_type=None, delivery_method=None):
        if self.notification_fn:
            if msg_type == "followup_task":
                self.notification_fn(user_name, customer_id, pat_id, messages=msg, msg_type=msg_type, delivery_method=delivery_method)
            elif msg_type is None:
                if not isinstance(msg, list):
                    msg = [msg]
                self.notification_fn(user_name, customer_id, pat_id, messages=msg, msg_type=msg_type, delivery_method=delivery_method)

    @asyncio.coroutine
    def update_followup_task_status(self, task_id, status):
        yield from self.persistence.update_followup_task_status(task_id, status)

    @asyncio.coroutine
    def get_customer_configurations(self):

        desired = {
            WP.Results.customerid: 'customer_id',
            WP.Results.name: 'name',
            WP.Results.abbr: 'abbr',
            WP.Results.license: 'license_type',
            WP.Results.license_exp: 'license_exp',
            WP.Results.settings: 'settings'
        }
        results = yield from self.persistence.customer_info(desired, limit=None)

        for result in results:
            asyncio.Task(self.client_interface.update_customer_configuration(result['customer_id'],
                                                                             result['settings']))
        return

    @asyncio.coroutine
    def get_customer_configuration(self, customer_id):

        desired = {
            WP.Results.customerid: 'customer_id',
            WP.Results.name: 'name',
            WP.Results.abbr: 'abbr',
            WP.Results.license: 'license_type',
            WP.Results.license_exp: 'license_exp',
            WP.Results.settings: 'settings'
        }
        result = yield from self.persistence.customer_info(desired, customer=customer_id,
                                                           limit=None)

        if result:
            asyncio.Task(self.client_interface.update_customer_configuration(result['customer_id'],
                                                                             result['settings']))
        return

    @asyncio.coroutine
    def evaluate_composition(self, composition):
        self.comp_eval_writer_fn(composition)

    @asyncio.coroutine
    def write_audit_log(self, user_name, action, customer_id, patient=None, device=None,
                        details=None, rows=None, target_user=None):
        if target_user:
            targets = (target_user, customer_id)
        else:
            targets = None
        asyncio.Task(self.persistence.audit_log(user_name, action, customer_id, patient=patient,
                                                device=device, details=details, rows=rows,
                                                target_user_and_customer=targets))

    @asyncio.coroutine
    def report(self, path):
        ML.report('/clientapp/' + path)
