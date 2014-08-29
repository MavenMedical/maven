# *************************************************************************
# Copyright (c) 2014 - Maven Medical
#
# ************************
# AUTHOR:
__author__ = 'Yuki Uchino'
# ************************
# DESCRIPTION:   This file provides the webservice calls required for Patient Management
#
# ************************
# ASSUMES:
# ************************
# SIDE EFFECTS:
# ************************
# LAST MODIFIED FOR JIRA ISSUE: MAV-303
# *************************************************************************
from utils.enums import USER_ROLES
import json
import asyncio
import utils.database.web_persistence as WP
from utils.streaming.http_svcs_wrapper import http_service, CONTEXT, CONFIG_PERSISTENCE
import utils.streaming.http_responder as HTTP
import maven_config as MC
date = str


class PatientMgmtWebservices():

    def __init__(self, configname):
        config = MC.MavenConfig[configname]
        self.persistence = WP.WebPersistence(config[CONFIG_PERSISTENCE])

    @http_service(['GET'], '/patients(?:(\d+)-(\d+)?)?',
                  [CONTEXT.PROVIDER, CONTEXT.CUSTOMERID],
                  {CONTEXT.PROVIDER: str, CONTEXT.CUSTOMERID: int,
                   CONTEXT.STARTDATE: date, CONTEXT.ENDDATE: date},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_patients(self, _header, _body, context, matches, _key):
        provider = context[CONTEXT.PROVIDER]
        customerid = context[CONTEXT.CUSTOMERID]
        startdate = self.helper.get_date(context, CONTEXT.STARTDATE)
        enddate = self.helper.get_date(context, CONTEXT.ENDDATE)
        desired = {
            WP.Results.patientname: 'name',
            WP.Results.patientid: 'id',
            WP.Results.sex: 'gender',
            WP.Results.birthdate: 'DOB',
            WP.Results.diagnosis: 'diagnosis',
            WP.Results.cost: 'cost',
        }
        results = yield from self.persistence.patient_info(desired, provider, customerid,
                                                           startdate=startdate,
                                                           enddate=enddate,
                                                           limit=self.helper.limit_clause(matches))

        if results:
            asyncio.Task(self.persistence.audit_log(provider, 'patient list web service',
                                                    customerid, rows=1,
                                                    details=list({r['id'] for r in results})))

        return HTTP.OK_RESPONSE, json.dumps(results), None

    @http_service(['GET'], '/patient_details',
                  [CONTEXT.PROVIDER, CONTEXT.KEY, CONTEXT.PATIENTLIST, CONTEXT.CUSTOMERID],
                  {CONTEXT.PROVIDER: str, CONTEXT.KEY: str, CONTEXT.PATIENTLIST: str,
                   CONTEXT.CUSTOMERID: int, CONTEXT.ENCOUNTER: str,
                   CONTEXT.STARTDATE: date, CONTEXT.ENDDATE: date},
                  {USER_ROLES.provider})
    def get_patient_details(self, _header, _body, context, matches, _key):
        """
        This method returns Patient Details which include the data in the header of
        the Encounter Page - i.e. Allergies Problem List, Last Encounter, others.
        """
        provider = context[CONTEXT.PROVIDER]
        patientid = context[CONTEXT.PATIENTLIST]
        customerid = context[CONTEXT.CUSTOMERID]
        startdate = self.helper.get_date(context, CONTEXT.STARTDATE)
        enddate = self.helper.get_date(context, CONTEXT.ENDDATE)
        # if not auth_key == _authorization_key((provider, patient_id), AUTH_LENGTH):
        #   raise HTTP.IncompleteRequest('%s has not been authorized to view patient %s.'
        #                                % (provider, patient_id))

        desired = {
            WP.Results.patientname: 'name',
            WP.Results.patientid: 'id',
            WP.Results.sex: 'gender',
            WP.Results.birthdate: 'DOB',
            WP.Results.diagnosis: 'diagnosis',
            WP.Results.cost: 'cost',
            WP.Results.encounter_list: 'encounters',
            WP.Results.allergies: 'Allergies',
            WP.Results.problems: 'ProblemList',
            WP.Results.admission: 'admitdate',
            WP.Results.lengthofstay: 'LOS',
        }
        results = yield from self.persistence.patient_info(desired, provider, customerid,
                                                           patients=patientid,
                                                           startdate=startdate,
                                                           enddate=enddate,
                                                           limit=self.helper.limit_clause(matches))

        if results:
            asyncio.Task(self.persistence.audit_log(provider, 'patient details web service',
                                                    customerid, patientid, rows=1))

        return HTTP.OK_RESPONSE, json.dumps(results[0]), None
