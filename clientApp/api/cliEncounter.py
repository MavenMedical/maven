from datetime import datetime
import cliProcOrder
import obfuscator

__author__ = 'dave'

class cliEncounter:
    """*************************************************************************
    *  Copyright (c) 2014 - Maven Medical
    * __________________
    *
    *  Description: This class represents a patient Encounter from the EMR system.
    *               It lives on the non-cloud system
    *  Author: Dave
    *  Assumes: xml Format  - Check
    *  Side Effects: None
    *  Last Modified: MAV-35
    * *************************************************************************"""
    contactDateTime=None
    depName=""
    depId=""
    contactId=""
    contactType=""
    patientClass=""
    providerId=""
    orders=[]
    encDiagnoses=[]

    def __init__(self, contactstring, ordstring, config):
        if config.EMR == "Epic":
            EpicParse(self, contactstring, ordstring, config)

def EpicParse(self,xmlContact,xmlOrders,config):
    # obf=obfuscator(config)  # If you wanted to hash something, simply uncomment this
    import xml.etree.ElementTree as etree
    try:
        root = etree.fromstring(xmlContact)
        self.contactDateTime = datetime.strptime(root.findall(".//DateTime")[0].text, config.dateFormat)
        self.depName = root.findall(".//DepartmentName")[0].text
        depids = root.findall(".//DepartmentIDs/IDType")
        for dp in depids:
            if "internal" in dp.findall(".//Type")[0].text.lower():
                self.depId=dp.findall("ID")[0].text
        csns = root.findall(".//IDs/IDType")
        for csn in csns:
            if "serial" in dp.findall(".//Type")[0].text.lower():
                self.contactId=dp.findall("ID")[0].text
        self.contactType = root.findall("./Type")[0].text
        patclass = root.findall("./PatientClass")[0].text
        if patclass == "E":
            self.patientClass="Emergency"
        elif patclass == "I":
            self.patientClass="Inpatient"
        else:
            self.patientClass="Ambulatory"

        self.providerId=""  # TODO: Figure out how to get this at some point

        root = etree.fromstring(xmlOrders)
        for ord in root.findall(".//Order"):
            self.orders.append(cliProcOrder.cliProcOrder(ord.findall(".//Name")[0].text, ord.findall(".//ProcedureCode")[0].text
                                            , ord.findall(".//CodeType")[0].text, ord.findall(".//Type")[0].text))

        # TODO add encounter diagnoses

    except:
        raise #Exception("cliEncounter: Could not parse the initial xml input.")