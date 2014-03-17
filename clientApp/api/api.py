import uuid
import datetime
from enum import Enum


class Resource():

    def __init__(self, customer_id=None, name_space=None, identifier=None):
        self.customer_id = customer_id
        self.name_space = name_space
        self.id = uuid.uuid1()
        self.version_id = 1
        self.last_modified_date = datetime.datetime.now()

        if identifier is None:
            self.identifier = []

    def add_identifier(self, use, label, system, value, period, assigner):
        """
        This method is used to add an identifier to the list of identifiers associated with this resource

        :param use:
        :param label:
        :param system:
        :param value:
        :param period:
        :param assigner:
        """
        self.identifier.append(Identifier(use=use,
                                          label=label,
                                          system=system,
                                          value=value,
                                          period=period,
                                          assigner=assigner))

    def add_maven_identifier(self, value, period=None, assigner=None):
        """
        This method is used to add an identifier to the list of identifiers associated with this resource

        :param use:
        :param label:
        :param system:
        :param value:
        :param period:
        :param assigner:
        """
        identifier_use = 'official'
        identifier_label = 'maven-resource'
        identifier_system = 'maven'

        self.identifier.append(Identifier(use=identifier_use,
                                          label=identifier_label,
                                          system=identifier_system,
                                          value=value,
                                          period=period,
                                          assigner=assigner))


class Patient(Resource):

    def __init__(self, name=None, identifier=None, birthDate=None, gender=None, address=None, problem_list=None):
        Resource.__init__(self, identifier=identifier)
        if name is None:
            self.name = []
        self.telecom = []
        self.gender = gender
        self.birthDate = birthDate
        self.deceased = False
        if address is None:
            self.address = []
        if problem_list is None:
            self.problem_list = []
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

    def add_name(self, given, family, use=None, text=None, prefix=None, suffix=None, period=None):
        last_name = family
        first_name = given
        self.name.append(HumanName(use=use,
                                   text=text,
                                   family=family,
                                   given=given,
                                   prefix=prefix,
                                   suffix=suffix,
                                   period=period))

    def get_birth_month(self):
        return self.birthDate.strftime('%m')

    def set_birth_date(self, datetime):
        self.birthDate = datetime


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

    def __init__(self, type=None):
        Resource.__init__(self)
        OrganizationType = Enum('prov', 'dept', 'icu', 'team', 'fed', 'ins', 'edu', 'reli', 'pharm')
        self.type = type
        self.type = []
        self.telecom = []
        self.address = []
        self.partOf = ""
        self.location = []
        self.active = True


class Encounter(Resource):

    def __init__(self, status=None, encounter_class=None, type=None, subject=None,
                 period=None, serviceProvider=None, partOf=None, participant=None,
                 hospitalization=None, department=None):
        Resource.__init__(self)
        self.status = status
        self.encounter_class = encounter_class
        self.type = type
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
        self.department = department

    def add_practitioner(self, practitioner):
        self.participant.append(practitioner)

    def get_admit_date(self):
        return self.period.start

    def get_discharge_date(self):
        return self.period.end


class Procedure(Resource):

    def __init__(self, patient=None, encounter=None, period=None,
                 performer=None, followUp=None, type=None):
        Resource.__init__(self)
        self.subject = patient
        self.patient = patient
        self.type = type
        self.encounter = encounter
        self.outcome = ""
        self.date = period
        self.followUp = followUp
        self.notes = ""
        self.performer = performer


class Order(Resource):

    def __init__(self, patient=None, practitioner=None, detail=None, when=None):
        Resource.__init__(self)
        self.date = datetime.datetime.now()
        self.subject = patient
        self.patient = patient
        self.source = practitioner
        self.practitioner = practitioner
        self.target = None

        if detail is None:
            self.detail = []

        if when is None:
            self.when = []


class OrderResponse(Resource):

    def __init__(self, request=None, responder=None, fulfillment=None):
        Resource.__init__(self)
        self.request = request
        self.date = datetime.datetime.now()
        self.who = responder
        self.code = ""
        self.description = ""
        if fulfillment is None:
            self.fulfillment = []


class Medication(Resource):

    def __init__(self, name=None, code=None, isBrand=False, manufacturer=None, kind=None):
        Resource.__init__(self)
        self.name = name
        self.code = code
        self.isBrand = isBrand
        self.manufacturer = manufacturer
        self.kind = kind


class Alert(Resource):

    def __init__(self, category=None, status=None, subject=None, author=None):
        Resource.__init__(self)
        self.category = category
        self.status = status
        self.subject = subject
        self.author = author
        self.note = ""


class Observation(Resource):

    def __init__(self, subject=None, specimen=None, performer=None, related=None, reference_range=None):
        Resource.__init__(self)
        self.subject = subject
        self.specimen = specimen
        if performer is None:
            self.performer = []

        if related is None:
            self.related = []

        if reference_range is None:
            self.reference_range = []


class List(Resource):

    def __init__(self, code=None, subject=None, source=None,
                          date=None, ordered=True, mode=None,
                          emptyReason=None, entry=None):
        Resource.__init__(self)
        self.code = code
        self.subject = subject
        self.source = source
        self.date = date
        self.ordered = ordered
        self.mode = mode
        self.emptyReason = emptyReason

        if entry is None:
            self.entry = []


    def add_entry(self, resource):
        self.entry.append(resource)


class Condition(Resource):

    def __init__(self, subject=None, encounter=None, asserter=None, date_asserted=None,
                 code=None, category=None, status=None, notes=None, related_item=None,
                 isChronic=None, isHospital=None, isPOA=None, isPrinciple=None):
        Resource.__init__(self)
        self.subject = subject
        self.encounter = encounter
        self.asserter = asserter
        if date_asserted is None:
            self.date_asserted = datetime.datetime.now()
        self.code = code
        self.category = category
        self.status = status
        self.notes = notes
        if related_item is None:
            self.related_item = []
        self.isChronic = isChronic
        self.isHospital = isHospital
        self.isPOA = isPOA
        self.isPrinciple = isPrinciple


class Location(Resource):

    def __init__(self, name=None, description=None, type=None,
                 telecom=None, address=None, managingOrganization=None,
                 status=None, partOf=None, mode=None):
        Resource.__init__(self)
        self.name = name
        self.description = description
        self.type = type
        self.telecom = telecom
        self.address = address
        self.managingOrganization = managingOrganization
        self.status = status
        self.partOf = partOf
        self.mode = mode





#####
#####
#####
#####
##### DATA TYPES REFERENCED BY THE RESOURCES ABOVE. THESE ITEMS DO NOT INHERIT RESOURCE
#####
#####
#####

class Identifier():

    def __init__(self, value, use=None, label=None, system=None, period=None, assigner=None):
        self.use = use               # usual | official | temp | secondary (If known)
        self.label = label             # Description of identifier
        self.system = system
        self.value = value
        self.period = period
        self.assigner = assigner


class Period():

    def __init__(self, start=None, end=None):
        self.start = start
        self.end = end


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

    def __init__(self, use=None, text=None, line=None, city=None, state=None, zip=None, country=None, period=None):
        self.use = use
        self.text = text
        if line is None:
            self.line = []
        self.city = city
        self.state = state
        self.zip = zip
        self.country = country
        self.period = period


class Schedule():

    def __init__(self, event=None, frequency=1):
        self.event = event
        self.frequency = frequency


def jdefault(o):
    if isinstance(o, datetime.datetime):
        return datetime.datetime
    else:
        if hasattr(o, '__dict__'):
            return o.__dict__
