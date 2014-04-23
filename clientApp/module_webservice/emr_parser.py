#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#************************
#AUTHOR:
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

import utils.api.api as api


class EpicParser():

    def __init__(self):
        #raise NotImplementedError
        pass

    def create_composition(self, xml_root):
        composition = api.Composition(type="CostEvaluator")

        if "PatientDemographics" in xml_root.tag:
            composition.subject = self.parse_demographics(xml_root)

        elif "Contact" in xml_root.tag:
            composition.section.append(api.Section(title="Encounter", content=self.parse_encounter(xml_root)))

        elif "ProblemsResult" in xml_root.tag:
            composition.section.append(api.Section(title="Problem List", content=self.parse_problem_list(xml_prob_list=xml_root)))

        elif "Orders" in xml_root.tag:
            composition.section.append(api.Section(title="Encounter Orders", content=self.parse_orders(xml_root)))

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
            pat = api.Patient()
            pat.add_name(given=[self.firstName], family=[self.lastName])
            pat.add_maven_identifier(value=uuid.uuid1())
            pat.identifier.append(api.Identifier(system='NationalIdentifier', value=self.patientId))
            pat.address.append(api.Address(zip=self.zipcode))
            pat.birthDate = self.birthDate
            pat.gender = self.gender

        except:
            raise Exception('Error constructing patient from API and data')

        return pat

    def parse_encounter(self, xml_contact):
        """
        :param xml_contact: XML Encounter Contact from EPIC
        """

        pat_encounter = api.Encounter()

        try:
            root = ET.fromstring(xml_contact)
            contactDateTime = dateutil.parser.parse(root.findall(".//DateTime")[0].text)
            pat_encounter.period = api.Period(start=contactDateTime)
            department = root.findall(".//DepartmentName")[0].text
            pat_encounter.department = api.Location(name=department)
            depids = root.findall(".//DepartmentIDs/IDType")
            for dp in depids:
                if "internal" in dp.findall(".//Type")[0].text.lower():
                    id = dp.findall("ID")[0].text
                    pat_encounter.department.identifier.append(api.Identifier(label="Internal", system="clientEMR", value=id))
            csns = root.findall(".//IDs/IDType")
            for csn in csns:
                if "serial" in dp.findall(".//Type")[0].text.lower():
                    id = dp.findall("ID")[0].text
                    pat_encounter.identifier.append(api.Identifier(system="clientEMR", label="serial", value=id))
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

            procedure = api.Procedure()
            procedure.type = ord_type
            procedure.name = ord_name
            procedure.identifier.append(api.Identifier(system="clientEMR", label="name", value=ord_name))
            procedure.identifier.append(api.Identifier(system="clientEMR", label=ord_code_type, value=ord_code))

            encounter_orders.append(api.Order(detail=[procedure], text=ord_name))

        return encounter_orders

    def parse_medical_problem(self, xmlIn, pat, enc):

        prob = api.Condition(encounter=enc.id, subject=pat.id)
        root = xmlIn
        dxid = root.findall(".//DiagnosisIDs/IDType")
        # Loop through the dx ID's in this list until the internal one. Use that to instantiate a new DX Object
        for idtp in dxid:
            if "internal" in idtp.findall(".//Type")[0].text.lower():
                prob.identifier.append(api.Identifier(label="Internal", system="clientEMR", value=idtp.findall(".//ID")[0].text))
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

    def create_composition(self, xml_enc):
        composition = api.Composition(type="CostEvaluator")
        enc_root = ET.fromstring(xml_enc)
        composition.customer_id = 1

        for child in enc_root:
            if "EncID" in child.tag:
                if composition.encounter is not None:
                    composition.encounter.identifier.append(api.Identifier(system="clientEMR",
                                                                           label="Internal",
                                                                           value=child.text))
                else:
                    composition.encounter = api.Encounter()
                    composition.encounter.identifier.append(api.Identifier(system="clientEMR",
                                                                           label="Internal",
                                                                           value=child.text))

            elif "ProvID" in child.tag:
                if composition.encounter is None:
                    composition.encounter = api.Encounter()
                practitioner = api.Practitioner()
                practitioner.add_identifier(system="clientEMR",
                                            label="Internal",
                                            value=child.text)
                composition.encounter.add_practitioner(practitioner)

            elif "PatientDemographics" in child.tag:
                composition.subject = self.parse_demographics(child)

            elif "Orders" in child.tag:
                composition.section.append(api.Section(title="Encounter Orders",
                                                       content=self.parse_orders(child)))
            elif "ActiveProblems" in child.tag:
                composition.section.append(api.Section(title="Problem List",
                                                       content=self.parse_problem_list(child)))

        return composition

    def parse_demographics(self, xml_root):
        try:
            #Parse important data elements out of incoming XML using Python's ElementTree object
            city = xml_root.findall(".//City")[0].text
            country = xml_root.findall(".//Country")[0].text
            county = xml_root.findall(".//County")[0].text
            state = xml_root.findall(".//State")[0].text
            street = xml_root.findall(".//Street")[0].text
            zipcode = xml_root.findall(".//Zip")[0].text

            birthDate = dateutil.parser.parse(xml_root.findall(".//DateOfBirth")[0].text)
            birthMonth = birthDate.strftime('%m')
            gender = xml_root.findall(".//Gender")[0].text
            maritalStatus = xml_root.findall(".//MaritalStatus")[0].text
            firstName = xml_root.findall(".//FirstName")[0].text
            lastName = xml_root.findall(".//LastName")[0].text
            nationalIdentifier = xml_root.findall(".//NationalIdentifier")[0].text
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
            #Create Patient from the API using data from above
            patient = api.Patient()
            patient.add_name(given=[firstName], family=[lastName])
            patient.add_maven_identifier(value=uuid.uuid1())
            patient.identifier.append(api.Identifier(system='NationalIdentifier', value=patientSSN))
            if patientID is not None and patientIDType is not None:
                patient.identifier.append(api.Identifier(system='clientEMR', label=patientIDType, value=patientID))
            patient.address.append(api.Address(zip=zipcode, city=city,
                                           country=country, county=county,
                                           state=state, line=[street]))
            patient.birthDate = birthDate
            patient.gender = gender
            patient.maritalStatus = maritalStatus

        except:
            raise Exception('Error constructing FHIR patient from VistA XML data')

        return patient

    def parse_orders(self, xml_root):
        try:
            encounter_orders = []
            for ord in xml_root.findall(".//Order"):
                ord_id = ord.findall(".//ID")[0].text
                ord_name = ord.findall(".//Name")[0].text
                ord_code = ord.findall(".//ProcedureCode")[0].text
                ord_code_type = ord.findall(".//CodeType")[0].text
                if ord_code_type is None:
                    ord_code_type = "Internal"
                ord_type = ord.findall(".//Type")[0].text
                datetime = ord.findall(".//OrderingDate")[0].text.replace('@', ' ')
                ord_datetime = dateutil.parser.parse(datetime)


                procedure = api.Procedure()
                procedure.type = ord_type
                procedure.name = ord_name
                procedure.date = ord_datetime
                procedure.identifier.append(api.Identifier(system="clientEMR", label=ord_code_type, value=ord_code))
                encounter_orders.append(api.Order(detail=[procedure], text=ord_name))
        except:
            raise Exception("Error parsing Vista Encounter Orders")

        return encounter_orders

    def parse_problem_list(self, xml_root):
        problem_list = []

        try:
            for prb in xml_root.findall(".//Problems/Problem"):
                condition = self.parse_condition(prb)
                problem_list.append(condition)

        except:
            raise Exception('Error parsing problem list')

        return problem_list

    def parse_condition(self, xml_root):
        prob = api.Condition()
        dx_IDs = xml_root.findall(".//DiagnosisIDs/IDType")
        # Loop through the dx ID's in this list until the internal one. Use that to instantiate a new DX Object
        for id in dx_IDs:
            if "internal" in id.findall(".//Type")[0].text.lower():
                prob.identifier.append(api.Identifier(label="Internal", system="clientEMR", value=id.findall(".//ID")[0].text))
                #self.diagnosis = cliDiagnosis.cliDiagnosis(idtp.findall(".//ID")[0].text, config)

            elif "icd" in id.findall(".//Type")[0].text.lower():
                prob.identifier.append(api.Identifier(label="ICD", system="clientEMR", value=id.findall(".//ID")[0].text))

        prob.date_asserted = dateutil.parser.parse(xml_root.findall(".//NotedDate")[0].text)

        chron = xml_root.findall(".//IsChronic")[0].text
        if chron is not None and "true" in chron.lower():
            prob.isChronic = True

        hosp = xml_root.findall(".//IsHospitalProblem")[0].text
        if hosp is not None and "true" in hosp.lower():
            prob.isHospital = True

        poa = xml_root.findall(".//IsPresentOnAdmission")[0].text
        if poa is not None and "true" in poa.lower():
            prob.isPOA = True

        princ = xml_root.findall(".//IsPrincipal")[0].text
        if princ is not None and "true" in princ.lower():
            prob.isPrincipal = True

        return prob


if __name__ == '__main__':
    file = open('/home/devel/yukidev/maven/clientApp/fake_data/dave_test_encounter.xml')
    r = file.read()
    file.close()
    VistaParser().create_composition(r)
