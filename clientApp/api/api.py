import uuid
import datetime

from enum import Enum


class Resource():

    def __init__(self, customer_id=None, name_space=None, identifier=None, name=None):
        self.customer_id = customer_id
        self.name_space = name_space
        self.id = uuid.uuid1()
        self.version_id = 1
        self.last_modified_date = datetime.datetime.now()

        if identifier is None:
            self.identifier = []

        if name is None:
            self.name = []

    def add_identifier(self, use, label, system, value, period, assigner):
        self.identifier.append(Identifier(use=use,
                                          label=label,
                                          system=system,
                                          value=value,
                                          period=period,
                                          assigner=assigner))

    def add_name(self, use, text, family, given, prefix, suffix, period):
        self.name.append(HumanName(use=use,
                                   text=text,
                                   family=family,
                                   given=given,
                                   prefix=prefix,
                                   suffix=suffix,
                                   period=period))


class Patient(Resource):

    def __init__(self):
        Resource.__init__(self)
        self.telecom = []
        self.gender = None
        self.birthDate = None
        self.deceased = False
        self.address = []
        self.maritalStatus = ""
        self.multipleBirth = 0
        self.photo = []
        self.communication = []
        self.careProvider = []
        self.managingOrganization = []
        self.active = True
        self.contact = []
        self.link = []

        firstName = ""
        lastName = ""
        birthMonth = ""
        zipcode = ""
        patientId = ""
        gender = ""
        config = None
        problemList = []
        Encounter=None


    def add_careProvider(self, orgclinician):
        self.careProvider.append(orgclinician)


class Practitioner(Resource):

    def __init__(self, organization=None):
        Resource.__init__(self)
        self.telecom = []
        self.address = ""
        self.gender = []
        self.birthDate = ""
        self.photo = None

        if organization is None:
            self.organization = []
        self.role = []
        self.specialty = []
        self.period = ""
        self.location = []
        self.qualification = [{'code', 'period', 'issuer'}]
        self.communication = []


class Organization(Resource):

    def __init__(self):
        Resource.__init__(self)
        OrganizationType = Enum('prov', 'dept', 'icu', 'team', 'fed', 'ins', 'edu', 'reli', 'pharm')
        self.type = OrganizationType.dept
        self.type = []
        self.telecom = []
        self.address = []
        self.partOf = ""
        self.location = []
        self.active = True


class Encounter(Resource):

    def __init__(self, status=None, encounter_class=None, subject=None,
                 period=None, serviceProvider=None, partOf=None, participant=None,
                 hospitalization=None):
        Resource.__init__(self)
        self.status = status
        self.encounter_class = encounter_class
        self.type = None
        self.subject = subject
        self.period = period
        self.length = None
        self.reason = None
        self.indication = None
        self.priority = None
        self.serviceProvider = serviceProvider
        self.partOf = partOf

        if participant is None:
            self.participant = []
        self.hospitalization = hospitalization


class Procedure(Resource):

    def __init__(self, patient=None, encounter=None, period=None, performer=None, followUp=None):
        Resource.__init__(self)
        self.subject = patient
        self.patient = patient
        self.type = None
        self.encounter = encounter
        self.outcome = ""
        self.date = period
        self.followUp = followUp
        self.notes = ""
        self.performer = performer


#####
#####
#####
#####
##### DATA TYPES REFERENCED BY THE RESOURCES ABOVE. THESE ITEMS DO NOT INHERIT RESOURCE
#####
#####
#####

class Identifier():

    def __init__(self, use=None, label=None, system=None, value=None, period=None, assigner=None):
        self.use = use               # usual | official | temp | secondary (If known)
        self.label = label             # Description of identifier
        self.system = system
        self.value = value
        self.period = period
        self.assigner = assigner


class Period():

    def __init__(self):
        self.start = ""
        self.end = ""


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

        if given is None:
            self.given = []

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