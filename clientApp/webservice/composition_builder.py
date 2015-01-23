# *************************************************************************
# Copyright (c) 2014 - Maven Medical
# ************************
# AUTHOR:
__author__ = 'Yuki Uchino'
# ************************
# DESCRIPTION:   This composition_builder.py file contains the code required to build a FHIR Composition
#                object from an Electronic Health Record that has a web-based API, so that it can be analyzed
#                by the back-end Composition Evaluator.
#
#
# ************************
# ASSUMES:
# ************************
# SIDE EFFECTS:
# ************************
# LAST MODIFIED FOR JIRA ISSUE: MAV-289
# *************************************************************************
from enum import Enum
from lxml import etree
import dateutil.parser
import re
import json
import asyncio
import maven_config as MC
import maven_logging as ML
import utils.web_client.allscripts_http_client as AHC
from utils.web_client.builder import builder
import utils.api.pyfhir.pyfhir_generated as FHIR_API
from utils.enums import ORDER_STATUS


COMP_BUILD_LOG = ML.get_logger('clientApp.webservice.allscripts_server')
CONFIG_API = 'api'
CONFIG_CLIENTEHR = 'client ehr'
CUSTOMERID = 'customer_id'


class Types(Enum):
    Patient = 1
    ClinicalSummary = 2
    CDASummary = 3
    Practitioners = 4
    Practitioner = 5
    Orders = 6


class CompositionBuilder(builder):

    def __init__(self, customer_id, allscripts_api):
        builder.__init__(self)
        self.allscripts_api = allscripts_api
        self.provs = {}
        self.customer_id = customer_id

    @asyncio.coroutine
    def build_providers(self):
        ret = yield from self.allscripts_api.GetProviders()
        for prov in ret:
            self.provs[prov['UserName'].upper()] = self.build_partial_practitioner(prov)

    @builder.build(FHIR_API.Composition)
    @ML.trace(COMP_BUILD_LOG.debug, True)
    def build_composition(self, obj, username, patient, doc_id, doc_datetime, encounter_dx, cda_result):
        obj.author = self.provs[username]
        obj.encounter = FHIR_API.Encounter(identifier=[FHIR_API.Identifier(label="Internal",
                                                                           system="clientEMR",
                                                                           value=doc_id)],
                                           period=FHIR_API.Period(start=doc_datetime),
                                           fhir_class=FHIR_API.Coding(system="http://hl7.org/fhir/encounter-class",
                                                                      code="ambulatory"))
        COMP_BUILD_LOG.debug(json.dumps(FHIR_API.remove_none(json.loads(json.dumps(obj, default=FHIR_API.jdefault))), indent=4))
        COMP_BUILD_LOG.debug(("Finished building Composition ID=%s" % obj.id))
        return obj

    @builder.provide(Types.Patient)
    @ML.coroutine_trace(COMP_BUILD_LOG.debug, True)
    def _patient(self, username, patient, doc_id, doc_datetime, encounter_dx, cda_result):
        ret = yield from self.allscripts_api.GetPatient(username, patient)
        return ret

    @builder.provide(Types.ClinicalSummary)
    @ML.coroutine_trace(COMP_BUILD_LOG.debug, True)
    def _clin_summary(self, username, patient, doc_id, doc_datetime, encounter_dx, cda_result):
        ret = yield from self.allscripts_api.GetClinicalSummary(username, patient, AHC.CLINICAL_SUMMARY.All)
        return ret, encounter_dx

    # @builder.provide(Types.Orders)
    # @ML.coroutine_trace(COMP_BUILD_LOG.debug(), True)
    # def _orders(self, username, patient, doc_id, doc_datetime, encounter_dx):
        # TODO - Should probably move lookback_until to something configurable (default 6 months)
    #    lookback_until = datetime.now()-timedelta(days=180)
    #    ret = yield from self.allscripts_api.GetOrders(username, patient, lookback_date=lookback_until.date().isoformat())
    #    return ret

    @builder.provide(Types.CDASummary)
    def _CDA_summary(self, username, patient, doc_id, doc_datetime, encounter_dx, cda_result):
        if cda_result:
            return cda_result
        else:
            ret = yield from self.allscripts_api.GetPatientCDA(username, patient)
            return ret

    @builder.require(Types.Patient, Types.ClinicalSummary, Types.CDASummary)
    # @ML.coroutine_trace(COMP_BUILD_LOG.debug, True)
    def _build_composition_components(self, composition, patient_result, clin_summary_result, CDA_summary_result):

        # Create the FHIR Composition Object with a Type=LOINC coded version of
        # Virtual Medical Record for Clinical Decision Support ("74028-2") and append to the FHIR Bundle's Entries
        composition.type = FHIR_API.CodeableConcept(coding=[FHIR_API.Coding(system="http://loinc.org",
                                                                            code="74028-2")])

        # Extract the "J-codes" (HCPCS procedure codes) from the CDA
        proc_history_section = self.extract_hcpcs_codes_from_cda(CDA_summary_result)
        if proc_history_section:
            composition.section.append(proc_history_section)

        composition.customer_id = self.customer_id
        composition.subject = self._build_subject(patient_result)
        fhir_dx_section = self._build_conditions(clin_summary_result)
        composition.section.append(fhir_dx_section)

    def _build_subject(self, get_patient_result):
        fhir_patient = self.allscripts_api.build_subject(get_patient_result)
        return fhir_patient

    def _build_conditions(self, clin_summary):
        fhir_dx_section = self.allscripts_api.build_conditions(clin_summary)
        return fhir_dx_section

    def build_partial_practitioner(self, provider_result):
        fhir_practitioner = self.allscripts_api.build_partial_practitioner(provider_result)
        return fhir_practitioner

    def _build_full_practitioner(self, get_provider_result):
        fhir_practitioner = self.allscripts_api.build_full_practitioner(get_provider_result)
        return fhir_practitioner

    def _build_encounter(self):
        pass

    def extract_hcpcs_codes_from_cda(self, cda_result):

        # Make sure the CDA result is there
        if cda_result.get('cdaxml', None) is None:
            return None

        # Make lxml ElementTree object
        cda_etree = etree.fromstring(cda_result['cdaxml']).getroottree()

        # Extract default namespace to add to xml path queries
        cda_root = cda_etree.getroot()
        default_ns = "{{{}}}".format(cda_root.nsmap.get(None, None))

        # Get the list of component sections which contain the patient data
        proc_hist_rows = None
        for sec in cda_etree.findall('.//{}section'.format(default_ns)):
            c = sec.find('{}code'.format(default_ns))
            if c.get('code') == '47519-4':
                proc_hist_rows = sec.find('{}text'.format(default_ns)).find('{}table'.format(default_ns)).find('{}tbody'.format(default_ns)).getchildren()
                break
        # If no procedure history rows detected, return
        if proc_hist_rows is None:
            return None

        # Create a new FHIR Composition Section for holding Orders
        fhir_orders_section = FHIR_API.Section(title="History of Procedures",
                                               code=FHIR_API.CodeableConcept(coding=[FHIR_API.Coding(system="http://loinc.org",
                                                                                                     code="47519-4")]))

        # Regular Expression for pulling HCPCS jcodes (procedure codes) from CDA html
        jcode_regex = re.compile('(?:\(([Jj]\S+)\))')

        # Extract HCPCS code, datetime, order status and generate FHIR Order object
        for row in proc_hist_rows:

            # Extract the jcode
            columns = row.getchildren()
            procname = columns[0].text
            jcode = jcode_regex.findall(procname)
            if len(jcode) == 0:
                # if no code continuing looping through the other rows
                continue

            # Ignore "-" value when parsing dates
            date_collected = None if columns[1].text == "-" else dateutil.parser.parse(columns[1].text)
            # date_completed = None if row[2] == "-" else dateutil.parser.parse(row[2])

            # Order Status
            procstatus = ORDER_STATUS.CM.name if columns[3].text == 'Ordered' else 'UK'

            # Generate the FHIR Procedure/Order Object and add to the Encounter Orders Composition Section
            procedure = FHIR_API.Procedure(name=procname,
                                           date=date_collected,
                                           type=FHIR_API.CodeableConcept(text="Procedure",
                                                                         coding=[FHIR_API.Coding(system="HCPCS",
                                                                                                 code=jcode[0],
                                                                                                 display=procname)]))
            order = FHIR_API.Order(text=procname,
                                   status=procstatus,
                                   detail=[procedure])

            fhir_orders_section.content.append(order)

        return fhir_orders_section


if __name__ == '__main__':
    MC.MavenConfig['allscripts_old_demo'] = {
        AHC.http.CONFIG_BASEURL: 'http://aws-eehr-11.4.1.unitysandbox.com/Unity/UnityService.svc/json',
        AHC.http.CONFIG_OTHERHEADERS: {
            'Content-Type': 'application/json'
        },
        AHC.CONFIG_APPNAME: 'web20',
        AHC.CONFIG_APPUSERNAME: 'webtwozero',
        AHC.CONFIG_APPPASSWORD: 'www!web20!',
    }

    MC.MavenConfig['allscripts_demo'] = {
        AHC.http.CONFIG_BASEURL: 'http://192.237.182.238/Unity/UnityService.svc',
        AHC.http.CONFIG_OTHERHEADERS: {
            'Content-Type': 'application/json'
        },
        AHC.CONFIG_APPNAME: 'MavenPathways.TestApp',
        AHC.CONFIG_APPUSERNAME: 'MavenPathways',
        AHC.CONFIG_APPPASSWORD: 'MavenPathways123!!',
    }

    MC.MavenConfig['scheduler'] = {CONFIG_API: 'allscripts_demo'}

    comp_builder = CompositionBuilder('scheduler')
    loop = asyncio.get_event_loop()
    print(loop.run_until_complete(comp_builder.build_composition("CLIFFHUX", "66561")))
