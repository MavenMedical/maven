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
import app.database.web_persistence as WP
from utils.streaming.http_svcs_wrapper import http_service, CONTEXT, CONFIG_PERSISTENCE
import utils.streaming.http_responder as HTTP
from clientApp.webservice.clientapp_rpc_endpoint import ClientAppEndpoint
import maven_config as MC
date = str


class UserMgmtWebservices():

    def __init__(self, configname, rpc):
        self.client_interface = rpc.create_client(ClientAppEndpoint)
        config = MC.MavenConfig[configname]
        self.persistence = WP.WebPersistence(config[CONFIG_PERSISTENCE])

    @http_service(['GET'], '/alerts(?:(\d+)-(\d+)?)?',
                  [CONTEXT.PROVIDER, CONTEXT.USER, CONTEXT.CUSTOMERID],
                  {CONTEXT.PROVIDER: str, CONTEXT.PATIENTLIST: list, CONTEXT.CUSTOMERID: int,
                   CONTEXT.ENCOUNTER: str, CONTEXT.STARTDATE: date, CONTEXT.ENDDATE: date,
                   CONTEXT.ORDERID: str, CONTEXT.CATEGORIES: list, CONTEXT.USER: str},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_alerts(self, _header, _body, context, matches, _key):
        user = context[CONTEXT.USER]
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
            asyncio.Task(self.persistence.audit_log(user, 'get alerts web service',
                                                    customer, patients[0], rows=len(results)))

        return HTTP.OK_RESPONSE, json.dumps(results), None

    # handles when a user either likes or dislikes an alert
    @http_service(['GET'], '/rate_alert',
                  [CONTEXT.USERID, CONTEXT.CUSTOMERID, CONTEXT.ALERTID, CONTEXT.ACTION,
                   CONTEXT.RULEID, CONTEXT.CATEGORY],
                  {CONTEXT.USERID: int, CONTEXT.CUSTOMERID: int, CONTEXT.ALERTID: int,
                   CONTEXT.ACTION: str, CONTEXT.RULEID: str, CONTEXT.CATEGORY: str},
                  {USER_ROLES.provider})
    def rate_alert(self, _header, _body, context, _matches, _key):
        userid = context[CONTEXT.USERID]
        customer = context[CONTEXT.CUSTOMERID]
        alertid = context[CONTEXT.ALERTID]
        action = context[CONTEXT.ACTION]
        category = context[CONTEXT.CATEGORY]
        ruleid = context[CONTEXT.RULEID]
        if ruleid is not int:
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

        if result:
            return HTTP.OK_RESPONSE, json.dumps(['TRUE']), None
        else:
            return HTTP.OK_RESPONSE, json.dumps(['FALSE']), None

    # handles when a user provides extra information as to why he/she liked/disliked an alert
    @http_service(['GET'], '/critique_alert',
                  [CONTEXT.CUSTOMERID, CONTEXT.RULEID, CONTEXT.USERID,
                   CONTEXT.CATEGORY, CONTEXT.ACTIONCOMMENT, CONTEXT.ALERTID],
                  {CONTEXT.CUSTOMERID: int, CONTEXT.RULEID: str, CONTEXT.CATEGORY: str,
                   CONTEXT.ACTIONCOMMENT: str, CONTEXT.USERID: int, CONTEXT.ALERTID: int},
                  {USER_ROLES.provider})
    def critique_alert(self, _header, _body, context, _matches, _key):
        userid = context[CONTEXT.USERID]
        customerid = context[CONTEXT.CUSTOMERID]
        alertid = context[CONTEXT.ALERTID]
        actioncomment = context[CONTEXT.ACTIONCOMMENT]
        category = context[CONTEXT.CATEGORY]
        ruleid = context[CONTEXT.RULEID]
        if ruleid is not int:
            ruleid = "0"

        result = yield from self.persistence.update_alert_setting(userid, customerid,
                                                                  alertid, ruleid,
                                                                  category, actioncomment)
        if result:
            return HTTP.OK_RESPONSE, json.dumps(['TRUE']), None
        else:
            return HTTP.OK_RESPONSE, json.dumps(['FALSE']), None

    # handles when a user updates his/her profile settings
    @http_service(['GET'], '/save_user_settings',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID, CONTEXT.OFFICIALNAME, CONTEXT.DISPLAYNAME],
                  {CONTEXT.USER: str, CONTEXT.CUSTOMERID: int,
                   CONTEXT.OFFICIALNAME: str, CONTEXT.DISPLAYNAME: str},
                  {USER_ROLES.provider, USER_ROLES.supervisor, USER_ROLES.mavensupport, USER_ROLES.administrator})
    def save_user_settings(self, _header, _body, context, _matches, _key):
        user = context[CONTEXT.USER]
        customer = context[CONTEXT.CUSTOMERID]
        officialname = context[CONTEXT.OFFICIALNAME]
        displayname = context[CONTEXT.DISPLAYNAME]

        result = yield from self.persistence.save_user_settings(user, customer, officialname, displayname)
        if result:
            return HTTP.OK_RESPONSE, json.dumps(['TRUE']), None
        else:
            return HTTP.OK_RESPONSE, json.dumps(['FALSE']), None

    # returns a list of audits with the specified information
    @http_service(['GET'], '/audits(?:(\d+)-(\d+)?)?',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID, CONTEXT.ROLES],
                  {CONTEXT.CUSTOMERID: int,
                   CONTEXT.STARTDATE: date, CONTEXT.ENDDATE: date,
                   CONTEXT.USER: str, CONTEXT.ROLES: list,
                   CONTEXT.TARGETUSER: str, CONTEXT.TARGETCUSTOMER: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor, USER_ROLES.mavensupport, USER_ROLES.administrator})
    def get_audits(self, _header, _body, context, matches, _key):
        target_user = None
        customer = None

        if (USER_ROLES.supervisor.name in context[CONTEXT.ROLES] or
                USER_ROLES.administrator.name in context[CONTEXT.ROLES] or
                USER_ROLES.mavensupport.name in context[CONTEXT.ROLES]):
            target_user = context.get(CONTEXT.TARGETUSER, None)
        if USER_ROLES.mavensupport.name in context[CONTEXT.ROLES]:
            customer = context.get(CONTEXT.TARGETCUSTOMER, None)

        if not target_user:
            target_user = context[CONTEXT.USER]
        if not customer:
            customer = context[CONTEXT.CUSTOMERID]

        startdate = self.helper.get_date(context, CONTEXT.STARTDATE)
        enddate = self.helper.get_date(context, CONTEXT.ENDDATE)
        limit = self.helper.limit_clause(matches)

        desired = {
            WP.Results.auditid: 'id',
            WP.Results.datetime: 'date',
            WP.Results.userid: 'user',
            WP.Results.patientid: 'patient',
            WP.Results.action: 'action',
            WP.Results.details: 'details',
            WP.Results.device: 'device',
            WP.Results.target_user: 'target',
        }

        results = yield from self.persistence.audit_info(desired, target_user, customer,
                                                         startdate=startdate,
                                                         enddate=enddate, limit=limit)

        return HTTP.OK_RESPONSE, json.dumps(results), None

    # used to return a list of recipients, typically for an autocomplete box. Can return users and/or groups
    @http_service(['GET'], '/recipients(?:(\d+)-(\d+)?)?',
                  [CONTEXT.CUSTOMERID],
                  {CONTEXT.CUSTOMERID: int, CONTEXT.ROLES: list,
                   CONTEXT.NAME: str, CONTEXT.TARGETROLE: str},
                  {USER_ROLES.administrator, USER_ROLES.provider,
                   USER_ROLES.mavensupport, USER_ROLES.supervisor})
    def get_recipients(self, _header, _body, context, matches, _key):
        customer = context[CONTEXT.CUSTOMERID]
        name = context.get(CONTEXT.NAME, None)
        targetrole = context.get(CONTEXT.TARGETROLE, None)
        limit = self.helper.limit_clause(matches)

        results = yield from self.persistence.get_recipients(customer, role=targetrole, search_term=name, limit=limit)

        return (HTTP.OK_RESPONSE,
                json.dumps([{'label': k[0], 'value': k[1]} for k in results]),
                None)

    # returns a list of user groups
    @http_service(['GET'], '/user_group/(\d+)',
                  [CONTEXT.CUSTOMERID],
                  {CONTEXT.CUSTOMERID: int, CONTEXT.ROLES: list, CONTEXT.NAME: str},
                  {USER_ROLES.administrator, USER_ROLES.supervisor, USER_ROLES.provider})
    def get_group(self, _header, _body, context, matches, _key):
        customer = context[CONTEXT.CUSTOMERID]
        id = matches[0]
        desired = {WP.Results.username: 'value', WP.Results.userid: 'id', WP.Results.officialname: 'label'}

        users = yield from self.persistence.membership_info(desired, customer, group=id)

        results = yield from self.persistence.get_groups(customer, None, None, id)

        ret = {'users': users, 'name': results[0]['term'], 'id': id, 'description': results[0]['description']}

        return HTTP.OK_RESPONSE, json.dumps(ret), None

    @http_service(['PUT'], '/user_group/(\d+)',
                  [CONTEXT.CUSTOMERID],
                  {CONTEXT.CUSTOMERID: int, CONTEXT.ROLES: list, CONTEXT.NAME: str},
                  {USER_ROLES.administrator, USER_ROLES.supervisor, USER_ROLES.provider})
    def put_group(self, _header, _body, context, matches, _key):
        customer = context[CONTEXT.CUSTOMERID]
        id = matches[0]
        body = json.loads(_body.decode('utf-8'))
        usersJSON = body['users']
        name = body['name']
        description = body['description']

        body = yield from self.persistence.update_group(customer, id, name, description, "", usersJSON)

        return HTTP.OK_RESPONSE, json.dumps({}), None

    @http_service(['GET'], '/user_group/',
                  [CONTEXT.CUSTOMERID],
                  {CONTEXT.CUSTOMERID: int, CONTEXT.ROLES: list, CONTEXT.NAME: str},
                  {USER_ROLES.administrator, USER_ROLES.supervisor, USER_ROLES.provider})
    def get_groups(self, _header, _body, context, matches, _key):
        customer = context[CONTEXT.CUSTOMERID]
        search_term = context.get(CONTEXT.NAME, None)
        results = yield from self.persistence.get_groups(customer, search_term=search_term)
        return HTTP.OK_RESPONSE, json.dumps(results), None

    @http_service(['DELETE'], '/user_group/(\d+)',
                  [CONTEXT.CUSTOMERID],
                  {CONTEXT.CUSTOMERID: int, CONTEXT.ROLES: list, CONTEXT.NAME: str},
                  {USER_ROLES.administrator, USER_ROLES.supervisor, USER_ROLES.provider})
    def remove_group(self, _header, _body, context, matches, _key):
        customer = context[CONTEXT.CUSTOMERID]
        results = yield from self.persistence.remove_group(customer, matches[0])
        return HTTP.OK_RESPONSE, json.dumps(results), None

    @http_service(['POST'], '/user_group/',
                  [CONTEXT.CUSTOMERID],
                  {CONTEXT.CUSTOMERID: int, CONTEXT.ROLES: list, CONTEXT.NAME: str},
                  {USER_ROLES.administrator, USER_ROLES.supervisor, USER_ROLES.provider})
    def create_group(self, _header, _body, context, matches, _key):
        customer = context[CONTEXT.CUSTOMERID]
        body = json.loads(_body.decode('utf-8'))

        yield from self.persistence.create_group(customer, body['term'], body['description'])
        return HTTP.OK_RESPONSE, json.dumps({}), None

    # send a messge to either a user or group
    @http_service(['POST'], '/send_message',
                  [CONTEXT.CUSTOMERID, CONTEXT.USER, CONTEXT.TARGETUSER],
                  {CONTEXT.CUSTOMERID: int, CONTEXT.USER: str,
                   CONTEXT.TARGETUSER: str, CONTEXT.PATIENTLIST: str},
                  {USER_ROLES.provider, USER_ROLES.supervisor, USER_ROLES.administrator})
    def send_message(self, _header, body, context, _matches, _key):
        user = context[CONTEXT.USER]
        customer = context[CONTEXT.CUSTOMERID]
        patient = context.get(CONTEXT.PATIENTLIST, None)
        body = json.loads(body.decode('utf-8'))
        subject = body['subject'] + " - " + user
        message = body['message']
        target = context[CONTEXT.TARGETUSER]

        if target.startswith('user_'):
            # send to an individual user
            target = target.replace('user_', '')

            subject = body['subject'] + " - " + user
            message = body['message']
            # patient = body.get('patient', None)
            yield from self.client_interface.notify_user(customer, user, subject, message,
                                                         patient=patient, target=target)
            return HTTP.OK_RESPONSE, b'', None

        elif target.startswith('group_'):
            # send to a group
            group = target.replace('group_', '')

            results = yield from self.persistence.membership_info({WP.Results.username: 'user_name'},
                                                                  customer, group=group)
            for row in results:
                target = row['user_name']
                yield from self.client_interface.notify_user(customer, user, subject, message,
                                                             patient=patient, target=target)
            return HTTP.OK_RESPONSE, b'', None

        return HTTP.BAD_REQUEST, json.dumps("INVALID RECIPIENT"), None

    # returns a full list of audits (no limit) with certain parameters
    @http_service(['GET'], '/download_audits',
                  [CONTEXT.PROVIDER, CONTEXT.USER, CONTEXT.CUSTOMERID],
                  {CONTEXT.PROVIDER: str, CONTEXT.PATIENTLIST: list, CONTEXT.CUSTOMERID: int,
                   CONTEXT.ENCOUNTER: str, CONTEXT.STARTDATE: date, CONTEXT.ENDDATE: date,
                   CONTEXT.ORDERID: str, CONTEXT.CATEGORIES: list, CONTEXT.USER: str,
                   CONTEXT.TARGETPROVIDER: str, CONTEXT.TARGETCUSTOMER: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor, USER_ROLES.administrator})
    def download_audits(self, _header, _body, context, matches, _key):
        provider = context.get(CONTEXT.TARGETPROVIDER, None)
        customer = context.get(CONTEXT.TARGETCUSTOMER, None)
        if not provider:
            provider = context[CONTEXT.PROVIDER]
        if not customer:
            customer = context[CONTEXT.CUSTOMERID]

        startdate = self.helper.get_date(context, CONTEXT.STARTDATE)
        enddate = self.helper.get_date(context, CONTEXT.ENDDATE)

        desired = {
            WP.Results.auditid: 'id',
            WP.Results.datetime: 'date',
            WP.Results.userid: 'user',
            WP.Results.patientid: 'patient',
            WP.Results.action: 'action',
            WP.Results.details: 'details',
            WP.Results.device: 'device',
        }

        results = yield from self.persistence.audit_info(desired, provider, customer,
                                                         startdate=startdate,
                                                         enddate=enddate, limit=None)

        return HTTP.OK_RESPONSE, json.dumps(results), None
