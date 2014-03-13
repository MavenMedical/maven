#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:   This message_parser.py contains the classes required to parse the incoming
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
import argparse
import json


class EpicParser():

    def __init__(self):
        raise NotImplementedError

    def parse_demographics(self, xml_demog):

        demog_root = ET.fromstring(xml_demog)
        try:
            self.zipcode = demog_root.findall(".//Zip")[0].text
            self.firstName = demog_root.findall(".//FirstName")[0].text
            self.lastName = demog_root.findall(".//LastName")[0].text
            self.patientId = demog_root.findall(".//NationalIdentifier")[0].text
            self.gender = demog_root.findall(".//Gender")[0].text
            self.birthMonth = datetime.date(demog_root.findall(".//DateOfBirth")[0].text).strftime('%m')

        except:
            raise Exception('Error parsing demographics')

    def parse_problem_list(self, xml_prob_list):

        problem_list = []
        probl_root = ET.fromstring(xml_prob_list)
        try:
            for prb in probl_root.findall(".//Problems/Problem"):
                problem_list.append({'problem_comment', 'diagnosis_id'})

        except:
            raise Exception('Error parsing problem list')

        return problem_list

    def parse_encounter(self, str):
        raise NotImplementedError

    def parse_orders(self, str):
        raise NotImplementedError
