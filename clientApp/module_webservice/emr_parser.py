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
import maven_config as MC
import json
import clientApp.api.api as api
import uuid
import io
import dateutil.parser
from app.utils.database.database import AsyncConnectionPool,SingleThreadedConnection, MappingUtilites
import asyncio


class EpicParser():

    def __init__(self):
        #raise NotImplementedError
        pass

    def create_composition(self):
        raise NotImplementedError

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

if __name__ == '__main__':
    MavenConfig = {
        'test conn pool': {
            AsyncConnectionPool.CONFIG_CONNECTION_STRING:
            ("dbname=%s user=%s password=%s host=%s port=%s" % ('maven', 'maven', 'temporary', 'localhost', '5432')),
            AsyncConnectionPool.CONFIG_MIN_CONNECTIONS: 4,
            AsyncConnectionPool.CONFIG_MAX_CONNECTIONS: 8
        },
        'test blocking': {
            SingleThreadedConnection.CONFIG_CONNECTION_STRING:
            ("dbname=%s user=%s password=%s host=%s port=%s" % ('maven', 'maven', 'temporary', 'localhost', '5432'))
        }
    }

    MC.MavenConfig = MavenConfig


    composition = api.Composition(event="OutgoingToMavenMessage", author="MavenClientApp", type="CostEvaluator")

    EP_pat = EpicParser().parse_demographics("<GetPatientDemographicsResult><Address><City>Madison</City><Country>United States</Country><County>Dane</County><State>Wisconsin</State><Street xmlns:a=\"http://schemas.microsoft.com/2003/10/Serialization/Arrays\"><a:string>134 Memory Ln.</a:string></Street><Zip>53714</Zip></Address><DateOfBirth>1956-06-04T00:00:00</DateOfBirth><Email></Email><Gender>Male</Gender><MaritalStatus>Married</MaritalStatus><Name><FirstName>Adam</FirstName><LastName>Aardvark</LastName><MaidenName></MaidenName><MiddleName></MiddleName><Nickname></Nickname><Suffix></Suffix><Title></Title></Name><NationalIdentifier>999-42-0089</NationalIdentifier><Phones><Phone><Number>999-555-0088</Number><Type>Home Phone</Type></Phone></Phones><Race></Race><Religion></Religion></GetPatientDemographicsResult>")
    composition.subject = EP_pat

    EP_enc = EpicParser().parse_encounter("<Contact><DateTime>2009-04-20T07:54:48</DateTime><DepartmentAbbreviation>WI HBN ED</DepartmentAbbreviation><DepartmentIDs><IDType><ID>1231</ID><Type>Internal</Type></IDType></DepartmentIDs><DepartmentName>WI HARBOR BLUFF ED</DepartmentName><IDs><IDType><ID>257549</ID><Type>Contact Serial Number</Type></IDType><IDType><ID>15844</ID><Type>External Visit ID</Type></IDType></IDs><PatientClass>E</PatientClass><Type>Hospital Encounter</Type></Contact>")
    composition.encounter = EP_enc

    EP_pl = EpicParser().parse_problem_list("<GetActiveProblemsResult><ErrorCode></ErrorCode><Problems><Problem><Comment>Severe Asthma</Comment><Description></Description><DiagnosisIDs><IDType><ID>120910</ID><Type>Internal</Type></IDType></DiagnosisIDs><EntryPerson><ID>8941</ID><Name>SEWAK, MIHIR S</Name></EntryPerson><IsChronic>false</IsChronic><IsHospitalProblem>false</IsHospitalProblem><IsPresentOnAdmission></IsPresentOnAdmission><IsPrincipal>false</IsPrincipal><IsVisibleToPatient>true</IsVisibleToPatient><NotedDate>2011-01-01T00:00:00</NotedDate><Priority>1</Priority><ProblemClass>1</ProblemClass><ProblemIDs><IDType><ID>2610049</ID><Type>Internal</Type></IDType></ProblemIDs></Problem></Problems></GetActiveProblemsResult>", EP_pat, EP_enc)
    composition.section.append(api.Section(title="Problem List", content=EP_pl))

    EP_ord = EpicParser().parse_orders("<Orders>    <Order>          <ProcedureCode>1234567</ProcedureCode>          <CodeType>Internal</CodeType>          <ExpectedDate>2011-01-01T00:00:00</ExpectedDate>          <ExpiredDate></ExpiredDate>          <Name>CBC with Automated Diff</Name>          <Type>Lab</Type>   </Order><Order>          <ProcedureCode>2345678</ProcedureCode>          <CodeType>Internal</CodeType>          <ExpectedDate>2011-01-01T00:00:00</ExpectedDate>          <ExpiredDate></ExpiredDate>          <Name>CBC with Automated Diff</Name>          <Type>Lab</Type>   </Order></Orders>")
    composition.section.append(api.Section(title="Encounter Orders", content=EP_ord))

    EP_pat_json = json.dumps(composition, default=api.jdefault, indent=4)
    print(EP_pat_json)

    comp_recreated = json.loads(EP_pat_json)
    print(comp_recreated['type'])
    for sec in comp_recreated['section']:
        if sec['title'] == "Problem List":
            for dx in sec['content']:
                print(dx['identifier'][0]['label'])
                print(dx['identifier'][0]['value'])

    comp_r = api.Composition().create_composition_from_json(comp_recreated)
    orders = comp_r.get_encounter_orders()

    orders_cost_query = []
    orders = comp_r.get_encounter_orders()

    for order in orders:
        order_details = composition.get_proc_supply_details(order)

        for detail in order_details:
            orders_cost_query.append([detail[0], detail[1]])

    total_cost = 0.0
    orders_cost_summary = []

    print(orders_cost_query)
    conn = SingleThreadedConnection('test conn pool')
    for order in orders_cost_query:
        cur = conn.execute("select cost_amt from costmap where billing_code='%s'" % order[0])
        for result in cur:
            order.append(float(result[0]))
            #order['totalCost'] = float(result[0])
            total_cost += float(result[0])

    print(orders_cost_query)
    print(total_cost)