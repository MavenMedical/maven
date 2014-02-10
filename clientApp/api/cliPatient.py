from _elementtree import tostring
from datetime import datetime
import cliEncounter
from cliProblem import cliProblem
from obfuscator import obfuscator

class cliPatient:
    """*************************************************************************
    *  Copyright (c) 2014 - Maven Medical
    * __________________
    *
    *  Description: This class represents a patients Patient Record from the EMR system.
    *               It lives on the non-cloud system
    *  Author: Dave
    *  Assumes: xml Format  - Check
    *  Side Effects: None
    *  Last Modified: MAV-35
    * *************************************************************************"""

    firstName = ""
    lastName = ""
    birthMonth = ""
    zipcode = ""
    patientId = ""
    gender = ""
    config = None
    problemList = []
    Encounter=None

    def __init__(self, demogstring, probstring, encstring, ordstring, config):
        if config.EMR == "Epic":
            EpicParse(self, demogstring, probstring, encstring, ordstring, config)

def EpicParse(self, xmlDemog, xmlProbList, xmlEnc, xmlOrd, config):
    obf=obfuscator(config)
    import xml.etree.ElementTree as etree
    try:
        root = etree.fromstring(xmlDemog)
        self.zipcode = root.findall(".//Zip")[0].text
        #names and other identifiers will be hashed and salted
        self.firstName = obf.hash(root.findall(".//FirstName")[0].text)
        self.lastName = obf.hash(root.findall(".//LastName")[0].text)
        self.patientId = obf.hash(root.findall(".//NationalIdentifier")[0].text)
        self.gender = root.findall(".//Gender")[0].text
        bdate = datetime.strptime(root.findall(".//DateOfBirth")[0].text,config.dateFormat)
        self.birthMonth = (bdate.year*100)+bdate.month

        root = etree.fromstring(xmlProbList)
        for prb in root.findall(".//Problems/Problem"):
            self.problemList.append(cliProblem(tostring(prb), config))

        self.Encounter = cliEncounter.cliEncounter(xmlEnc, xmlOrd, config)

    except:
        raise Exception("cliPatient: Could not parse the initial xml input.")



