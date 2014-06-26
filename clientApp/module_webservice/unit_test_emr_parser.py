#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:
#
#
#
#
#************************
#ASSUMES:
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE:
#*************************************************************************
import unittest
from emr_parser import VistaParser
import datetime


class TestEMRParser(unittest.TestCase):

    def setUp(self):
        with open("/home/devel/maven/clientApp/module_webservice/test_message_from_ehr") as f:
            r = f.readlines()
            self.composition = VistaParser().create_composition(r[11])

    def test_demographics(self):
        """
        Test to make sure we're properly parsing the following data elements

        * Name
        * Birthdate
        * Address
        * SSN
        * PatientID
        """
        self.assertEqual(self.composition.subject.get_name(), "ALLERGIES, SUZY")
        self.assertEqual(self.composition.subject.birthDate, datetime.datetime(2003, 1, 2))
        self.assertEqual(self.composition.subject.get_pat_id(), "1235412")

    def test_encounter(self):
        pass

    def test_encounter_order(self):
        pass

    def test_encounter_dx(self):
        pass