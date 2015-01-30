# *************************************************************************
# Copyright (c) 2014 - Maven Medical
#
# ************************
# AUTHOR:
__author__ = 'Yuki Uchino'
# ************************
# DESCRIPTION:   This file provides the webservice calls required for Maven Transparent functionality
#
# ************************
# ASSUMES:
# ************************
# SIDE EFFECTS:
# ************************
# LAST MODIFIED FOR JIRA ISSUE: MAV-303
# *************************************************************************
# from utils.streaming.webservices_core import *
from utils.streaming.http_svcs_wrapper import CONFIG_PERSISTENCE, http_service, CONTEXT
from utils.enums import USER_ROLES
from collections import defaultdict
import maven_config as MC
from datetime import date
import app.database.web_persistence as WP
import utils.streaming.http_responder as HTTP
import json
import asyncio


class TransparentWebservices():

    def __init__(self, configname, _rpc):
        config = MC.MavenConfig[configname]
        self.persistence = WP.WebPersistence(config[CONFIG_PERSISTENCE])
        self.persistence.schedule()

    @http_service(['GET'], '/total_spend',
                  [CONTEXT.PROVIDER, CONTEXT.KEY, CONTEXT.CUSTOMERID],
                  {CONTEXT.PROVIDER: str, CONTEXT.KEY: list, CONTEXT.PATIENTLIST: list,
                   CONTEXT.ENCOUNTER: str, CONTEXT.CUSTOMERID: int,
                   CONTEXT.STARTDATE: date, CONTEXT.ENDDATE: date},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_total_spend(self, _header, _body, context, _matches, _key):
        provider = context[CONTEXT.PROVIDER]
        patient_ids = context.get(CONTEXT.PATIENTLIST, None)
        customer = context[CONTEXT.CUSTOMERID]
        encounter = context.get(CONTEXT.ENCOUNTER, None)
        startdate = self.helper.get_date(context, CONTEXT.STARTDATE)
        enddate = self.helper.get_date(context, CONTEXT.ENDDATE)
        # auth_keys = dict(zip(patient_ids, context[CONTEXT.KEY]))

        desired = {
            WP.Results.spending: 'spending',
            WP.Results.savings: 'savings',
        }

        if patient_ids or encounter:
            provider = None

        results = yield from self.persistence.total_spend(desired, customer,
                                                          provider=provider,
                                                          startdate=startdate,
                                                          enddate=enddate,
                                                          patients=patient_ids,
                                                          encounter=encounter)

        return HTTP.OK_RESPONSE, json.dumps(results), None

    @http_service(['GET'], '/spending',
                  [CONTEXT.PROVIDER, CONTEXT.KEY, CONTEXT.CUSTOMERID],
                  {CONTEXT.PROVIDER: str, CONTEXT.KEY: list, CONTEXT.PATIENTLIST: list,
                   CONTEXT.CUSTOMERID: int, CONTEXT.ENCOUNTER: str,
                   CONTEXT.STARTDATE: date, CONTEXT.ENDDATE: date},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_daily_spending(self, _header, _body, context, _matches, _key):
        provider = context[CONTEXT.PROVIDER]
        customer = context[CONTEXT.CUSTOMERID]
        ret = defaultdict(lambda: defaultdict(int))
        encounter = context.get(CONTEXT.ENCOUNTER, None)
        patient_ids = context.get(CONTEXT.PATIENTLIST, None)
        startdate = self.helper.get_date(context, CONTEXT.STARTDATE)
        enddate = self.helper.get_date(context, CONTEXT.ENDDATE)
        # auth_keys = dict(zip(patient_ids, context[CONTEXT.KEY]))

        desired = {x: x for x in [WP.Results.date, WP.Results.ordertype, WP.Results.spending]}
        # if AK.check_authorization((provider, patient_id), auth_keys[patient_id], AUTH_LENGTH):
        results = yield from self.persistence.daily_spend(desired, provider, customer,
                                                          startdate=startdate,
                                                          enddate=enddate,
                                                          patients=patient_ids,
                                                          encounter=encounter)

        for row in results:
            if WP.Results.spending is int:
                ret[row[WP.Results.date]][row[WP.Results.ordertype]] += row[WP.Results.spending]
            else:
                ret[row[WP.Results.date]][row[WP.Results.ordertype]] = row[WP.Results.spending]

        return HTTP.OK_RESPONSE, json.dumps(ret), None

    @http_service(['GET'], '/orders(?:(\d+)-(\d+)?)?',
                  [CONTEXT.USER, CONTEXT.CUSTOMERID],
                  {CONTEXT.USER: str, CONTEXT.PATIENTLIST: list, CONTEXT.CUSTOMERID: int,
                   CONTEXT.ENCOUNTER: str, CONTEXT.ORDERTYPE: str,
                   CONTEXT.STARTDATE: date, CONTEXT.ENDDATE: date},
                  {USER_ROLES.provider, USER_ROLES.supervisor})
    def get_orders(self, _header, _body, context, matches, _key):
        ordertype = context.get(CONTEXT.ORDERTYPE, None)
        if ordertype:
            ordertypes = [ordertype]
        else:
            ordertypes = []
        patients = context.get(CONTEXT.PATIENTLIST, None)

        encounter = context.get(CONTEXT.ENCOUNTER, None)
        customer = context[CONTEXT.CUSTOMERID]
        startdate = self.helper.get_date(context, CONTEXT.STARTDATE)
        enddate = self.helper.get_date(context, CONTEXT.ENDDATE)
        limit = self.helper.limit_clause(matches)
        if not limit:
            limit = 'LIMIT 10'
        # auth_keys = dict(zip(patient_ids, context[CONTEXT.KEY]))

        desired = {
            WP.Results.ordername: 'name',
            WP.Results.datetime: 'date',
            WP.Results.active: 'result',
            WP.Results.cost: 'cost',
            WP.Results.ordertype: CONTEXT.ORDERTYPE,
            WP.Results.orderid: 'id',
        }

        results = yield from self.persistence.orders(desired, customer,
                                                     encounter=encounter,
                                                     patientid=patients,
                                                     startdate=startdate,
                                                     enddate=enddate,
                                                     ordertypes=ordertypes, limit=limit)

        if results and patients and len(patients) == 1:
            user = context.get(CONTEXT.USER)
            asyncio.Task(self.persistence.audit_log(user, 'get orders',
                                                    customer, patients[0], rows=len(results)))

        return HTTP.OK_RESPONSE, json.dumps(results), None

    @http_service(['GET'], '/hist_spending',
                  [CONTEXT.PROVIDER, CONTEXT.CUSTOMERID],
                  {CONTEXT.PROVIDER: str, CONTEXT.PATIENTLIST: list, CONTEXT.CUSTOMERID: int},
                  {USER_ROLES.supervisor, USER_ROLES.provider})
    def get_hist_spend(self, _header, _body, context, matches, _key):
        desired = {
            WP.Results.patientid: "patientid",
            WP.Results.patientname: "patientname",
            WP.Results.encounterid: "encounterid",
            WP.Results.spending: "spending",
            WP.Results.startdate: "admission",
            WP.Results.enddate: "discharge",
            WP.Results.diagnosis: "diagnosis",
        }
        results = yield from self.persistence.per_encounter(desired,
                                                            context.get(CONTEXT.PROVIDER),
                                                            context.get(CONTEXT.CUSTOMERID),
                                                            patients=context.get(CONTEXT.PATIENTLIST, None))

        return HTTP.OK_RESPONSE, json.dumps(results), None


def run():
    from utils.database.database import AsyncConnectionPool
    import utils.streaming.webservices_core as WC
    from app.backend.webservices.authentication import AuthenticationWebservices
    from app.backend.webservices.patient_mgmt import PatientMgmtWebservices
    from app.backend.webservices.user_mgmt import UserMgmtWebservices
    from app.backend.webservices.search import SearchWebservices
    import utils.streaming.stream_processor as SP

    MC.MavenConfig = \
        {
            "httpserver":
                {
                    SP.CONFIG_HOST: 'localhost',
                    SP.CONFIG_PORT: 8087,
                    CONFIG_PERSISTENCE: "persistence layer",
                },
            'persistence layer': {WP.CONFIG_DATABASE: 'webservices conn pool', },
            'webservices conn pool':
                {
                    AsyncConnectionPool.CONFIG_CONNECTION_STRING: MC.dbconnection,
                    AsyncConnectionPool.CONFIG_MIN_CONNECTIONS: 4,
                    AsyncConnectionPool.CONFIG_MAX_CONNECTIONS: 8
                }
        }

    core_scvs = WC.WebserviceCore('httpserver')
    for c in [AuthenticationWebservices, PatientMgmtWebservices,
              UserMgmtWebservices, SearchWebservices,
              TransparentWebservices]:
        core_scvs.register_services(c('httpserver'))

    event_loop = asyncio.get_event_loop()
    core_scvs.schedule(event_loop)
    event_loop.run_forever()

if __name__ == '__main__':
    run()
