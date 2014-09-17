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
import utils.database.web_persistence as WP
import asyncio
from utils.enums import CONFIG_PARAMS
import maven_config as MC


class ClientAppManagerRemoteProcedureCalls():

    def __init__(self):
        self.persistence = WP.WebPersistence(CONFIG_PARAMS.PERSISTENCE_SVC.value)

    @asyncio.coroutine
    def get_customer_configurations(self):

        desired = {
            WP.Results.customerid: 'customer_id',
            WP.Results.name: 'name',
            WP.Results.abbr: 'abbr',
            WP.Results.license: 'license_type',
            WP.Results.license_exp: 'license_exp',
            WP.Results.config: 'config'
        }
        results = yield from self.persistence.customer_info(desired, limit=None)

        return results
