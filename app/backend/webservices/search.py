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
import json
from utils.streaming.http_svcs_wrapper import http_service, CONTEXT, CONFIG_PERSISTENCE
from utils.enums import USER_ROLES
import utils.database.web_persistence as WP
import utils.streaming.http_responder as HTTP
import maven_config as MC


class SearchWebservices():

    def __init__(self, configname, _rpc):
        config = MC.MavenConfig[configname]
        self.persistence = WP.WebPersistence(config[CONFIG_PERSISTENCE])

    @http_service(['GET'], '/autocomplete_patient',
                  [CONTEXT.PATIENTNAME, CONTEXT.PROVIDER, CONTEXT.CUSTOMERID],
                  {CONTEXT.PATIENTNAME: str, CONTEXT.PROVIDER: str,
                   CONTEXT.CUSTOMERID: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_autocomplete_patient(self, _header, _body, context, matches, _key):
        provider = context[CONTEXT.PROVIDER]
        patientname = context[CONTEXT.PATIENTNAME]
        customerid = context[CONTEXT.CUSTOMERID]
        desired = {
            WP.Results.patientname: 'label',
            WP.Results.patientid: 'value',
        }
        results = yield from self.persistence.patient_info(desired, provider, customerid,
                                                           limit=self.helper.limit_clause(matches),
                                                           patient_name=patientname)

        return HTTP.OK_RESPONSE, json.dumps(results), None

        # return HTTP.OK_RESPONSE, json.dumps(['Maven']), None

    @http_service(['GET'], '/autocomplete_diagnosis',
                  [CONTEXT.DIAGNOSIS, CONTEXT.PROVIDER, CONTEXT.CUSTOMERID],
                  {CONTEXT.DIAGNOSIS: str, CONTEXT.PROVIDER: str,
                   CONTEXT.CUSTOMERID: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_autocomplete_diagnosis(self, _header, _body, context, matches, _key):
        # context = self.helper.restrict_context(qs,
        #                                        FrontendWebService.diagnosis_required_contexts,
        #                                        FrontendWebService.diagnosis_available_contexts)
        # provider = context[CONTEXT.PROVIDER]
        # diagnosis = context[CONTEXT.DIAGNOSIS]
        # customerid = context[CONTEXT.CUSTOMERID]
        # desired = {
        #    WP.Results.diagnosis: 'diagnosis',
        # }
        """ NOT READY YET:
        results = yield from self.persistence.diagnosis_info(desired, provider,
                                                                       customerid,
                                                                       diagnosis=diagnosis,
                                                                       limit=self.helper.limit_clause(matches),)
        """
        # return HTTP.OK_RESPONSE, json.dumps(results), None
        return HTTP.OK_RESPONSE, json.dumps(['Alzheimer\'s', 'Diabetes']), None

    @http_service(['GET'], '/search/groups',
                  [CONTEXT.PROVIDER, CONTEXT.CUSTOMERID],
                  {CONTEXT.PROVIDER: str, CONTEXT.CUSTOMERID: int},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_customer_groups(self, _header, _body, context, matches, _key):

        customer_id = context[CONTEXT.CUSTOMERID]
        groups = yield from self.persistence.get_groups(customer_id)
        if groups or isinstance(groups, list):
            return HTTP.OK_RESPONSE, json.dumps(groups), None
        else:
            return HTTP.BAD_RESPONSE, json.dumps('FALSE'), None
