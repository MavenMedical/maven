import cliDiagnosis
import obfuscator
from datetime import datetime

__author__ = 'dave'

class cliProblem:
    """*************************************************************************
    *  Copyright (c) 2014 - Maven Medical
    * __________________
    *
    *  Description: This class represents a patients Problem List from the EMR system.
    *               It lives on the non-cloud system
    *  Author: Dave
    *  Assumes: xml Format  - Check
    *  Side Effects: None
    *  Last Modified: MAV-35
    * *************************************************************************"""
    diagnosis = None
    dateNoted = None
    isChronic = False
    isHospital = False
    isPOA = False
    isPrincipal=False

    def __init__(self, probstring, config):
        if config.EMR == "Epic":
            EpicParse(self, probstring, config)

def EpicParse(self, xmlIn, config):
    import xml.etree.ElementTree as etree
    try:
        root = etree.fromstring(xmlIn)
        dxid = root.findall(".//DiagnosisIDs/IDType")
        # Loop through the dx ID's in this list until the internal one. Use that to instantiate a new DX Object
        for idtp in dxid:
            if "internal" in idtp.findall(".//Type")[0].text.lower():
                self.diagnosis = cliDiagnosis.cliDiagnosis(idtp.findall(".//ID")[0].text, config)
                break
        self.dateNoted = datetime.strptime(root.findall(".//NotedDate")[0].text, config.dateFormat)
        chron=root.findall(".//IsChronic")[0].text
        if chron != None and "true" in chron.lower():
            self.isChronic = True
        hosp = root.findall(".//IsHospitalProblem")[0].text
        if hosp != None and "true" in hosp.lower():
            self.isHospital = True
        poa = root.findall(".//IsPresentOnAdmission")[0].text
        if poa != None and "true" in poa.lower():
            self.isPOA = True
        princ = root.findall(".//IsPrincipal")[0].text
        if princ != None and "true" in princ.lower():
            self.isPrincipal = True

    except:
        raise Exception("cliProblem: Could not parse the initial xml input.")
    pass