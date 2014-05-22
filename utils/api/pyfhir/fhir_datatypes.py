#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:   This fhir_datatypes.py file contains the necessary objects required to represent the
#               simple and complex datatypes required by the FHIR Standard
#
#
#
#************************
#ASSUMES:
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-165
#*************************************************************************

from enum import Enum


class Period():

    def __init__(self, start=None, end=None):
        self.start = start
        self.end = end


class Identifier():

    def __init__(self, value, use=None, label=None, system=None, period=None, assigner=None):
        self.use = use               # usual | official | temp | secondary (If known)
        self.label = label             # Description of identifier
        self.system = system
        self.value = value
        self.period = period
        self.assigner = assigner


class CodeableConcept():

    def __init__(self, text=None, coding=None):
        self.text = text
        if coding is None:
            self.coding = []


class Coding():

    def __init__(self, system=None, version=None, code=None, display=None, primary=False, valueSet=None):
        self.system = system
        self.version = version
        self.code = code
        self.display = display
        self.primary = primary
        self.valueSet = valueSet


class Quantity():

    def __init__(self, value=None, comparator=None, units=None, system=None, code=None):
        self.value = value
        self.comparator = comparator
        self.units = units
        self.system = system
        self.code = code


class Range():

    def __init__(self, low=None, high=None):
        self.low = low
        self.high = high


class ReferenceRange():

    def __init__(self, low=None, high=None, meaning=None, age=None):
        self.low = low
        self.high = high
        self.meaning = meaning
        self.age = age


class Related():

    def __init__(self, type=None, target=None):
        self.type = type
        self.target = target


class Hospitalization():

    def __init__(self, preAdmissionIdentifier=None, origin=None,
                 period=None, destination=None,
                 dischargeDiagnosis=None, reAdmission=False):

        if preAdmissionIdentifier is None:
            self.preAdmissionIdentifier = []
        self.origin = origin
        self.admitSource = None
        self.period = period
        self.destination = destination
        self.dischargeDisposition = None
        self.dischargeDiagnosis = dischargeDiagnosis
        self.reAdmission = reAdmission


class HumanName():

    def __init__(self, use=None, text=None, family=None, given=None, prefix=None, suffix=None, period=None):
        self.use = use
        self.text = text
        self.period = period

        if family is None:
            self.family = []
        else:
            self.family = family

        if given is None:
            self.given = []
        else:
            self.given = given

        if prefix is None:
            self.prefix = []

        if suffix is None:
            self.suffix = []


class RelatedItem():

    def __init__(self, type=None, target=None):
        self.type = type
        self.target = target


class Accomodation():

    def __init__(self):
        self.bed = ""
        self.period = ""


class Address():

    def __init__(self, use=None, text=None, line=None, city=None, state=None, zip=None, country=None, period=None, county=None):
        self.use = use
        self.text = text
        if line is None:
            self.line = []
        self.city = city
        self.state = state
        self.zip = zip
        self.country = country
        self.period = period
        self.county = county


class Schedule():
    def __init__(self, event=None, frequency=1):
        self.event = event
        self.frequency = frequency


class Section():
    def __init__(self, title=None, code=None, subject=None, content=None):
        self.title = title
        self.code = code
        self.subject = subject
        self.content = content
        #if content is None:
        #    self.content = []


class Event():
    def __init__(self, type=None, subtype=None, action=None, dateTime=None, outcome=None, outcomeDesc=None):
        self.type = type
        self.subtype = subtype
        self.action = action
        self.dateTime = dateTime
        self.outcome = outcome
        self.outcomeDesc = outcomeDesc


class Participant():
    def __init__(self, role=None, reference=None, userId=None, altId=None, name=None, requestor=False, media=None, network=None):
        self.role = role
        self.reference = reference
        self.userId = userId
        self.altId = altId
        self.name = name
        self.requestor = requestor
        self.media = media
        self.network = network


class Object():
    def __init__(self, identifier=None, reference=None, type=None, role=None, lifecycle=None,
                 sensitivity=None, name=None, description=None, query=None, detail=None):
        self.identifier = identifier
        self.reference = reference
        self.type = type
        self.role = role
        self.lifecycle = lifecycle
        self.sensitivity = sensitivity
        self.name = name
        self.description = description
        self.query = query
        if detail is None:
            self.detail = []


class Source():
    def __init__(self, site=None, identifier=None, type=None):
        self.site = site
        self.identifier = identifier
        self.type = type


class Network():
    def __init__(self, identifier=None, type=None):
        self.identifier = identifier
        self.type = type