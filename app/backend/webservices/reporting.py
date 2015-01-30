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
import app.database.web_persistence as WP
from utils.streaming.http_svcs_wrapper import http_service, CONTEXT, CONFIG_PERSISTENCE
import utils.streaming.http_responder as HTTP
import maven_config as MC
date = str


class ReportingWebservices():

    def __init__(self, configname, rpc):
        config = MC.MavenConfig[configname]
        self.persistence = WP.WebPersistence(config[CONFIG_PERSISTENCE])

    @http_service(['GET'], '/interaction_details',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID, CONTEXT.TARGETUSER, CONTEXT.PATIENT,
                   CONTEXT.PROTOCOL, CONTEXT.ACTIVITY],
                  {CONTEXT.TARGETUSER: str, CONTEXT.PATIENT: str, CONTEXT.CUSTOMERID: int,
                   CONTEXT.USER: str, CONTEXT.PROTOCOL: int, CONTEXT.ACTIVITY: int},
                  {USER_ROLES.supervisor})
    def get_interaction_details(self, _header, _body, context, _matches, _key):
        user = context[CONTEXT.USER]
        targetuser = context[CONTEXT.TARGETUSER]
        protocol = context[CONTEXT.PROTOCOL]
        startactivity = context[CONTEXT.ACTIVITY]
        patient = context[CONTEXT.PATIENT]
        customer = context[CONTEXT.CUSTOMERID]

        asyncio.async(self.persistence.audit_log(user, 'get interaction', customer,
                                                 patient=patient,
                                                 details=json.dumps([protocol, targetuser])))

        results = yield from self.persistence.interaction_details(customer, targetuser, patient,
                                                                  protocol, startactivity)
        if results:
            summary = yield from self.persistence.encounter_report(customer, targetuser, patient,
                                                                   results[0]['datetime'])

        return HTTP.OK_RESPONSE, json.dumps({'base': results, 'summary': summary}), None

    @http_service(['GET'], '/interactions(?:(\d+)-(\d+)?)?',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID],
                  {CONTEXT.PATIENTLIST: list, CONTEXT.CUSTOMERID: int,
                   CONTEXT.STARTDATE: date, CONTEXT.ENDDATE: date, CONTEXT.USER: str},
                  {USER_ROLES.supervisor})
    def get_interactions(self, _header, _body, context, matches, _key):
        user = context[CONTEXT.USER]
        # provider = context.get(CONTEXT.TARGETPROVIDER, None)
        # patients = context.get(CONTEXT.PATIENTLIST, None)
        customer = context[CONTEXT.CUSTOMERID]

        # startdate = self.helper.get_date(context, CONTEXT.STARTDATE)
        # enddate = self.helper.get_date(context, CONTEXT.ENDDATE)
        limit = self.helper.limit_clause(matches)

        desired = {
            WP.Results.activityid: CONTEXT.ACTIVITY,
            WP.Results.patientid: CONTEXT.PATIENT,
            WP.Results.patientname: CONTEXT.PATIENTNAME,
            WP.Results.protocolname: 'protocolname',
            WP.Results.protocol: CONTEXT.PROTOCOL,
            WP.Results.datetime: 'date',
            WP.Results.username: 'providername',
            WP.Results.userid: CONTEXT.TARGETUSER,
            WP.Results.count: 'eventcount',
        }

        results = yield from self.persistence.interactions(desired, customer,
                                                           # provider=provider,
                                                           # patients=patients,
                                                           # startdate=startdate,
                                                           # enddate=enddate,
                                                           limit=limit)

        if results:
            asyncio.Task(self.persistence.audit_log(user, 'get interactions web service',
                                                    customer, rows=len(results)))

        return HTTP.OK_RESPONSE, json.dumps(results), None
