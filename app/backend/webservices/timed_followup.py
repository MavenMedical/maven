# *************************************************************************
# Copyright (c) 2014 - Maven Medical
#
# ************************
# AUTHOR:
__author__ = 'Yuki Uchino'
# ************************
# DESCRIPTION:   This file provides the webservice calls required for Maven Timed Follow-Up Functionality
#
# ************************
# ASSUMES:
# ************************
# SIDE EFFECTS:
# ************************
# LAST MODIFIED FOR JIRA ISSUE: MAV-503
# *************************************************************************
from utils.enums import USER_ROLES
import json
import utils.database.web_persistence as WP
from utils.streaming.http_svcs_wrapper import http_service, CONTEXT, CONFIG_PERSISTENCE
from clientApp.webservice.clientapp_rpc_endpoint import ClientAppEndpoint
import dateutil.relativedelta
import dateutil.parser
import utils.streaming.http_responder as HTTP
import maven_config as MC


class TimedFollowUpWebservices():

    def __init__(self, configname, rpc):
        self.client_interface = rpc.create_client(ClientAppEndpoint)
        config = MC.MavenConfig[configname]
        self.persistence = WP.WebPersistence(config[CONFIG_PERSISTENCE])

    @http_service(['POST'], '/add_task',
                  [CONTEXT.USERID, CONTEXT.CUSTOMERID],
                  {CONTEXT.USERID: int, CONTEXT.CUSTOMERID: int, CONTEXT.TARGETUSER: str, CONTEXT.PATIENTLIST: str},
                  {USER_ROLES.provider, USER_ROLES.supervisor, USER_ROLES.administrator})
    def post_task(self, _header, body, context, _matches, _key):
        customer_id = context.get(CONTEXT.CUSTOMERID)
        author_id = context.get(CONTEXT.USERID)
        target_username = context.get(CONTEXT.TARGETUSER, None)
        patient_id = context.get(CONTEXT.PATIENTLIST, None)

        delivery_method = body.get('delivery', None)
        msg_subject = body.get('msg_subject', None)
        msg_body = body.get('msg_body', None)

        # Parse out the DUE datetime
        due_datetime_str = body.get('due', None)
        due_datetime = due_datetime_str and dateutil.parser.parse(due_datetime_str)

        # Parse out the EXPIRE datetime if it exists, and if it doesn't exist make the default DUE + 1year
        expire_datetime_str = body.get('expire', None)
        if expire_datetime_str:
            expire_datetime = dateutil.parser.parse(expire_datetime_str)
        else:
            expire_datetime = due_datetime + dateutil.relativedelta.relativedelta(years=1)

        insert_task_result = yield from self.persistence.insert_followup_task(customer_id, author_id, target_username, patient_id,
                                                                              delivery_method, due_datetime, expire_datetime, msg_subject, msg_body)

        if insert_task_result:
            return HTTP.OK_RESPONSE, json.dumps({"task_id": insert_task_result}), None
        else:
            return HTTP.BAD_RESPONSE, "", None

    @http_service(['GET'], '/get_task',
                  [CONTEXT.USERID, CONTEXT.CUSTOMERID, CONTEXT.TASKID],
                  {CONTEXT.USERID: int, CONTEXT.CUSTOMERID: int, CONTEXT.TASKID: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor, USER_ROLES.administrator})
    def get_task(self, _header, body, context, _matches, _key):
        # customer_id = context.get(CONTEXT.CUSTOMERID)
        # task_id = context.get(CONTEXT.TASKID)
        raise NotImplementedError

    @http_service(['GET'], '/my_tasks',
                  [CONTEXT.USERID, CONTEXT.CUSTOMERID],
                  {CONTEXT.USERID: int, CONTEXT.CUSTOMERID: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor, USER_ROLES.administrator})
    def get_assigned_tasks(self, _header, body, context, _matches, _key):
        # user_id = context.get(CONTEXT.USERID)
        # customer_id = context.get(CONTEXT.CUSTOMERID)
        raise NotImplementedError

    @http_service(['GET'], '/my_authored_tasks',
                  [CONTEXT.USERID, CONTEXT.CUSTOMERID],
                  {CONTEXT.USERID: int, CONTEXT.CUSTOMERID: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor, USER_ROLES.administrator})
    def get_authored_tasks(self, _header, body, context, _matches, _key):
        # author_id = context.get(CONTEXT.USERID)
        # customer_id = context.get(CONTEXT.CUSTOMERID)
        raise NotImplementedError

    @http_service(['GET'], '/patient_tasks',
                  [CONTEXT.USERID, CONTEXT.CUSTOMERID, CONTEXT.PATIENTLIST],
                  {CONTEXT.USERID: int, CONTEXT.CUSTOMERID: int, CONTEXT.PATIENTLIST: str},
                  {USER_ROLES.provider, USER_ROLES.supervisor, USER_ROLES.administrator})
    def get_patient_tasks(self, _header, body, context, _matches, _key):
        # patient_id = context.get(CONTEXT.PATIENTLIST, None)
        # customer_id = context.get(CONTEXT.CUSTOMERID)
        raise NotImplementedError

    @http_service(['GET'], '/customer_tasks',
                  [CONTEXT.USERID, CONTEXT.CUSTOMERID],
                  {USER_ROLES.provider, USER_ROLES.supervisor, USER_ROLES.administrator})
    def get_customer_tasks(self, _header, body, context, _matches, _key):
        # customer_id = context.get(CONTEXT.CUSTOMERID)
        raise NotImplementedError
