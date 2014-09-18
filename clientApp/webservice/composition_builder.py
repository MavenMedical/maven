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
import json
import asyncio
import maven_config as MC
import maven_logging as ML
import utils.web_client.allscripts_http_client as AHC
from utils.web_client.builder import builder
import utils.api.pyfhir.pyfhir_generated as FHIR_API


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


class CompositionBuilder(builder):

    def __init__(self, allscripts_api):
        builder.__init__(self)
        self.allscripts_api = allscripts_api
        self.provs = {}
        self.customer_id = MC.MavenConfig[CUSTOMERID]

    @asyncio.coroutine
    def build_providers(self):
        ret = yield from self.allscripts_api.GetProviders(username=self.config.get(AHC.CONFIG_APPUSERNAME))
        for prov in ret:
            self.provs[prov['UserName']] = self.build_partial_practitioner(prov)

    @builder.build(FHIR_API.Composition)
    @ML.trace(COMP_BUILD_LOG.debug, True)
    def build_composition(self, obj, username, patient, doc_id):
        obj.author = self.provs[username]
        obj.encounter = FHIR_API.Encounter(identifier=[FHIR_API.Identifier(label="Internal",
                                                                           system="clientEMR",
                                                                           value=doc_id)])
        COMP_BUILD_LOG.debug(json.dumps(FHIR_API.remove_none(json.loads(json.dumps(obj, default=FHIR_API.jdefault))), indent=4))
        COMP_BUILD_LOG.debug(("Finished building Composition ID=%s" % obj.id))
        return obj

    @builder.provide(Types.Patient)
    @ML.coroutine_trace(COMP_BUILD_LOG.debug, True)
    def _patient(self, username, patient, doc_id):
        ret = yield from self.allscripts_api.GetPatient(username, patient)
        return ret

    @builder.provide(Types.ClinicalSummary)
    @ML.coroutine_trace(COMP_BUILD_LOG.debug, True)
    def _clin_summary(self, username, patient, doc_id):
        ret = yield from self.allscripts_api.GetClinicalSummary(username, patient, AHC.CLINICAL_SUMMARY.All)
        return ret

    @builder.provide(Types.CDASummary)
    @ML.coroutine_trace(COMP_BUILD_LOG.debug, True)
    def _CDA_summary(self, username, patient, doc_id):
        ret = yield from self.allscripts_api.GetPatientCDA(username, patient)
        return ret

    @builder.require(Types.Patient, Types.ClinicalSummary, Types.CDASummary)
    @ML.coroutine_trace(COMP_BUILD_LOG.debug, True)
    def _build_composition_components(self, composition, patient_result, clin_summary_result, CDA_summary_result):

        # Create the FHIR Composition Object with a Type=LOINC coded version of
        # Virtual Medical Record for Clinical Decision Support ("74028-2") and append to the FHIR Bundle's Entries
        composition.type = FHIR_API.CodeableConcept(coding=[FHIR_API.Coding(system="http://loinc.org",
                                                                            code="74028-2")])
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
