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
import dateutil.parser
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
CUSTOMERID = 'customer_id'


class Types(Enum):
    Patient = 1
    ClinicalSummary = 2
    Practitioners = 3
    Practitioner = 4


class CompositionBuilder(builder):

    def __init__(self, configname):
        builder.__init__(self)
        self.config = MC.MavenConfig[configname]
        apiname = self.config[CONFIG_API]
        self.allscripts_api = AHC.allscripts_api(apiname)
        self.provs = {}
        self.customer_id = MC.MavenConfig[CUSTOMERID]

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

    @builder.require(Types.Patient, Types.ClinicalSummary)
    @ML.coroutine_trace(COMP_BUILD_LOG.debug, True)
    def _build_composition_components(self, composition, patient_result, clin_summary_result):

        # Create the FHIR Composition Object with a Type=LOINC coded version of
        # Virtual Medical Record for Clinical Decision Support ("74028-2") and append to the FHIR Bundle's Entries
        composition.type = FHIR_API.CodeableConcept(coding=[FHIR_API.Coding(system="http://loinc.org",
                                                                            code="74028-2")])
        composition.customer_id = self.customer_id
        composition.subject = self._build_subject(patient_result)
        fhir_dx_section = self._build_conditions(clin_summary_result)
        composition.section.append(fhir_dx_section)

    def _build_subject(self, get_patient_result):

        # Extract the demographic information
        firstname = get_patient_result['Firstname']
        lastname = get_patient_result['LastName']
        birthDate = dateutil.parser.parse(get_patient_result['dateofbirth'])
        street = get_patient_result['Addressline1']
        street2 = get_patient_result['AddressLine2']
        city = get_patient_result['City']
        state = get_patient_result['State']
        zip = get_patient_result['ZipCode']
        sex = get_patient_result['gender']
        maritalStatus = get_patient_result['MaritalStatus']

        # Create Medical Record Number (MRN) FHIR Identifier
        fhir_MRN_identifier = FHIR_API.Identifier(label="MRN",
                                                  system="clientEMR",
                                                  value=get_patient_result['mrn'])

        # Create SSN FHIR Identifier
        fhir_SSN_identifier = FHIR_API.Identifier(label="NationalIdentifier",
                                                  system="clientEMR",
                                                  value=get_patient_result['ssn'])

        # Create clientEMR Internal Identifier
        fhir_EMR_identifier = FHIR_API.Identifier(system="clientEMR",
                                                  label="Internal",
                                                  value=get_patient_result['ID'])

        fhir_patient = FHIR_API.Patient(identifier=[fhir_EMR_identifier, fhir_MRN_identifier, fhir_SSN_identifier],
                                        birthDate=birthDate,
                                        name=[FHIR_API.HumanName(given=[firstname],
                                                                 family=[lastname])],
                                        gender=sex,
                                        maritalStatus=maritalStatus,
                                        address=[FHIR_API.Address(line=[street, street2],
                                                                  city=city,
                                                                  state=state,
                                                                  zip=zip)])
        return fhir_patient

    def _build_conditions(self, clin_summary):
        fhir_dx_section = FHIR_API.Section(title="Encounter Dx",
                                           code=FHIR_API.CodeableConcept(coding=[FHIR_API.Coding(system="http://loinc.org",
                                                                                                 code="11450-4")]))
        for problem in [detail for detail in clin_summary if detail['section'] == "problems"]:

            # Instantiate the FHIR Condition
            fhir_condition = FHIR_API.Condition()

            # Figure out whether it's a Problem List/Encounter Dx, or Past Medical History
            # Parsing this string 'Promoted: Yes'
            if len(problem['detail']) > 0 and problem['detail'].replace(" ", "").split(":")[1] == "Yes":
                fhir_condition.category = "Encounter"
            else:
                fhir_condition.category = "History"

            # Get the date the condition was asserted
            fhir_condition.dateAsserted = dateutil.parser.parse(problem['displaydate']) or None

            # Create the FHIR CodeableConcept that contains the Display Name and terminology (ICD-9) coding
            code, system = problem['entrycode'].split("|")

            if system in ["ICD-9", "ICD9"]:
                fhir_condition.code = FHIR_API.CodeableConcept(coding=[FHIR_API.Coding(system="ICD-9",
                                                                                       code=code,
                                                                                       display=problem['description'])])
            else:
                fhir_condition.code = FHIR_API.CodeableConcept(coding=[FHIR_API.Coding(display=problem['description'])])
                COMP_BUILD_LOG.debug("Diagnosis Terminology (ICD-9/10, SNOMED CT) not provided for %s" % problem)

            fhir_dx_section.content.append(fhir_condition)

        return fhir_dx_section

    def build_partial_practitioner(self, provider_result):

        # Extract the demographic information
        firstname = provider_result['FirstName']
        lastname = provider_result['LastName']

        specialty = provider_result['PrimSpecialty']

        # Create clientEMR Internal Identifier
        fhir_identifiers = [FHIR_API.Identifier(system="clientEMR",
                                                label="Internal",
                                                value=provider_result['EntryCode']),
                            FHIR_API.Identifier(system="clientEMR",
                                                label="Username",
                                                value=provider_result['UserName'])]

        # Instantiate and build the FHIR Practitioner from the data
        fhir_practitioner = FHIR_API.Practitioner(identifier=fhir_identifiers,
                                                  name=FHIR_API.HumanName(given=[firstname],
                                                                          family=[lastname]),
                                                  specialty=[specialty])
        return fhir_practitioner

    def _build_full_practitioner(self, get_provider_result):

        # Extract the demographic information
        firstname = get_provider_result['FirstName']
        lastname = get_provider_result['LastName']
        suffix = get_provider_result['SuffixName']
        specialty = get_provider_result['Specialty']
        street1 = get_provider_result['AddressLine1'].strip()
        street2 = get_provider_result['AddressLine2']
        city = get_provider_result['City']
        state = get_provider_result['State'].strip()
        zipcode = get_provider_result['ZipCode']

        contactInfo = [FHIR_API.Contact(system="Phone",
                                        value=get_provider_result['Phone'].strip()),
                       FHIR_API.Contact(system="Fax",
                                        value=get_provider_result['Fax'].strip())]

        # Create clientEMR Internal Identifier
        fhir_identifiers = [FHIR_API.Identifier(system="clientEMR",
                                                label="Internal",
                                                value=get_provider_result['EntryCode']),
                            FHIR_API.Identifier(system="clientEMR",
                                                label="NPI",
                                                value=get_provider_result['NPI'])]

        # Instantiate and build the FHIR Practitioner from the data
        fhir_practitioner = FHIR_API.Practitioner(identifier=fhir_identifiers,
                                                  name=FHIR_API.HumanName(given=[firstname],
                                                                          family=[lastname],
                                                                          suffix=[suffix]),
                                                  specialty=[specialty],
                                                  telecom=contactInfo,
                                                  address=[FHIR_API.Address(line=[street1, street2],
                                                                            city=city,
                                                                            state=state,
                                                                            zip=zipcode)])
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
