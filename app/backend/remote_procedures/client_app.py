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
# LAST MODIFIED FOR JIRA ISSUE: MAV-404
# *************************************************************************
import asyncio
import utils.database.web_persistence as WP
import utils.streaming.stream_processor as SP
from utils.enums import CONFIG_PARAMS


class ClientAppRemoteProcedureCalls(SP.StreamProcessor):

    def __init__(self):

        self.persistence = WP.WebPersistence(CONFIG_PARAMS.PERSISTENCE_SVC.value)

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
        return results

    @asyncio.coroutine
    def write_user_create_to_db(self, customer_id, provider_info):
        yield from self.persistence.EHRsync_create_user_provider(provider_info)

    @asyncio.coroutine
    def write_user_deactivation_to_db(self, customer_id, provider_info):
        yield from self.persistence.EHRsync_update_user_provider(provider_info)

    @asyncio.coroutine
    def evaluate_composition(self, composition):
        raise NotImplementedError
