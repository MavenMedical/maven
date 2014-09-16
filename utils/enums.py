# *************************************************************************
# Copyright (c) 2014 - Maven Medical
# ************************
# AUTHOR:
__author__ = 'Yuki Uchino'
# ************************
# DESCRIPTION:   This enums.py contains the enums/lists that are standardized throughout various applications
#
#
#
#
# ************************
# ASSUMES:
# ************************
# SIDE EFFECTS:
# ************************
# LAST MODIFIED FOR JIRA ISSUE: MAV-223
# *************************************************************************
from enum import Enum


class ALERT_TYPES(Enum):
    CDS = "Evidence"
    COST = "Transparent"
    REC_RESULT = "Recent Results"
    ALT_MED = "Alternative Medications"
    PATHWAY = "Pathways"


class ALERT_PRIORITY(Enum):
    COST = 1
    REC_RESULT = 2
    ALT_MED = 3
    CDS = 4


class ALERT_SETTING_ACTIONS(Enum):
    LI = "like"
    DI = "dislike"
    OI = "opt in"
    OO = "opt out"


class ALERT_VALIDATION_STATUS(Enum):
    SUPPRESS = -1
    NO_SEND = 100
    DEBUG_ALERT = 200
    DEVICE_ALERT = 300
    EHR_ALERT = 400


class CONDITION_TYPE(Enum):
    PL = "Problem List Diagnosis"
    ENC = "Encounter Diagnosis"


class DIAGNOSTIC_TERMINOLOGIES(Enum):
    icd9 = "International Statistical Classification of Diseases Version 9"
    ICD9 = "International Statistical Classification of Diseases Version 9"
    icd10 = "International Statistical Classification of Diseases Version 10"
    ICD10 = "International Statistical Classification of Diseases Version 10"
    snomed = "SNOMED CT"
    SNOMED = "SNOMED CT"


class MEDICATION_ORDER_TYPES(Enum):
    med = "Medication"
    meds = "Medication"
    medication = "Medication"
    medications = "Medication"


class NOTIFICATION_STATE(Enum):
    OFF = "User not Connected to Notification Service"
    DESKTOP = "User Registered with Desktop Notification Service"
    MOBILE = "User Registered with Mobile Notification Service"


class ORDER_SOURCE(Enum):
    WEBSERVICE = "Orders that came in via Webservice"
    EXTRACT = "Orders that were identified/updated via an Extract"


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


class PROCEDURE_TERMINOLOGIES(Enum):
    cpt = "Current Procedural Terminology"
    CPT = "Current Procedural Terminology"
    cpt4 = "Current Procedural Terminology v4"
    CPT4 = "Current Procedural Terminology v4"
    HCPCS = "Healthcare Common Procedure Coding System"
    hcpcs = "Healthcare Common Procedure Coding System"


class USER_ROLES(Enum):
    mavensupport = "mavensupport"
    maventask = "maventask"
    provider = "provider"
    supervisor = "supervisor"
    notification = "notification"
    administrator = "administrator"


class USER_STATE(Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
