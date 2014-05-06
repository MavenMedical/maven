import uuid
import datetime
import dateutil.parser


class Resource():

    def __init__(self, customer_id=None, name_space=None, identifier=None, text=None, resourceType=None):
        self.customer_id = customer_id
        self.name_space = name_space
        self.id = uuid.uuid1()
        self.version_id = 1
        self.last_modified_date = datetime.datetime.now()

        if text is None:
            self.text = ""

        if identifier is None:
            self.identifier = []
        self.resourceType = resourceType

    def add_identifier(self, use=None, label=None, system=None, value=None, period=None, assigner=None):
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
        identifier_label = 'Internal'
        identifier_system = 'maven'

        self.identifier.append(Identifier(use=identifier_use,
                                          label=identifier_label,
                                          system=identifier_system,
                                          value=value,
                                          period=period,
                                          assigner=assigner))


class Composition(Resource):

    def __init__(self, date=None, type=None, cclass=None,
                 title=None, status=None, confidentiality=None,
                 subject=None, author=None, custodian=None, encounter=None,
                 section=None, event=None, maven_route_key=None):
        Resource.__init__(self)
        if date is None:
            self.date = datetime.datetime.now()
        self.type = type
        self.cclass = cclass
        self.title = title
        self.status = status
        self.confidentiality = confidentiality
        self.subject = subject
        self.author = author
        self.custodian = custodian
        self.event = event
        self.encounter = encounter
        self.maven_route_key = maven_route_key

        if section is None:
            self.section = []

    def create_composition_from_json(self, json_composition):

        composition = Composition()

        if json_composition['customer_id'] is not None:
            composition.customer_id = int(json_composition['customer_id'])

        if json_composition['subject'] is not None:
            composition.subject = self.create_patient_from_json(json_composition['subject'])

        if json_composition['encounter'] is not None:
            composition.encounter = self.create_encounter_from_json(json_composition['encounter'])

        for sec in json_composition['section']:
            if sec['title'] == "Encounter Orders":
                composition.section.append(Section(title="Encounter Orders", content=self.create_orders_from_json(sec['content'])))

            elif sec['title'] == "Problem List":
                composition.section.append(Section(title="Problem List", content=self.create_problem_list_from_json(sec['content'])))

            elif sec['title'] == "Encounter Cost Breakdown":
                composition.section.append(Section(title="Encounter Cost Breakdown", content=sec['content']))

        return composition

    def create_patient_from_json(self, json_patient):
        """
        This method takes a json_patient object and converts the json string dictionary
        into a FHIR-compliant Patient Object from this clinical API library

        :param json_patient: A json string representation of a patient, most likely the "subject"
                             parameter from a composition object.
        """
        patient = Patient()

        if json_patient['gender'] is not None:
            patient.gender = json_patient['gender']

        if json_patient['birthDate'] is not None:
            patient.birthDate = dateutil.parser.parse(json_patient['birthDate'])

        if len(json_patient['name']) > 0:
            for name in json_patient['name']:
                patient.add_name(given=[name['given'][0]], family=[name['family'][0]])

        if len(json_patient['identifier']) > 0:
            for id in json_patient['identifier']:
                patient.add_identifier(label=id['label'], system=id['system'], value=id['value'])
        return patient

    def create_encounter_from_json(self, json_encounter):
        encounter = Encounter()
        encounter.last_modified_date = dateutil.parser.parse(json_encounter['last_modified_date'])

        if json_encounter['period'] is not None:
            encounter.period = Period(start=json_encounter['period']['start'], end=json_encounter['period']['end'])

        if json_encounter['department'] is not None:
            encounter.department = Location(name=json_encounter['department']['name'],
                                            customer_id=json_encounter['department']['customer_id'])

        if json_encounter['identifier'] is not None:
            for id in json_encounter['identifier']:
                encounter.identifier.append(Identifier(label=id['label'], system=id['system'], value=id['value']))

        if json_encounter['encounter_class'] is not None:
            encounter.encounter_class = json_encounter['encounter_class']

        if len(json_encounter['participant']) > 0:
            for prov in json_encounter['participant']:
                practitioner = Practitioner()

                for id in prov['identifier']:
                    practitioner.identifier.append(Identifier(label=id['label'], system=id['system'], value=id['value']))

                encounter.participant.append(practitioner)

        if json_encounter['type'] != "null":
            encounter.type = json_encounter['type']

        return encounter

    def create_orders_from_json(self, json_orders):
        orders_list = []
        for ord in json_orders:
            order = Order()

            #A FHIR order actually contains a list of DETAILS where the list of procedures,
            # medications, and supply items are stored.
            for deet in ord['detail']:
                if deet['type'] == "Lab" or "Procedure" or "PROC":
                    procedure = Procedure(name=deet['name'], type=deet['type'])

                    for id in deet['identifier']:
                        procedure.add_identifier(label=id['label'], system=id['system'], value=id['value'])

                    order.detail.append(procedure)

            orders_list.append(order)

        return orders_list

    def create_problem_list_from_json(self, json_problem_list):
        problem_list = []

        for prob in json_problem_list:
            condition = Condition()
            condition.isChronic = prob['isChronic']
            condition.isPrinciple = prob['isPrinciple']
            condition.encounter = prob['encounter']
            condition.isHospital = prob['isHospital']
            condition.isPOA = prob['isPOA']
            condition.customer_id = prob['customer_id']
            for id in prob['identifier']:
                condition.identifier.append(Identifier(label=id['label'], system=id['system'], value=id['value']))

            problem_list.append(condition)

        return problem_list

    def get_encounter_orders(self):
        orders_list = []

        for sec in self.section:
            if sec.title == "Encounter Orders":
                for ord in sec.content:
                    orders_list.append(ord)
        return orders_list

    def get_proc_supply_details(self, order):
        proc_supply_list = []
        for detail in order.detail:
            if detail.type == "Lab" or "Procedure" or "PROC":
                for id in detail.identifier:
                    if id.system == "clientEMR" and id.label == "Internal" or id.label == "maven" or id.label == "CPT4":
                        proc_supply_list.append([id.value, detail.name])
        return proc_supply_list

    def get_encounter_problem_list(self):
        problem_list = []

        for sec in self.section:
            if sec.title == "Problem List":
                for problem in sec.content:
                    problem_list.append(problem)

        return problem_list

    def get_encounter_dx_codes(self):
        """
        Returns the encounter diagnoses as a list of ICD-9 codes
        """
        problem_list = self.get_encounter_problem_list()
        problem_list_codes_IDs = []

        for problem in problem_list:
            for id in problem.identifier:
                problem_list_codes_IDs.append(id.value)

        return problem_list_codes_IDs

    def get_encounter_meds(self):
        raise NotImplementedError

    def get_alerts_section(self):
        """
        Returns the "Maven Alerts" section of the composition. If no alerts section is found, then it generates an empty section
        and returns that.
        """
        for sec in self.section:
            if sec.title == "Maven Alerts":
                return sec

        alerts_section = Section(title="Maven Alerts", content=[])
        self.section.append(alerts_section)

        return alerts_section

    def get_encounter_cost_breakdown(self):
        """
        Returns the "Encounter Cost Breakdown" section of the composition
        """

        for sec in self.section:
            if sec.title == "Encounter Cost Breakdown":
                return sec

        return None


class Patient(Resource):
    """
    :param name: List of HumanName objects
    :param identifier: List of Identifier() objects
    :param birthDate:
    """

    def __init__(self, name=None, identifier=None, birthDate=None, gender=None, address=None, problem_list=None):
        Resource.__init__(self, identifier=identifier)
        if name is None:
            self.name = []
        self.resourceType = "Patient"
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

    def get_current_pcp(self):
        #TODO add for loop to look up current pcp
        return "304923812"

    def add_name(self, given, family, use=None, text=None, prefix=None, suffix=None, period=None):
        self.name.append(HumanName(use=use,
                                   text=text,
                                   family=family,
                                   given=given,
                                   prefix=prefix,
                                   suffix=suffix,
                                   period=period))

    def get_name(self):
        """
        Returns patient name in format "lastname, firstname"
        """
        return self.name[0].family[0] + ", " + self.name[0].given[0]

    def get_birth_month(self):
        return self.birthDate.strftime('%m')

    def set_birth_date(self, datetime):
        self.birthDate = datetime

    def get_pat_id(self):
        for id in self.identifier:
            if id.label == "Internal" and id.system == "clientEMR":
                return id.value

    def get_mrn(self):
        return "b59145f2b2d411e398360800275923d2"
        #for id in self.identifier:
            #if id.label == "MRN" and id.system == "clientEMR":
                #return id.value


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
        #OrganizationType = enumerate('prov', 'dept', 'icu', 'team', 'fed', 'ins', 'edu', 'reli', 'pharm')
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

    def get_csn(self):
        for id in self.identifier:
            if id.system == "clientEMR" and id.label == "Internal":
                return id.value

    def get_prov_id(self):
        for participant in self.participant:
            for id in participant.identifier:
                if id.system == "clientEMR" and id.label == "Internal":
                    return id.value


class Procedure(Resource):

    def __init__(self, patient=None, encounter=None, period=None,
                 performer=None, followUp=None, type=None,
                 name=None, cost=None):
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
        self.name = name
        self.cost = cost


class Order(Resource):

    def __init__(self, date=None, patient=None, practitioner=None, detail=None, when=None, totalCost=None, text=None):
        Resource.__init__(self, text=text)
        self.date = date
        self.subject = patient
        self.patient = patient
        self.source = practitioner
        self.practitioner = practitioner
        self.target = None
        self.totalCost = totalCost

        if detail is None:
            self.detail = []
        else:
            self.detail = detail

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

    def __init__(self, customer_id, category=None, status=None, subject=None, author=None, provider_id=None, encounter_id=None,
                 code_trigger=None, sleuth_rule=None, alert_datetime=None, short_title=None, long_title=None,
                 tag_line=None, description=None, override_indications=None, outcome=None, saving=None):
        Resource.__init__(self, customer_id=customer_id)
        self.category = category
        self.status = status
        self.subject = subject
        self.author = author
        self.note = ""
        self.provider_id = provider_id
        self.encounter_id = encounter_id
        self.code_trigger = code_trigger
        self.sleuth_rule = sleuth_rule
        self.alert_datetime = alert_datetime
        self.short_title = short_title
        self.long_title = long_title
        self.tag_line = tag_line
        self.description = description
        if override_indications is None:
            self.override_indications = []
        else:
            self.override_indications = override_indications
        self.outcome = outcome
        self.saving = saving


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

    def get_problem_ID(self):
        for id in self.identifier:
            if id.label == "ICD":
                return id


class Location(Resource):

    def __init__(self, name=None, description=None, type=None,
                 telecom=None, address=None, managingOrganization=None,
                 status=None, partOf=None, mode=None, customer_id=None):
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
        self.customer_id = customer_id


class SecurityEvent(Resource):

    def __init__(self, source, participant, object=None, type=None, subtype=None, action=None, dateTime=None, outcome=None,
                 outcomeDesc=None):
        Resource.__init__(self)
        self.source = source
        if participant is None:
            self.participant = []
        if object is None:
            self.object = []
        self.type = type
        self.subtype = subtype
        self.action = action
        self.dateTime = dateTime
        self.outcome = outcome
        self.outcomeDesc = outcomeDesc



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


def jdefault(o):
    if isinstance(o, datetime.datetime):
        return datetime.datetime.isoformat(o)
    elif hasattr(o, 'hex'):
        return o.hex
    else:
        if hasattr(o, '__dict__') and o is not None:
            return o.__dict__


##################################################################
#CUSTOM MAVEN FHIR OBJECTS PROBABLY NOT FHIR-SERVER COMPATIBLE
##################################################################
class Rule(Resource):

    def __init__(self, customer_id=None, rule_id=None, code_trigger=None, code_trigger_type=None, dep_id=None, name=None, tag_line=None, description=None, rule_details=None):
        Resource.__init__(self, customer_id=customer_id)
        self.sleuth_rule_id = rule_id
        self.code_trigger = code_trigger
        self.code_trigger_type = code_trigger_type
        self.dep_id = dep_id
        self.name = name
        self.tag_line = tag_line
        self.description = description
        self.rule_details = rule_details['details']
        self.encounter_dx_rules = []
        self.historic_dx_rules = []
        self.encounter_proc_rules = []
        self.historic_proc_rules = []
        self.lab_rules = []
        self.drug_list_rules = []

        #extract the rule_details JSON object into respective lists of each type
        self.extract_rule_details(self.rule_details)

    def extract_rule_details(self, rule_details):
        """
        Takes the rule_details JSON object and creates lists of each respective type of rule

        :param rule_details: JSON object of rule details as defined on the wiki (https://mavenmedical.atlassian.net/wiki/display/MAV/Rule+Structure)
        """

        for rule_detail in rule_details:

            if rule_detail['type'] == "encounter_dx":
                self.encounter_dx_rules.append(rule_detail)

            elif rule_detail['type'] == "historic_dx":
                self.historic_dx_rules.append(rule_detail)

            elif rule_detail['type'] == "encounter_proc":
                self.encounter_proc_rules.append(rule_detail)

            elif rule_detail['type'] == "lab":
                self.lab_rules.append(rule_detail)

            elif rule_detail['type'] == "drug_list":
                self.drug_list_rules.append(rule_detail)
