# *************************************************************************
# Copyright (c) 2014 - Maven Medical
#
# ************************
# AUTHOR:
__author__ = 'Yuki Uchino'
# ************************
# DESCRIPTION:   This file provides the webservice calls required for User Management
#
# ************************
# ASSUMES:
# ************************
# SIDE EFFECTS:
# ************************
# LAST MODIFIED FOR JIRA ISSUE: MAV-303
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


class UserMgmtWebservices():

    def __init__(self, configname):
        config = MC.MavenConfig[configname]
        self.persistence = WP.WebPersistence(config[CONFIG_PERSISTENCE])

    @http_service(['GET'], '/alerts(?:(\d+)-(\d+)?)?',
                  [CONTEXT.PROVIDER, CONTEXT.CUSTOMERID],
                  {CONTEXT.PROVIDER: str, CONTEXT.PATIENTLIST: list, CONTEXT.CUSTOMERID: int,
                   CONTEXT.ENCOUNTER: str, CONTEXT.STARTDATE: date, CONTEXT.ENDDATE: date,
                   CONTEXT.ORDERID: str, CONTEXT.CATEGORIES: list},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_alerts(self, _header, _body, context, matches, _key):
        provider = context[CONTEXT.PROVIDER]
        patients = context.get(CONTEXT.PATIENTLIST, None)
        customer = context[CONTEXT.CUSTOMERID]
        orderid = context.get(CONTEXT.ORDERID, None)
        categories = context.get(CONTEXT.CATEGORIES, None)

        startdate = self.helper.get_date(context, CONTEXT.STARTDATE)
        enddate = self.helper.get_date(context, CONTEXT.ENDDATE)
        limit = self.helper.limit_clause(matches)

        desired = {
            WP.Results.alertid: 'id',
            # WP.Results.patientid: 'patient',
            WP.Results.datetime: 'date',
            WP.Results.title: 'name',
            WP.Results.description: 'html',
            WP.Results.savings: 'cost',
            WP.Results.alerttype: 'alerttype',
            WP.Results.ruleid: 'ruleid',
            WP.Results.likes: 'likes',
            WP.Results.dislikes: 'dislikes'
        }

        results = yield from self.persistence.alerts(desired, provider, customer,
                                                     patients=patients,
                                                     startdate=startdate,
                                                     enddate=enddate,
                                                     limit=limit, orderid=orderid,
                                                     categories=categories)

        if results and patients and len(patients) == 1:
            asyncio.Task(self.persistence.audit_log(provider, 'get alerts web service',
                                                    customer, patients[0], rows=len(results)))

        return HTTP.OK_RESPONSE, json.dumps(results), None

    @http_service(['GET'], '/rate_alert',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID, CONTEXT.ALERTID, CONTEXT.ACTION,
                   CONTEXT.RULEID, CONTEXT.CATEGORY],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int, CONTEXT.ALERTID: int,
                   CONTEXT.ACTION: str, CONTEXT.RULEID: str, CONTEXT.CATEGORY: str},
                  {USER_ROLES.provider})
    def rate_alert(self, _header, _body, context, _matches, _key):
        userid = context[CONTEXT.USER]
        customer = context[CONTEXT.CUSTOMERID]
        alertid = context[CONTEXT.ALERTID]
        action = context[CONTEXT.ACTION]
        category = context[CONTEXT.CATEGORY]
        ruleid = context[CONTEXT.RULEID]
        if ruleid == "null":
            ruleid = "0"

        desired = {
            WP.Results.action: 'action',
        }

        update = 0
        result = yield from self.persistence.alert_settings(desired, userid, customer,
                                                            alertid, ruleid, category)
        if result:
            # record exists so update, don't add
            update = 1

        result = yield from self.persistence.rate_alert(customer, userid, category,
                                                        "", alertid, ruleid, "", action,
                                                        update=update)

        # return HTTP.OK_RESPONSE, json.dumps(['ALERT LIKED']), None
        if result:
            return HTTP.OK_RESPONSE, json.dumps(['TRUE']), None
        else:
            return HTTP.OK_RESPONSE, json.dumps(['FALSE']), None

    @http_service(['GET'], '/critique_alert',
                  [CONTEXT.CUSTOMERID, CONTEXT.RULEID, CONTEXT.USER,
                   CONTEXT.CATEGORY, CONTEXT.ACTIONCOMMENT, CONTEXT.ALERTID],
                  {CONTEXT.CUSTOMERID: int, CONTEXT.RULEID: int, CONTEXT.CATEGORY: str,
                   CONTEXT.ACTIONCOMMENT: str, CONTEXT.USER: str, CONTEXT.ALERTID: int},
                  {USER_ROLES.provider})
    def critique_alert(self, _header, _body, context, _matches, _key):
        userid = context[CONTEXT.USER]
        customerid = context[CONTEXT.CUSTOMERID]
        alertid = context[CONTEXT.ALERTID]
        actioncomment = context[CONTEXT.ACTIONCOMMENT]
        category = context[CONTEXT.CATEGORY]
        ruleid = context[CONTEXT.RULEID]
        if ruleid == "null":
            ruleid = "0"

        result = yield from self.persistence.update_alert_setting(userid, customerid,
                                                                  alertid, ruleid,
                                                                  category, actioncomment)
        if result:
            return HTTP.OK_RESPONSE, json.dumps(['TRUE']), None
        else:
            return HTTP.OK_RESPONSE, json.dumps(['FALSE']), None

    @http_service(['GET'], '/save_user_settings',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID, CONTEXT.OFFICIALNAME, CONTEXT.DISPLAYNAME],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int,
                   CONTEXT.OFFICIALNAME: str, CONTEXT.DISPLAYNAME: str},
                  None)
    def save_user_settings(self, _header, _body, context, _matches, _key):
        userid = context[CONTEXT.USER]
        officialname = context[CONTEXT.OFFICIALNAME]
        displayname = context[CONTEXT.DISPLAYNAME]

        result = yield from self.persistence.update_user_settings(userid, officialname,
                                                                  displayname)
        if result:
            return HTTP.OK_RESPONSE, json.dumps(['TRUE']), None
        else:
            return HTTP.OK_RESPONSE, json.dumps(['FALSE']), None
