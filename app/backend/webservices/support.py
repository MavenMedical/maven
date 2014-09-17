# *************************************************************************
# Copyright (c) 2014 - Maven Medical
#
# ************************
# AUTHOR:
__author__ = 'Carlos Brenneisen'
# ************************
# DESCRIPTION:   This file provides the webservice calls required for Maven Support
#
# ************************
# ASSUMES:
# ************************
# SIDE EFFECTS:
# ************************
# LAST MODIFIED FOR JIRA ISSUE: MAV-
# *************************************************************************
# from utils.streaming.webservices_core import *

from utils.enums import USER_ROLES
import json
import asyncio
import utils.database.web_persistence as WP
from utils.streaming.http_svcs_wrapper import http_service, CONTEXT, CONFIG_PERSISTENCE
import utils.streaming.http_responder as HTTP
import maven_config as MC
from datetime import datetime
from dateutil.relativedelta import relativedelta

date = str


class SupportWebservices():

    def __init__(self, configname):
        config = MC.MavenConfig[configname]
        self.persistence = WP.WebPersistence(config[CONFIG_PERSISTENCE])

    @http_service(['GET'], '/customers(?:(\d+)-(\d+)?)?',
                  [CONTEXT.USERID],
                  {CONTEXT.USERID: int},
                  {USER_ROLES.mavensupport})
    def get_customers(self, _header, _body, context, matches, _key):
        limit = self.helper.limit_clause(matches)

        desired = {
            WP.Results.customerid: 'customer_id',
            WP.Results.name: 'name',
            WP.Results.abbr: 'abbr',
            WP.Results.license: 'license_type',
            WP.Results.license_exp: 'license_exp',
            WP.Results.config: 'config',
            WP.Results.settings: 'settings'
        }
        results = yield from self.persistence.customer_info(desired, customer=None, limit=limit)

        return HTTP.OK_RESPONSE, json.dumps(results), None

    @http_service(['GET'], '/update_customer',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID, CONTEXT.STATE, CONTEXT.TARGETUSER],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int,
                   CONTEXT.STATE: str, CONTEXT.TARGETUSER: int},
                  {USER_ROLES.supervisor})
    def update_customer(self, _header, _body, context, _matches, _key):
        userid = context[CONTEXT.TARGETUSER]
        state = context[CONTEXT.STATE]

        result = yield from self.persistence.update_user(userid, state)
        if result:
            return HTTP.OK_RESPONSE, json.dumps(['TRUE']), None
        else:
            return HTTP.OK_RESPONSE, json.dumps(['FALSE']), None

    @http_service(['GET'], '/add_customer',
                  [CONTEXT.USERID, CONTEXT.NAME, CONTEXT.CONFIG,
                   CONTEXT.ABBREVIATION, CONTEXT.LICENSE],
                  {CONTEXT.USERID: int, CONTEXT.LICENSE: int,
                   CONTEXT.NAME: str, CONTEXT.ABBREVIATION: str,
                   CONTEXT.CONFIG: str},
                  {USER_ROLES.mavensupport})
    def add_customer(self, _header, _body, context, _matches, _key):
        name = context[CONTEXT.NAME]
        abbr = context[CONTEXT.ABBREVIATION]
        license = context[CONTEXT.LICENSE]
        license_exp = datetime.now() + relativedelta(years=1)
        config = context[CONTEXT.CONFIG]

        result = yield from self.persistence.add_customer(name, abbr, license, license_exp, config)
        if result:
            return HTTP.OK_RESPONSE, json.dumps(['TRUE']), None
        else:
            return HTTP.OK_RESPONSE, json.dumps(['FALSE']), None
