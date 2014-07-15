#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:   This enums.py contains the enums/lists that are standardized throughout various applications
#
#
#
#
#************************
#ASSUMES:
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-223
#*************************************************************************
from enum import Enum


class ALERT_TYPES(Enum):
    cds = "Evidence"
    cost = "Transparent"
    dup_order = "Recent Results"
    alt_med = "Alternative Medications"


class CONDITION_TYPE(Enum):
    PL = "Problem List Diagnosis"
    ENC = "Encounter Diagnosis"


class ORDER_TYPES(Enum):
    Imaging = "Radiological Procedure"
    Lab = "Laboratory Procedure"
    Med = "Medication"
    Medication = "Medication"
    Proc = "General Medical Procedure"
    Procedure = "General Medical Procedure"


class PROCEDURE_ORDER_TYPES(Enum):
    proc = "General Medical Procedure"
    procs = "General Medical Procedure"
    procedure = "General Medical Procedure"
    procedures = "General Medical Procedure"
    lab = "Laboratory Procedure"
    labs = "Laboratory Procedures"
    imaging = "Radiological Procedure"



class ORDER_STATUS(Enum):
    ER = "Error, order not found"
    SC = "In process, scheduled"
    IP = "In process, unspecified"
    RP = "Order has been replaced"
    CM = "Order is completed"
    HD = "Order is on hold"
    CA = "Order was canceled"
    DC = "Order was discontinued"
    A = "Some, but not all, results available"


class PROCEDURE_TERMINOLOGIES(Enum):
    cpt = "Current Procedural Terminology"
    CPT = "Current Procedural Terminology"
    cpt4 = "Current Procedural Terminology v4"
    CPT4 = "Current Procedural Terminology v4"
    HCPCS = "Healthcare Common Procedure Coding System"
    hcpcs = "Healthcare Common Procedure Coding System"


class DIAGNOSTIC_TERMINOLOGIES(Enum):
    icd9 = "International Statistical Classification of Diseases Version 9"
    ICD9 = "International Statistical Classification of Diseases Version 9"
    icd10 = "International Statistical Classification of Diseases Version 10"
    ICD10 = "International Statistical Classification of Diseases Version 10"
    snomed = "SNOMED CT"
    SNOMED = "SNOMED CT"