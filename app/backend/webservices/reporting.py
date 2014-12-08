# *************************************************************************
# Copyright (c) 2014 - Maven Medical
#
# ************************
# AUTHOR:
__author__ = 'Tom DuBois'
# ************************
# DESCRIPTION:   This file provides the webservice calls required for
#                reports and retrospective analysis
#
# ************************
# ASSUMES:
# ************************
# SIDE EFFECTS:
# ************************
# LAST MODIFIED FOR JIRA ISSUE:
# *************************************************************************
# from utils.streaming.webservices_core import *
from utils.enums import USER_ROLES
import json
import asyncio
import utils.database.web_persistence as WP
from utils.streaming.http_svcs_wrapper import http_service, CONTEXT, CONFIG_PERSISTENCE
import utils.streaming.http_responder as HTTP
import maven_config as MC
date = str


class ReportingWebservices():

    def __init__(self, configname, rpc):
        config = MC.MavenConfig[configname]
        self.persistence = WP.WebPersistence(config[CONFIG_PERSISTENCE])

    @http_service(['GET'], '/interactions(?:(\d+)-(\d+)?)?',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID],
                  {CONTEXT.PROVIDER: str, CONTEXT.PATIENTLIST: list, CONTEXT.CUSTOMERID: int,
                   CONTEXT.STARTDATE: date, CONTEXT.ENDDATE: date, CONTEXT.USER: str},
                  {USER_ROLES.supervisor})
    def get_interactions(self, _header, _body, context, matches, _key):
        user = context[CONTEXT.USER]
        provider = context.get(CONTEXT.PROVIDER, None)
        patients = context.get(CONTEXT.PATIENTLIST, None)
        customer = context[CONTEXT.CUSTOMERID]

        startdate = self.helper.get_date(context, CONTEXT.STARTDATE)
        enddate = self.helper.get_date(context, CONTEXT.ENDDATE)
        limit = self.helper.limit_clause(matches)

        desired = {
            WP.Results.activityid: 'id',
            WP.Results.patientid: 'patient',
            WP.Results.protocol: 'protocol',
            WP.Results.datetime: 'date',
            WP.Results.username: 'provider',
        }

        results = yield from self.persistence.interactions(desired, customer,
                                                           provider=provider,
                                                           patients=patients,
                                                           startdate=startdate,
                                                           enddate=enddate,
                                                           limit=limit)

        if results:
            asyncio.Task(self.persistence.audit_log(user, 'get interactions web service',
                                                    customer, rows=len(results)))

        return HTTP.OK_RESPONSE, json.dumps(results), None
