#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#************************
#AUTHOR:
from utils.api.pyfhir.fhir_datatypes import Period, Identifier, Address, Section

__author__='Yuki Uchino'
#************************
#DESCRIPTION:   This emr_parser.py contains the classes required to parse the incoming
#               SOAP XML messages from Epic, VistA and any other EMRs that Maven integrates
#               with.
#
#
#************************
#ASSUMES:
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-91
#*************************************************************************
import xml.etree.ElementTree as ET
import datetime
import uuid
import dateutil.parser
import json
import utils.api.pyfhir.pyfhir_generated as FHIR_API


class EpicParser():

    def __init__(self):
        #raise NotImplementedError
        pass

    def create_composition(self, xml_root):
        composition = FHIR_API.Composition(type="CostEvaluator")

        if "PatientDemographics" in xml_root.tag:
            composition.subject = self.parse_demographics(xml_root)

        elif "Contact" in xml_root.tag:
            composition.section.append(Section(title="Encounter", content=self.parse_encounter(xml_root)))

        elif "ProblemsResult" in xml_root.tag:
            composition.section.append(
                Section(title="Problem List", content=self.parse_problem_list(xml_prob_list=xml_root)))

        elif "Orders" in xml_root.tag:
            composition.section.append(Section(title="Encounter Orders", content=self.parse_orders(xml_root)))

    def parse_demographics(self, xml_demog):
        """
        :param xml_demog: XML chunk containing demographic information from EPIC
        """

        demog_root = ET.fromstring(xml_demog)
        try:
            #Parse important data elements out of incoming XML using Python's ElementTree object
            self.zipcode = demog_root.findall(".//Zip")[0].text
            self.firstName = demog_root.findall(".//FirstName")[0].text
            self.lastName = demog_root.findall(".//LastName")[0].text
            self.patientId = demog_root.findall(".//NationalIdentifier")[0].text
            self.gender = demog_root.findall(".//Gender")[0].text
            self.birthDateText = demog_root.findall(".//DateOfBirth")[0].text.split("T")[0]
            self.birthDate = datetime.datetime(int(self.birthDateText.split("-")[0]), int(self.birthDateText.split("-")[1]), int(self.birthDateText.split("-")[2]))
            self.birthMonth = self.birthDate.strftime('%m')

        except:
            raise Exception('Error parsing XML demographics')

        try:
            #Create Patient from the API using data from above
            pat = FHIR_API.Patient()
            pat.add_name(given=[self.firstName], family=[self.lastName])
            pat.add_maven_identifier(value=uuid.uuid1())
            pat.identifier.append(Identifier(system='NationalIdentifier', value=self.patientId))
            pat.address.append(Address(zip=self.zipcode))
            pat.birthDate = self.birthDate
            pat.gender = self.gender

        except:
            raise Exception('Error constructing patient from API and data')

        return pat

    def parse_encounter(self, xml_contact):
        """
        :param xml_contact: XML Encounter Contact from EPIC
        """

        pat_encounter = FHIR_API.Encounter()

        try:
            root = ET.fromstring(xml_contact)
            contactDateTime = dateutil.parser.parse(root.findall(".//DateTime")[0].text)
            pat_encounter.period = Period(start=contactDateTime)
            department = root.findall(".//DepartmentName")[0].text
            pat_encounter.department = FHIR_API.Location(name=department)
            depids = root.findall(".//DepartmentIDs/IDType")
            for dp in depids:
                if "internal" in dp.findall(".//Type")[0].text.lower():
                    id = dp.findall("ID")[0].text
                    pat_encounter.department.identifier.append(Identifier(label="Internal", system="clientEMR", value=id))
            csns = root.findall(".//IDs/IDType")
            for csn in csns:
                if "serial" in dp.findall(".//Type")[0].text.lower():
                    id = dp.findall("ID")[0].text
                    pat_encounter.identifier.append(Identifier(system="clientEMR", label="serial", value=id))
            pat_encounter.type = root.findall("./Type")[0].text
            patclass = root.findall("./PatientClass")[0].text
            if patclass == "E":
                pat_encounter.encounter_class = "Emergency"
            elif patclass == "I":
                pat_encounter.encounter_class ="Inpatient"
            else:
                pat_encounter.encounter_class ="Ambulatory"

        except:
            raise Exception("Error parsing Encounter information")

        return pat_encounter

    def parse_problem_list(self, xml_prob_list, pat, pat_enc):

        problem_list = []
        probl_root = ET.fromstring(xml_prob_list)
        try:
            for prb in probl_root.findall(".//Problems/Problem"):
                condition = self.parse_medical_problem(prb, pat, pat_enc)
                problem_list.append(condition)

        except:
            raise Exception('Error parsing problem list')

        return problem_list

    def parse_orders(self, str):
        encounter_orders = []
        root = ET.fromstring(str)
        for ord in root.findall(".//Order"):
            ord_name = ord.findall(".//Name")[0].text
            ord_code = ord.findall(".//ProcedureCode")[0].text
            ord_code_type = ord.findall(".//CodeType")[0].text
            ord_type = ord.findall(".//Type")[0].text

            procedure = FHIR_API.Procedure()
            procedure.type = ord_type
            procedure.name = ord_name
            procedure.identifier.append(Identifier(system="clientEMR", label="name", value=ord_name))
            procedure.identifier.append(Identifier(system="clientEMR", label=ord_code_type, value=ord_code))

            encounter_orders.append(FHIR_API.Order(detail=[procedure], text=ord_name))

        return encounter_orders

    def parse_medical_problem(self, xmlIn, pat, enc):

        prob = FHIR_API.Condition(encounter=enc.id, subject=pat.id)
        root = xmlIn
        dxid = root.findall(".//DiagnosisIDs/IDType")
        # Loop through the dx ID's in this list until the internal one. Use that to instantiate a new DX Object
        for idtp in dxid:
            if "internal" in idtp.findall(".//Type")[0].text.lower():
                prob.identifier.append(
                    Identifier(label="Internal", system="clientEMR", value=idtp.findall(".//ID")[0].text))
                #self.diagnosis = cliDiagnosis.cliDiagnosis(idtp.findall(".//ID")[0].text, config)
                break

        prob.date_asserted = dateutil.parser.parse(root.findall(".//NotedDate")[0].text)

        chron=root.findall(".//IsChronic")[0].text
        if chron is not None and "true" in chron.lower():
            prob.isChronic = True

        hosp = root.findall(".//IsHospitalProblem")[0].text
        if hosp is not None and "true" in hosp.lower():
            prob.isHospital = True

        poa = root.findall(".//IsPresentOnAdmission")[0].text
        if poa is not None and "true" in poa.lower():
            prob.isPOA = True

        princ = root.findall(".//IsPrincipal")[0].text
        if princ is not None and "true" in princ.lower():
            prob.isPrincipal = True

        return prob


class VistaParser():

    def __init__(self):
        self.terminologies = ['icd', 'icd9', 'icd10', 'icd-9', 'icd-10', 'cpt', 'cpt4', 'cpt3', 'maven']

    def create_composition(self, xml_enc):
        ###
        # Create the FHIR Bundle Object for bundling the FHIR Composition and it's Resources up.
        fhir_bundle = FHIR_API.Bundle(title="Vista EMR Message")

        ##
        # Create the FHIR Composition Object with a Type=LOINC coded version of
        # Virtual Medical Record for Clinical Decision Support ("74028-2") and append to the FHIR Bundle's Entries
        composition = FHIR_API.Composition(type=FHIR_API.CodeableConcept())
        composition.type.coding.append(FHIR_API.Coding(system="http://loinc.org", code="74028-2"))

        fhir_bundle.entry.append(composition)

        #TODO - Hardcoded customer id
        composition.customer_id = 1
        composition.encounter = FHIR_API.Encounter(customer_id=composition.customer_id)
        composition.author = FHIR_API.Practitioner(customer_id=composition.customer_id)

        enc_root = ET.fromstring(xml_enc)
        for child in enc_root:
            if "EncID" in child.tag:
                composition.encounter.identifier.append(FHIR_API.Identifier(system="clientEMR",
                                                                            label="Internal",
                                                                            value=child.text))

            elif "ProvID" in child.tag:
                composition.author.identifier.append(FHIR_API.Identifier(system="clientEMR",
                                                                         label="Internal",
                                                                         value=child.text))

            elif "PatientDemographics" in child.tag:
                self.parse_demographics(child, composition)

            elif "Orders" in child.tag:
                self.parse_encounter_orders(child, composition)

            elif "ActiveProblems" in child.tag:
                self.parse_encounter_diagnoses(child, composition)

        return composition

    def parse_demographics(self, xml_root, composition):
        try:
            composition.subject = FHIR_API.Patient(customer_id=composition.customer_id)

            #Parse important data elements out of incoming XML using Python's ElementTree object
            city = xml_root.findall(".//City")[0].text
            country = xml_root.findall(".//Country")[0].text
            county = xml_root.findall(".//County")[0].text
            state = xml_root.findall(".//State")[0].text
            street = xml_root.findall(".//Street")[0].text
            zipcode = xml_root.findall(".//Zip")[0].text
            birthDate = dateutil.parser.parse(xml_root.findall(".//DateOfBirth")[0].text)
            gender = xml_root.findall(".//Gender")[0].text
            maritalStatus = xml_root.findall(".//MaritalStatus")[0].text
            firstName = xml_root.findall(".//FirstName")[0].text
            lastName = xml_root.findall(".//LastName")[0].text
            patientSSN = xml_root.findall(".//NationalIdentifier")[0].text

            patientID = None
            if (len(xml_root.findall(".//PatientID")) > 0):
                patientID = xml_root.findall(".//PatientID")[0].text

            patientIDType = None
            if (len(xml_root.findall(".//PatientIDType")) > 0):
                patientIDType = xml_root.findall(".//PatientIDType")[0].text

        except:
            raise Exception('Error parsing XML demographics')

        try:
            composition.subject.add_name(given=[firstName], family=[lastName])
            composition.subject.birthDate = birthDate
            composition.subject.gender = gender
            composition.subject.maritalStatus = maritalStatus
            composition.subject.identifier.append(FHIR_API.Identifier(system='NationalIdentifier',
                                                                      value=patientSSN))

            if patientID is not None and patientIDType is not None:
                composition.subject.identifier.append(FHIR_API.Identifier(system='clientEMR',
                                                                          label=patientIDType,
                                                                          value=patientID))
            elif patientID is not None:
                composition.subject.identifier.append(FHIR_API.Identifier(system='clientEMR',
                                                                          label="Internal",
                                                                          value=patientID))

            composition.subject.address.append(FHIR_API.Address(zip=zipcode, city=city,
                                                                country=country,
                                                                state=state, line=[street]))

        except:
            raise Exception('Error constructing FHIR patient from VistA XML data')

    def parse_encounter_orders(self, xml_root, composition):
        try:
            encounter_orders_section = FHIR_API.Section(title="Encounter Orders")
            fhir_enc_orders_code = FHIR_API.CodeableConcept()
            fhir_enc_orders_code.coding.append(FHIR_API.Coding(system="http://loinc.org", code="46209-3"))
            encounter_orders_section.code = fhir_enc_orders_code

            encounter_orders = []
            for enc_ord in xml_root.findall(".//Order"):
                ord_id = enc_ord.findall(".//ID")[0].text
                ord_name = enc_ord.findall(".//Name")[0].text
                ord_code = enc_ord.findall(".//ProcedureCode")[0].text
                ord_code_type = enc_ord.findall(".//CodeType")[0].text
                if ord_code_type is None:
                    ord_code_type = "Internal"
                ord_type = enc_ord.findall(".//Type")[0].text
                datetime_raw = enc_ord.findall(".//OrderingDate")[0].text.replace('@', ' ')
                ord_datetime = dateutil.parser.parse(datetime_raw)

                if ord_code_type.lower() in self.terminologies:
                    if ord_type == "PROC":
                        fhir_identifier = FHIR_API.Identifier(system="clientEMR", value=ord_id, label="Internal")
                        fhir_codeableconcept = FHIR_API.CodeableConcept()
                        fhir_codeableconcept.coding.append(FHIR_API.Coding(system=ord_code_type, code=ord_code))

                        procedure = FHIR_API.Procedure(date=ord_datetime,
                                                       text=ord_name)
                        procedure.identifier.append(fhir_identifier)
                        procedure.type = fhir_codeableconcept

                        encounter_orders.append(FHIR_API.Order(detail=[procedure], text=ord_name))

                    elif ord_type == "MED":
                        pass

                    elif ord_type == 'IMAGING':
                        pass

                else:
                    fhir_identifier = FHIR_API.Identifier(system="clientEMR", value=ord_code, label=ord_code_type)
                    procedure = FHIR_API.Procedure(date=ord_datetime, text=ord_name)
                    procedure.identifier.append(fhir_identifier)

                    encounter_orders.append(FHIR_API.Order(detail=[procedure], text=ord_name))


            encounter_orders_section.content = encounter_orders
            composition.section.append(encounter_orders_section)

        except:
            raise Exception("Error parsing Vista Encounter Orders")

    def parse_encounter_diagnoses(self, xml_root, composition):
        section_code = FHIR_API.CodeableConcept()
        section_code.coding.append(FHIR_API.Coding(system="http://loinc.org", code="11450-4"))
        fhir_encounter_dx_section = FHIR_API.Section(title="Encounter Dx", code=section_code)

        encounter_dxs = []
        try:
            for prb in xml_root.findall(".//Problems/Problem"):
                condition = self._parse_condition(prb)
                encounter_dxs.append(condition)


            fhir_encounter_dx_section.content = encounter_dxs
            composition.section.append(fhir_encounter_dx_section)

        except:
            raise Exception('Error parsing problem list')

    def _parse_condition(self, xml_root):
        prob = FHIR_API.Condition()
        dx_IDs = xml_root.findall(".//DiagnosisIDs/IDType")

        for id in dx_IDs:
            dx_code_type = id.findall(".//Type")[0].text.lower()
            dx_code_value = id.findall(".//ID")[0].text

            if "internal" in dx_code_type:
                prob.identifier.append(FHIR_API.Identifier(label="Internal", system="clientEMR", value=dx_code_value))

            elif dx_code_type in self.terminologies:
                if prob.code is None:
                    prob.code = FHIR_API.CodeableConcept()
                prob.code.coding.append(FHIR_API.Coding(system=dx_code_type, code=dx_code_value))

        prob.dateAsserted = dateutil.parser.parse(xml_root.findall(".//NotedDate")[0].text)

        chron = xml_root.findall(".//IsChronic")[0].text
        if chron is not None and "true" in chron.lower():
            prob.stage = "Chronic"

        hosp = xml_root.findall(".//IsHospitalProblem")[0].text
        if hosp is not None and "true" in hosp.lower():
            prob.category = "Hospital Problem"

        poa = xml_root.findall(".//IsPresentOnAdmission")[0].text
        if poa is not None and "true" in poa.lower():
            prob.presentOnArrival = True

        princ = xml_root.findall(".//IsPrincipal")[0].text
        if princ is not None and "true" in princ.lower():
            prob.isPrincipal = True

        return prob

def delete_none(d):
    for key, value in d.items():
        if value is None:
            del d[key]
        elif isinstance(value, dict):
            delete_none(value)
    return d

def _get_composition(file_path):
    with open(file_path) as f:
        r = f.read()
        comp = VistaParser().create_composition(r)
        return comp


if __name__ == '__main__':
    file = open('/home/devel/yukidev/maven/clientApp/fake_data/dave_test_encounter.xml')
    r = file.read()
    file.close()
    VistaParser().create_composition(r)
