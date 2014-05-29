#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:   This FHIR Python Object API was automatically generated from JSON examples
#               provided by HL7 FHIR Working Group.
#
#
#
#************************
#ASSUMES:
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-
#*************************************************************************
import uuid
import datetime
import dateutil.parser
import itertools
from utils.api.pyfhir.pyfhir_datatypes_generated import *


class Resource():

    def __init__(self, customer_id=None, name_space=None, id=None, versionId=1, lastModifiedDate=None, identifier=None, text=None, resourceType=None):
        self.customer_id = customer_id
        self.name_space = name_space
        if id is None:
            self.id = uuid.uuid1()
        if versionId is None:
            self.version_id = versionId
        if lastModifiedDate is None:
            self.lastModifiedDate = datetime.datetime.now()
        self.resourceType = resourceType

        if text is None:
            self.text = ""
        if identifier is None:
            self.identifier = []

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

def jdefault(o):
    if o is None:
        return "None"
    elif isinstance(o, datetime.datetime):
        return datetime.datetime.isoformat(o)
    elif hasattr(o, 'hex'):
        return o.hex
    else:
        if hasattr(o, '__dict__') and o is not None:
            return o.__dict__


class Bundle(Resource):

    def __init__(self,
        customer_id=None,
        name_space=None,
        identifier=None,
        versionId=None,
        resourceType="Bundle",
        title=None,
        lastModifiedDate=None,
        id=None,
        link=None,
        category=None,
        entry=None,
        totalResults=None):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          versionId=versionId,
                          id=id,
                          resourceType=resourceType,
                          lastModifiedDate=lastModifiedDate)
        self.title = title
        self.link = link
        self.category = category
        self.totalResults = totalResults

        if entry is None:
            self.entry = []
        if category is None:
            self.category = []

class AdverseReaction(Resource):
    """
    Short Description: Specific reactions to a substance

    Formal Description: Records an unexpected reaction suspected to be related to the exposure of the reaction subject to a substance.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param date: The date (and possibly time) when the reaction began.
    :param subject: The subject of the adverse reaction.
    :param didNotOccurFlag: If true, indicates that no reaction occurred.
    :param recorder: Identifies the individual responsible for the information in the reaction record.
    :param symptom_code: Indicates the specific sign or symptom that was observed.
    :param symptom_severity: The severity of the sign or symptom.
    :param exposure_date: Identifies the initial date of the exposure that is suspected to be related to the reaction.
    :param exposure_type: The type of exposure: Drug Administration, Immunization, Coincidental.
    :param exposure_causalityExpectation: A statement of how confident that the recorder was that this exposure caused the reaction.
    :param exposure_substance: Substance that is presumed to have caused the adverse reaction.
    
    :param symptom: The signs and symptoms that were observed as part of the reaction.
    :param exposure: An exposure to a substance that preceded a reaction occurrence.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="AdverseReaction",
                 text=None,
                 date=None,
                 subject=None,
                 didNotOccurFlag=None,
                 recorder=None,
                 symptom_code=None,
                 symptom_severity=None,
                 exposure_date=None,
                 exposure_type=None,
                 exposure_causalityExpectation=None,
                 exposure_substance=None,
                 symptom=None,
                 exposure=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.date = date                                     # , When the reaction occurred
        self.subject = subject                                     # , Who had the reaction
        self.didNotOccurFlag = didNotOccurFlag                                     # , Indicates lack of reaction
        self.recorder = recorder                                     # , Who recorded the reaction
        self.symptom_code = symptom_code                                     # , E.g. Rash, vomiting
        self.symptom_severity = symptom_severity                                     # , severe | serious | moderate | minor
        self.exposure_date = exposure_date                                     # , When the exposure occurred
        self.exposure_type = exposure_type                                     # , drugadmin | immuniz | coincidental
        self.exposure_causalityExpectation = exposure_causalityExpectation                                     # , likely | unlikely | confirmed | unknown
        self.exposure_substance = exposure_substance                                     # , Presumed causative substance
        
        if symptom is None:
            self.symptom = []                                     # , { attb['short_desc'] }}
        if exposure is None:
            self.exposure = []                                     # , { attb['short_desc'] }}
        

class Alert(Resource):
    """
    Short Description: Key information to flag to healthcare providers

    Formal Description: Prospective warnings of potential issues when providing care to the patient.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param category: Allows an alert to be divided into different categories like clinical, administrative etc.
    :param status: Supports basic workflow.
    :param subject: The person who this alert concerns.
    :param author: The person or device that created the alert.
    :param note: The textual component of the alert to display to the user.
    
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Alert",
                 text=None,
                 category=None,
                 status=None,
                 subject=None,
                 author=None,
                 note=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.category = category                                     # , Clinical, administrative, etc.
        self.status = status                                     # , active | inactive | entered in error
        self.subject = subject                                     # , Who is alert about?
        self.author = author                                     # , Alert creator
        self.note = note                                     # , Text of alert
        
        

class AllergyIntolerance(Resource):
    """
    Short Description: Drug, food, environmental and others

    Formal Description: Indicates the patient has a susceptibility to an adverse reaction upon exposure to a specified substance.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param criticality: Criticality of the sensitivity.
    :param sensitivityType: Type of the sensitivity.
    :param recordedDate: Date when the sensitivity was recorded.
    :param status: Status of the sensitivity.
    :param subject: The patient who has the allergy or intolerance.
    :param recorder: Indicates who has responsibility for the record.
    :param substance: The substance that causes the sensitivity.
    
    :param reaction: Reactions associated with the sensitivity.
    :param sensitivityTest: Observations that confirm or refute the sensitivity.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="AllergyIntolerance",
                 text=None,
                 criticality=None,
                 sensitivityType=None,
                 recordedDate=None,
                 status=None,
                 subject=None,
                 recorder=None,
                 substance=None,
                 reaction=None,
                 sensitivityTest=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.criticality = criticality                                     # , fatal | high | medium | low
        self.sensitivityType = sensitivityType                                     # , allergy | intolerance | unknown
        self.recordedDate = recordedDate                                     # , When recorded
        self.status = status                                     # , suspected | confirmed | refuted | resolved
        self.subject = subject                                     # , Who the sensitivity is for
        self.recorder = recorder                                     # , Who recorded the sensitivity
        self.substance = substance                                     # , The substance that causes the sensitivity
        
        if reaction is None:
            self.reaction = []                                     # , { attb['short_desc'] }}
        if sensitivityTest is None:
            self.sensitivityTest = []                                     # , { attb['short_desc'] }}
        

class CarePlan(Resource):
    """
    Short Description: Healthcare plan for patient

    Formal Description: Describes the intention of how one or more practitioners intend to deliver care for a particular patient for a period of time, possibly limited to care for a specific condition or set of conditions.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param patient: Identifies the patient/subject whose intended care is described by the plan.
    :param status: Indicates whether the plan is currently being acted upon, represents future intentions or is now just historical record.
    :param period: Indicates when the plan did (or is intended to) come into effect and end.
    :param modified: Identifies the most recent date on which the plan has been revised.
    :param participant_role: Indicates specific responsibility of an individual within the care plan.  E.g. "Primary physician", "Team coordinator", "Caregiver", etc.
    :param participant_member: The specific person or organization who is participating/expected to participate in the care plan.
    :param goal_description: Human-readable description of a specific desired objective of the care plan.
    :param goal_status: Indicates whether the goal has been reached and is still considered relevant.
    :param goal_notes: Any comments related to the goal.
    :param activity_status: Identifies what progress is being made for the specific activity.
    :param activity_prohibited: If true, indicates that the described activity is one that must NOT be engaged in when following the plan.
    :param activity_notes: Notes about the execution of the activity.
    :param activity_detail: The details of the proposed activity represented in a specific resource.
    :param activity_simple: A simple summary of details suitable for a general care plan system (e.g. form driven) that doesn't know about specific resources such as procedure etc.
    :param activity_simple_category: High-level categorization of the type of activity in a care plan.
    :param activity_simple_code: Detailed description of the type of activity.  E.g. What lab test, what procedure, what kind of encounter.
    :param activity_simple_timing: The period, timing or frequency upon which the described activity is to occur.
    :param activity_simple_location: Identifies the facility where the activity will occur.  E.g. home, hospital, specific clinic, etc.
    :param activity_simple_product: Identifies the food, drug or other product being consumed or supplied in the activity.
    :param activity_simple_dailyAmount: Identifies the quantity expected to be consumed in a given day.
    :param activity_simple_quantity: Identifies the quantity expected to be supplied.
    :param activity_simple_details: This provides a textual description of constraints on the activity occurrence, including relation to other activities.  It may also include objectives, pre-conditions and end-conditions.  Finally, it may convey specifics about the activity such as body site, method, route, etc.
    :param notes: General notes about the care plan not covered elsewhere.
    
    :param concern: Identifies the conditions/problems/concerns/diagnoses/etc. whose management and/or mitigation are handled by this plan.
    :param participant: Identifies all people and organizations who are expected to be involved in the care envisioned by this plan.
    :param goal: Describes the intended objective(s) of carrying out the Care Plan.
    :param goal_concern: The identified conditions that this goal relates to - the condition that caused it to be created, or that it is intended to address.
    :param activity: Identifies a planned action to occur as part of the plan.  For example, a medication to be used, lab tests to perform, self-monitoring, education, etc.
    :param activity_goal: Internal reference that identifies the goals that this activity is intended to contribute towards meeting.
    :param activity_actionResulting: Resources that describe follow-on actions resulting from the plan, such as drug prescriptions, encounter records, appointments, etc.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="CarePlan",
                 text=None,
                 patient=None,
                 status=None,
                 period=None,
                 modified=None,
                 participant_role=None,
                 participant_member=None,
                 goal_description=None,
                 goal_status=None,
                 goal_notes=None,
                 activity_status=None,
                 activity_prohibited=None,
                 activity_notes=None,
                 activity_detail=None,
                 activity_simple=None,
                 activity_simple_category=None,
                 activity_simple_code=None,
                 activity_simple_timing=None,
                 activity_simple_location=None,
                 activity_simple_product=None,
                 activity_simple_dailyAmount=None,
                 activity_simple_quantity=None,
                 activity_simple_details=None,
                 notes=None,
                 concern=None,
                 participant=None,
                 goal=None,
                 goal_concern=None,
                 activity=None,
                 activity_goal=None,
                 activity_actionResulting=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.patient = patient                                     # , Who care plan is for
        self.status = status                                     # , planned | active | completed
        self.period = period                                     # , Time period plan covers
        self.modified = modified                                     # , When last updated
        self.participant_role = participant_role                                     # , Type of involvement
        self.participant_member = participant_member                                     # , Who is involved
        self.goal_description = goal_description                                     # , What's the desired outcome?
        self.goal_status = goal_status                                     # , in progress | achieved | sustaining | cancelled
        self.goal_notes = goal_notes                                     # , Comments about the goal
        self.activity_status = activity_status                                     # , not started | scheduled | in progress | on hold | completed | cancelled
        self.activity_prohibited = activity_prohibited                                     # , Do NOT do
        self.activity_notes = activity_notes                                     # , Comments about the activity
        self.activity_detail = activity_detail                                     # , Activity details defined in specific resource
        self.activity_simple = activity_simple                                     # , Activity details summarised here
        self.activity_simple_category = activity_simple_category                                     # , diet | drug | encounter | observation | procedure | supply | other
        self.activity_simple_code = activity_simple_code                                     # , Detail type of activity
        self.activity_simple_timing = activity_simple_timing                                     # , When activity is to occur
        self.activity_simple_location = activity_simple_location                                     # , Where it should happen
        self.activity_simple_product = activity_simple_product                                     # , What's administered/supplied
        self.activity_simple_dailyAmount = activity_simple_dailyAmount                                     # , How much consumed/day?
        self.activity_simple_quantity = activity_simple_quantity                                     # , How much is administered/supplied/consumed
        self.activity_simple_details = activity_simple_details                                     # , Extra info on activity occurrence
        self.notes = notes                                     # , Comments about the plan
        
        if concern is None:
            self.concern = []                                     # , { attb['short_desc'] }}
        if participant is None:
            self.participant = []                                     # , { attb['short_desc'] }}
        if goal is None:
            self.goal = []                                     # , { attb['short_desc'] }}
        if goal_concern is None:
            self.goal_concern = []                                     # , { attb['short_desc'] }}
        if activity is None:
            self.activity = []                                     # , { attb['short_desc'] }}
        if activity_goal is None:
            self.activity_goal = []                                     # , { attb['short_desc'] }}
        if activity_actionResulting is None:
            self.activity_actionResulting = []                                     # , { attb['short_desc'] }}


class Section():

    def __init__(self, title=None, code=None, subject=None, content=None):
        self.title = title
        self.code = code
        self.subject = subject
        self.content = content
        

class Composition(Resource):
    """
    Short Description: A set of resources composed into a single coherent clinical statement with clinical attestation

    Formal Description: A set of healthcare-related information that is assembled together into a single logical document that provides a single coherent statement of meaning, establishes its own context and that has clinical attestation with regard to who is making the statement.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param date: The composition editing time, when the composition was last logically changed by the author.
    :param type: Specifies the particular kind of composition (e.g. History and Physical, Discharge Summary, Progress Note). This usually equates to the purpose of making the composition.
    :param fhir_class: A categorization for the type of the composition. This may be implied by or derived from the code specified in the Composition Type.
    :param title: Official human-readable label for the composition.
    :param status: The workflow/clinical status of this composition. The status is a marker for the clinical standing of the document.
    :param confidentiality: The code specifying the level of confidentiality of the Composition.
    :param subject: Who or what the composition is about. The composition can be about a person, (patient or healthcare practitioner), a device (I.e. machine) or even a group of subjects (such as a document about a herd of livestock, or a set of patients that share a common exposure).
    :param attester_time: When composition was attested by the party.
    :param attester_party: Who attested the composition in the specified way.
    :param custodian: Identifies the organization or group who is responsible for ongoing maintenance of and access to the composition/document information.
    :param event: The main event/act/item, such as a colonoscopy or an appendectomy, being documented.
    :param event_period: The period of time covered by the documentation. There is no assertion that the documentation is a complete representation for this period, only that it documents events during this time.
    :param encounter: Describes the clinical encounter or type of care this documentation is associated with.
    :param section_title: The heading for this particular section.  This will be part of the rendered content for the document.
    :param section_code: A code identifying the kind of content contained within the section.
    :param section_subject: Identifies the primary subject of the section.
    :param section_content: Identifies the discrete data that provides the content for the section.
    
    :param author: Identifies who is responsible for the information in the composition.  (Not necessarily who typed it in.).
    :param attester: A participant who has attested to the accuracy of the composition/document.
    :param attester_mode: The type of attestation the authenticator offers.
    :param event_code: This list of codes represents the main clinical acts, such as a colonoscopy or an appendectomy, being documented. In some cases, the event is inherent in the typeCode, such as a "History and Physical Report" in which the procedure being documented is necessarily a "History and Physical" act.
    :param event_detail: Full details for the event(s) the composition/documentation consents.
    :param section: The root of the sections that make up the composition.
    :param section_section: A nested sub-section within this section.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Composition",
                 text=None,
                 date=None,
                 type=None,
                 fhir_class=None,
                 title=None,
                 status=None,
                 confidentiality=None,
                 subject=None,
                 attester_time=None,
                 attester_party=None,
                 custodian=None,
                 event=None,
                 event_period=None,
                 encounter=None,
                 section_title=None,
                 section_code=None,
                 section_subject=None,
                 section_content=None,
                 author=None,
                 attester=None,
                 attester_mode=None,
                 event_code=None,
                 event_detail=None,
                 section=None,
                 section_section=None,
                 write_key=None
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.date = date                                     # , Composition editing time
        self.type = type                                     # , Kind of composition (LOINC if possible)
        self.fhir_class = fhir_class                                     # , Categorization of Composition
        self.title = title                                     # , Human Readable name/title
        self.status = status                                     # , preliminary | final | appended | amended | entered in error
        self.confidentiality = confidentiality                                     # , As defined by affinity domain
        self.subject = subject                                     # , Who and/or what the composition is about
        self.attester_time = attester_time                                     # , When composition attested
        self.attester_party = attester_party                                     # , Who attested the composition
        self.custodian = custodian                                     # , Org which maintains the composition
        self.event = event                                     # , The clinical event/act/item being documented
        self.event_period = event_period                                     # , The period covered by the documentation
        self.encounter = encounter                                     # , Context of the conposition
        self.section_title = section_title                                     # , Label for section
        self.section_code = section_code                                     # , Classification of section (recommended)
        self.section_subject = section_subject                                     # , If section different to composition
        self.section_content = section_content                                     # , The actual data for the section
        self.write_key = write_key
        
        if author is None:
            self.author = []                                     # , { attb['short_desc'] }}
        if attester is None:
            self.attester = []                                     # , { attb['short_desc'] }}
        if attester_mode is None:
            self.attester_mode = []                                     # , { attb['short_desc'] }}
        if event_code is None:
            self.event_code = []                                     # , { attb['short_desc'] }}
        if event_detail is None:
            self.event_detail = []                                     # , { attb['short_desc'] }}
        if section is None:
            self.section = []                                     # , { attb['short_desc'] }}
        if section_section is None:
            self.section_section = []                                     # , { attb['short_desc'] }}
        
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
        enc_orders_section = self.get_section_by_coding("http://loinc.org", "46209-3")
        return enc_orders_section.content

    def get_section_by_coding(self, code_system, code_value):
        for sec in self.section:
            for coding in sec.code.coding:
                if coding.system == code_system and coding.code == code_value:
                    return sec

    def get_proc_supply_details(self, order):
        proc_supply_list = []
        for detail in order.detail:
            #TODO - Hardcoded array index look-up will need to change in order to accommodate multiple charges per order
            if detail.resourceType == "Lab" or "Procedure" or "PROC":
                for code in detail.type.coding:
                    if code.system == "clientEMR" or "maven" or "CPT4":
                        proc_supply_list.append([code.code, code.system])

            elif detail.resourceType == "Med" or "Medication":
                for code in detail.type.coding:
                    if code.system == "clientEMR" or "maven" or "NDC":
                        proc_supply_list.append([code.code, code.system])
                        
        return proc_supply_list

    def _get_proc_supply_details(self, order):
        proc_supply_list = []
        for detail in order.detail:
            print()
            pass

    def get_encounter_conditions(self):
        enc_conditions_section = self.get_section_by_coding("http://loinc.org", "11450-4")
        return enc_conditions_section.content

    def get_encounter_dx_codes(self):

        problem_list_codes_IDs = []
        for condition in self.get_encounter_conditions():
            for coding in condition.code.coding:
                problem_list_codes_IDs.append(coding.code)

        return problem_list_codes_IDs

    def get_encounter_meds(self):
        raise NotImplementedError

    def get_alerts_section(self):
        for sec in self.section:
            if sec.title == "Maven Alerts":
                return sec

        alerts_section = Section(title="Maven Alerts", content=[])
        self.section.append(alerts_section)

        return alerts_section

    def get_encounter_cost_breakdown(self):
        for sec in self.section:
            if sec.title == "Encounter Cost Breakdown":
                return sec

        return None

    def get_author_id(self):
        for id in self.author.identifier:
            if id.system == "clientEMR":
                return id.value


class ConceptMap(Resource):
    """
    Short Description: A statement of relationships from one set of concepts to one or more other concept systems

    Formal Description: A statement of relationships from one set of concepts to one or more other concept systems.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param version: The identifier that is used to identify this version of the concept map when it is referenced in a specification, model, design or instance. This is an arbitrary value managed by the profile author manually and the value should be a timestamp.
    :param name: A free text natural language name describing the concept map.
    :param publisher: The name of the individual or organization that published the concept map.
    :param description: A free text natural language description of the use of the concept map - reason for definition, conditions of use, etc.
    :param copyright: A copyright statement relating to the concept map and/or its contents.
    :param status: The status of the concept map.
    :param experimental: This ConceptMap was authored for testing purposes (or education/evaluation/marketing), and is not intended to be used for genuine usage.
    :param date: The date that the concept map status was last changed.
    :param source: The source value set that specifies the concepts that are being mapped.
    :param target: The target value set provides context to the mappings. Note that the mapping is made between concepts, not between value sets, but the value set provides important context about how the concept mapping choices are made.
    :param concept_system: System that defines the concept being mapped.
    :param concept_code: Identifies concept being mapped.
    :param concept_dependsOn_concept: A reference to a specific concept that holds a coded value. This can be an element in a FHIR resource, or a specific reference to a data element in a different specification (e.g. v2) or a general reference to a kind of data field, or a reference to a value set with an appropriately narrow definition.
    :param concept_dependsOn_system: System for a concept in the referenced concept.
    :param concept_dependsOn_code: Code for a concept in the referenced concept.
    :param concept_map_system: System of the target.
    :param concept_map_code: Code that identifies the target concept.
    :param concept_map_equivalence: equal | equivalent | wider | subsumes | narrower | specialises | inexact | unmatched | disjoint.
    :param concept_map_comments: Description of status/issues in mapping.
    
    :param telecom: Contacts of the publisher to assist a user in finding and communicating with the publisher.
    :param concept: Mappings for a concept from the source valueset.
    :param concept_dependsOn: A set of additional dependencies for this mapping to hold. This mapping is only applicable if the specified concept can be resolved, and it has the specified value.
    :param concept_map: A concept from the target value set that this concept maps to.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="ConceptMap",
                 text=None,
                 version=None,
                 name=None,
                 publisher=None,
                 description=None,
                 copyright=None,
                 status=None,
                 experimental=None,
                 date=None,
                 source=None,
                 target=None,
                 concept_system=None,
                 concept_code=None,
                 concept_dependsOn_concept=None,
                 concept_dependsOn_system=None,
                 concept_dependsOn_code=None,
                 concept_map_system=None,
                 concept_map_code=None,
                 concept_map_equivalence=None,
                 concept_map_comments=None,
                 telecom=None,
                 concept=None,
                 concept_dependsOn=None,
                 concept_map=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.version = version                                     # , Logical id for this version of the concept map
        self.name = name                                     # , Informal name for this concept map
        self.publisher = publisher                                     # , Name of the publisher (Organization or individual)
        self.description = description                                     # , Human language description of the concept map
        self.copyright = copyright                                     # , About the concept map or its content
        self.status = status                                     # , draft | active | retired
        self.experimental = experimental                                     # , If for testing purposes, not real usage
        self.date = date                                     # , Date for given status
        self.source = source                                     # , Identifies the source value set which is being mapped
        self.target = target                                     # , Provides context to the mappings
        self.concept_system = concept_system                                     # , System that defines the concept being mapped
        self.concept_code = concept_code                                     # , Identifies concept being mapped
        self.concept_dependsOn_concept = concept_dependsOn_concept                                     # , Reference to element/field/valueset provides the context
        self.concept_dependsOn_system = concept_dependsOn_system                                     # , System for a concept in the referenced concept
        self.concept_dependsOn_code = concept_dependsOn_code                                     # , Code for a concept in the referenced concept
        self.concept_map_system = concept_map_system                                     # , System of the target
        self.concept_map_code = concept_map_code                                     # , Code that identifies the target concept
        self.concept_map_equivalence = concept_map_equivalence                                     # , equal | equivalent | wider | subsumes | narrower | specialises | inexact | unmatched | disjoint
        self.concept_map_comments = concept_map_comments                                     # , Description of status/issues in mapping
        
        if telecom is None:
            self.telecom = []                                     # , { attb['short_desc'] }}
        if concept is None:
            self.concept = []                                     # , { attb['short_desc'] }}
        if concept_dependsOn is None:
            self.concept_dependsOn = []                                     # , { attb['short_desc'] }}
        if concept_map is None:
            self.concept_map = []                                     # , { attb['short_desc'] }}
        

class Condition(Resource):
    """
    Short Description: Detailed information about conditions, problems or diagnoses

    Formal Description: Use to record detailed information about conditions, problems or diagnoses recognized by a clinician. There are many uses including: recording a Diagnosis during an Encounter; populating a problem List or a Summary Statement, such as a Discharge Summary.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param subject: Indicates the patient who the condition record is associated with.
    :param encounter: Encounter during which the condition was first asserted.
    :param asserter: Person who takes responsibility for asserting the existence of the condition as part of the electronic record.
    :param dateAsserted: Estimated or actual date the condition/problem/diagnosis was first detected/suspected.
    :param code: Identification of the condition, problem or diagnosis.
    :param category: A category assigned to the condition. E.g. complaint | symptom | finding | diagnosis.
    :param status: The clinical status of the condition.
    :param certainty: The degree of confidence that this condition is correct.
    :param severity: A subjective assessment of the severity of the condition as evaluated by the clinician.
    :param onsetdate: Estimated or actual date the condition began, in the opinion of the clinician.
    :param onsetAge: Estimated or actual date the condition began, in the opinion of the clinician.
    :param onset: Estimated or actual date the condition began, in the opinion of the clinician.
    :param abatementdate: The date or estimated date that the condition resolved or went into remission. This is called "abatement" because of the many overloaded connotations associated with "remission" or "resolution" - Conditions are never really resolved, but they can abate.
    :param abatementAge: The date or estimated date that the condition resolved or went into remission. This is called "abatement" because of the many overloaded connotations associated with "remission" or "resolution" - Conditions are never really resolved, but they can abate.
    :param abatementboolean: The date or estimated date that the condition resolved or went into remission. This is called "abatement" because of the many overloaded connotations associated with "remission" or "resolution" - Conditions are never really resolved, but they can abate.
    :param abatement: The date or estimated date that the condition resolved or went into remission. This is called "abatement" because of the many overloaded connotations associated with "remission" or "resolution" - Conditions are never really resolved, but they can abate.
    :param stage: Clinical stage or grade of a condition. May include formal severity assessments.
    :param stage_summary: A simple summary of the stage such as "Stage 3". The determination of the stage is disease-specific.
    :param evidence_code: A manifestation or symptom that led to the recording of this condition.
    :param location_code: Code that identifies the structural location.
    :param location_detail: Detailed anatomical location information.
    :param relatedItem_type: The type of relationship that this condition has to the related item.
    :param relatedItem_code: Code that identifies the target of this relationship. The code takes the place of a detailed instance target.
    :param relatedItem_target: Target of the relationship.
    :param notes: Additional information about the Condition. This is a general notes/comments entry  for description of the Condition, its diagnosis and prognosis.
    
    :param stage_assessment: Reference to a formal record of the evidence on which the staging assessment is based.
    :param evidence: Supporting Evidence / manifestations that are the basis on which this condition is suspected or confirmed.
    :param evidence_detail: Links to other relevant information, including pathology reports.
    :param location: The anatomical location where this condition manifests itself.
    :param relatedItem: Further conditions, problems, diagnoses, procedures or events that are related in some way to this condition, or the substance that caused/triggered this Condition.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Condition",
                 text=None,
                 subject=None,
                 encounter=None,
                 asserter=None,
                 dateAsserted=None,
                 code=None,
                 category=None,
                 status=None,
                 certainty=None,
                 severity=None,
                 onsetdate=None,
                 onsetAge=None,
                 onset=None,
                 abatementDate=None,
                 abatementAge=None,
                 abatementBoolean=False,
                 abatement=None,
                 stage=None,
                 stage_summary=None,
                 evidence_code=None,
                 location_code=None,
                 location_detail=None,
                 relatedItem_type=None,
                 relatedItem_code=None,
                 relatedItem_target=None,
                 notes=None,
                 stage_assessment=None,
                 evidence=None,
                 evidence_detail=None,
                 location=None,
                 relatedItem=None,
                 presentOnArrival=False,
                 isPrincipal=False
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.subject = subject                                     # , Who has the condition?
        self.encounter = encounter                                     # , Encounter when condition first asserted
        self.asserter = asserter                                     # , Person who asserts this condition
        self.dateAsserted = dateAsserted                                     # , When first detected/suspected/entered
        self.code = code                                     # , Identification of the condition, problem or diagnosis
        self.category = category                                     # , E.g. complaint | symptom | finding | diagnosis
        self.status = status                                     # , provisional | working | confirmed | refuted
        self.certainty = certainty                                     # , Degree of confidence
        self.severity = severity                                     # , Subjective severity of condition
        self.onsetdate = onsetdate                                     # date, Estimated or actual date, or age
        self.onsetAge = onsetAge                                     # Age, Estimated or actual date, or age
        self.onset = onset                                     # , Estimated or actual date, or age
        self.abatementDate = abatementDate                                     # date, If/when in resolution/remission
        self.abatementAge = abatementAge                                     # Age, If/when in resolution/remission
        self.abatementBoolean = abatementBoolean                                     # boolean, If/when in resolution/remission
        self.abatement = abatement                                     # , If/when in resolution/remission
        self.stage = stage                                     # , Stage/grade, usually assessed formally
        self.stage_summary = stage_summary                                     # , Simple summary (disease specific)
        self.evidence_code = evidence_code                                     # , Manifestation/symptom
        self.location_code = location_code                                     # , Location - may include laterality
        self.location_detail = location_detail                                     # , Precise location details
        self.relatedItem_type = relatedItem_type                                     # , due-to | following
        self.relatedItem_code = relatedItem_code                                     # , Relationship target by means of a predefined code
        self.relatedItem_target = relatedItem_target                                     # , Relationship target resource
        self.notes = notes                                     # , Additional information about the Condition
        self.presentOnArrival = presentOnArrival
        self.isPrincipal = isPrincipal
        
        if stage_assessment is None:
            self.stage_assessment = []                                     # , { attb['short_desc'] }}
        if evidence is None:
            self.evidence = []                                     # , { attb['short_desc'] }}
        if evidence_detail is None:
            self.evidence_detail = []                                     # , { attb['short_desc'] }}
        if location is None:
            self.location = []                                     # , { attb['short_desc'] }}
        if relatedItem is None:
            self.relatedItem = []                                     # , { attb['short_desc'] }}
        
    def get_ICD9_id(self):
        for coding in self.code.coding:
            if coding.system == "icd":
                return coding.code

    def get_snomed_id(self):
        for coding in self.code.coding:
            if coding.system == "":
                return coding.code


class Conformance(Resource):
    """
    Short Description: A conformance statement

    Formal Description: A conformance statement is a set of requirements for a desired implementation or a description of how a target application fulfills those requirements in a particular implementation.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param version: The identifier that is used to identify this version of the conformance statement when it is referenced in a specification, model, design or instance. This is an arbitrary value managed by the profile author manually and the value should be a timestamp.
    :param name: A free text natural language name identifying the conformance statement.
    :param publisher: Name of Organization publishing this conformance statement.
    :param description: A free text natural language description of the conformance statement and its use. Typically, this is used when the profile describes a desired rather than an actual solution, for example as a formal expression of requirements as part of an RFP.
    :param status: The status of this conformance statement.
    :param experimental: A flag to indicate that this conformance statement is authored for testing purposes (or education/evaluation/marketing), and is not intended to be used for genuine usage.
    :param date: The date when the conformance statement was published.
    :param software: Software that is covered by this conformance statement.  It is used when the profile describes the capabilities of a particular software version, independent of an installation.
    :param software_name: Name software is known by.
    :param software_version: The version identifier for the software covered by this statement.
    :param software_releaseDate: Date this version of the software released.
    :param implementation: Identifies a specific implementation instance that is described by the conformance statement - i.e. a particular installation, rather than the capabilities of a software program.
    :param implementation_description: Information about the specific installation that this conformance statement relates to.
    :param implementation_url: A base URL for the implementation.  This forms the base for REST interfaces as well as the mailbox and document interfaces.
    :param fhirVersion: The version of the FHIR specification on which this conformance statement is based.
    :param acceptUnknown: A flag that indicates whether the application accepts unknown elements as part of a resource.
    :param rest_mode: Identifies whether this portion of the statement is describing ability to initiate or receive restful operations.
    :param rest_documentation: Information about the system's restful capabilities that apply across all applications, such as security.
    :param rest_security: Information about security of implementation.
    :param rest_security_cors: Server adds CORS headers when responding to requests - this enables javascript applications to yuse the server.
    :param rest_security_description: General description of how security works.
    :param rest_resource_type: A type of resource exposed via the restful interface.
    :param rest_resource_profile: A specification of the profile that describes the solution's support for the resource, including any constraints on cardinality, bindings, lengths or other limitations.
    :param rest_resource_readHistory: A flag for whether the server is able to return past versions as part of the vRead operation.
    :param rest_resource_updateCreate: A flag to indicate that the server allows the client to create new identities on the server. If the update operation is used (client) or allowed (server) to a new location where a resource doesn't already exist. This means that the server allows the client to create new identities on the server.
    :param rest_operation_code: A coded identifier of the operation, supported by the system.
    :param rest_operation_documentation: Guidance specific to the implementation of this operation, such as limitations on the kind of transactions allowed, or information about system wide search is implemented.
    :param rest_query_name: The name of a query, which is used in the _query parameter when the query is called.
    :param rest_query_definition: Identifies the custom query, defined either in FHIR core or another profile.
    :param rest_query_documentation: Additional information about how the query functions in this particular implementation.
    :param messaging_endpoint: An address to which messages and/or replies are to be sent.
    :param messaging_reliableCache: Length if the receiver's reliable messaging cache (if a receiver) or how long the cache length on the receiver should be (if a sender).
    :param messaging_documentation: Documentation about the system's messaging capabilities for this endpoint not otherwise documented by the conformance statement.  For example, process for becoming an authorized messaging exchange partner.
    :param messaging_event_code: A coded identifier of a supported messaging event.
    :param messaging_event_category: The impact of the content of the message.
    :param messaging_event_mode: The mode of this event declaration - whether application is sender or receiver.
    :param messaging_event_focus: A resource associated with the event.  This is the resource that defines the event.
    :param messaging_event_request: Information about the request for this event.
    :param messaging_event_response: Information about the response for this event.
    :param messaging_event_documentation: Guidance on how this event is handled, such as internal system trigger points, business rules, etc.
    :param document_mode: Mode of this document declaration - whether application is producer or consumer.
    :param document_documentation: A description of how the application supports or uses the specified document profile.  For example, when are documents created, what action is taken with consumed documents, etc.
    :param document_profile: A constraint on a resource used in the document.
    
    :param telecom: Contacts for Organization relevant to this conformance statement.  The contacts may be a website, email, phone numbers, etc.
    :param format: A list of the formats supported by this implementation.
    :param profile: A list of profiles supported by the system. For a server, "supported by the system" means the system hosts/produces a set of recourses, conformant to a particular profile, and allows its clients to search using this profile and to find appropriate data. For a client, it means the system will search by this profile and process data according to the guidance implicit in the profile.
    :param rest: A definition of the restful capabilities of the solution, if any.
    :param rest_resource: A specification of the restful capabilities of the solution for a specific resource type.
    :param rest_operation: A specification of restful operations supported by the system.
    :param rest_query: Definition of a named query and its parameters and their meaning.
    :param rest_documentMailbo: A list of profiles that this server implements for accepting documents in the mailbox. If this list is empty, then documents are not accepted. The base specification has the profile identifier "http://hl7.org/pyfhir/documents/mailbox". Other specifications can declare their own identifier for this purpose.
    :param messaging: A description of the messaging capabilities of the solution.
    :param messaging_event: A description of the solution's support for an event at this end point.
    :param document: A document definition.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Conformance",
                 text=None,
                 version=None,
                 name=None,
                 publisher=None,
                 description=None,
                 status=None,
                 experimental=None,
                 date=None,
                 software=None,
                 software_name=None,
                 software_version=None,
                 software_releaseDate=None,
                 implementation=None,
                 implementation_description=None,
                 implementation_url=None,
                 fhirVersion=None,
                 acceptUnknown=None,
                 rest_mode=None,
                 rest_documentation=None,
                 rest_security=None,
                 rest_security_cors=None,
                 rest_security_description=None,
                 rest_resource_type=None,
                 rest_resource_profile=None,
                 rest_resource_readHistory=None,
                 rest_resource_updateCreate=None,
                 rest_operation_code=None,
                 rest_operation_documentation=None,
                 rest_query_name=None,
                 rest_query_definition=None,
                 rest_query_documentation=None,
                 messaging_endpoint=None,
                 messaging_reliableCache=None,
                 messaging_documentation=None,
                 messaging_event_code=None,
                 messaging_event_category=None,
                 messaging_event_mode=None,
                 messaging_event_focus=None,
                 messaging_event_request=None,
                 messaging_event_response=None,
                 messaging_event_documentation=None,
                 document_mode=None,
                 document_documentation=None,
                 document_profile=None,
                 telecom=None,
                 format=None,
                 profile=None,
                 rest=None,
                 rest_resource=None,
                 rest_operation=None,
                 rest_query=None,
                 rest_documentMailbo=None,
                 messaging=None,
                 messaging_event=None,
                 document=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.version = version                                     # , Logical id for this version of the statement
        self.name = name                                     # , Informal name for this conformance statement
        self.publisher = publisher                                     # , Publishing Organization
        self.description = description                                     # , Human description of the conformance statement
        self.status = status                                     # , draft | active | retired
        self.experimental = experimental                                     # , If for testing purposes, not real usage
        self.date = date                                     # , Publication Date
        self.software = software                                     # , Software that is covered by this conformance statement
        self.software_name = software_name                                     # , A name the software is known by
        self.software_version = software_version                                     # , Version covered by this statement
        self.software_releaseDate = software_releaseDate                                     # , Date this version released
        self.implementation = implementation                                     # , If this describes a specific instance
        self.implementation_description = implementation_description                                     # , Describes this specific instance
        self.implementation_url = implementation_url                                     # , Base URL for the installation
        self.fhirVersion = fhirVersion                                     # , FHIR Version
        self.acceptUnknown = acceptUnknown                                     # , True if application accepts unknown elements
        self.rest_mode = rest_mode                                     # , client | server
        self.rest_documentation = rest_documentation                                     # , General description of implementation
        self.rest_security = rest_security                                     # , Information about security of implementation
        self.rest_security_cors = rest_security_cors                                     # , Adds CORS Headers (http://enable-cors.org/)
        self.rest_security_description = rest_security_description                                     # , General description of how security works
        self.rest_resource_type = rest_resource_type                                     # , A resource type that is supported
        self.rest_resource_profile = rest_resource_profile                                     # , What structural features are supported
        self.rest_resource_readHistory = rest_resource_readHistory                                     # , Whether vRead can return past versions
        self.rest_resource_updateCreate = rest_resource_updateCreate                                     # , If allows/uses update to a new location
        self.rest_operation_code = rest_operation_code                                     # , transaction | search-system | history-system
        self.rest_operation_documentation = rest_operation_documentation                                     # , Anything special about operation behavior
        self.rest_query_name = rest_query_name                                     # , Special named queries (_query=)
        self.rest_query_definition = rest_query_definition                                     # , Where query is defined
        self.rest_query_documentation = rest_query_documentation                                     # , Additional usage guidance
        self.messaging_endpoint = messaging_endpoint                                     # , Actual endpoint being described
        self.messaging_reliableCache = messaging_reliableCache                                     # , Reliable Message Cache Length
        self.messaging_documentation = messaging_documentation                                     # , Messaging interface behavior details
        self.messaging_event_code = messaging_event_code                                     # , Event type
        self.messaging_event_category = messaging_event_category                                     # , Consequence | Currency | Notification
        self.messaging_event_mode = messaging_event_mode                                     # , sender | receiver
        self.messaging_event_focus = messaging_event_focus                                     # , Resource that's focus of message
        self.messaging_event_request = messaging_event_request                                     # , Profile that describes the request
        self.messaging_event_response = messaging_event_response                                     # , Profile that describes the response
        self.messaging_event_documentation = messaging_event_documentation                                     # , Endpoint-specific event documentation
        self.document_mode = document_mode                                     # , producer | consumer
        self.document_documentation = document_documentation                                     # , Description of document support
        self.document_profile = document_profile                                     # , Constraint on a resource used in the document
        
        if telecom is None:
            self.telecom = []                                     # , { attb['short_desc'] }}
        if format is None:
            self.format = []                                     # , { attb['short_desc'] }}
        if profile is None:
            self.profile = []                                     # , { attb['short_desc'] }}
        if rest is None:
            self.rest = []                                     # , { attb['short_desc'] }}
        if rest_resource is None:
            self.rest_resource = []                                     # , { attb['short_desc'] }}
        if rest_operation is None:
            self.rest_operation = []                                     # , { attb['short_desc'] }}
        if rest_query is None:
            self.rest_query = []                                     # , { attb['short_desc'] }}
        if rest_documentMailbo is None:
            self.rest_documentMailbo = []                                     # , { attb['short_desc'] }}
        if messaging is None:
            self.messaging = []                                     # , { attb['short_desc'] }}
        if messaging_event is None:
            self.messaging_event = []                                     # , { attb['short_desc'] }}
        if document is None:
            self.document = []                                     # , { attb['short_desc'] }}
        

class Device(Resource):
    """
    Short Description: An instance of a manufactured thing that is used in the provision of healthcare

    Formal Description: This resource identifies an instance of a manufactured thing that is used in the provision of healthcare without being substantially changed through that activity. The device may be a machine, an insert, a computer, an application, etc. This includes durable (reusable) medical equipment as well as disposable equipment used for diagnostic, treatment, and research for healthcare and public health.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param type: A kind of this device.
    :param manufacturer: A name of the manufacturer.
    :param model: The "model" - an identifier assigned by the manufacturer to identify the product by its type. This number is shared by the all devices sold as the same type.
    :param version: The version of the device, if the device has multiple releases under the same model, or if the device is software or carries firmware.
    :param expiry: Date of expiry of this device (if applicable).
    :param udi: FDA Mandated Unique Device Identifier. Use the human readable information (the content that the user sees, which is sometimes different to the exact syntax represented in the barcode)  - see http://www.fda.gov/MedicalDevices/DeviceRegulationandGuidance/UniqueDeviceIdentification/default.htm.
    :param lotNumber: Lot number assigned by the manufacturer.
    :param owner: An organization that is responsible for the provision and ongoing maintenance of the device.
    :param location: The resource may be found in a literal location (i.e. GPS coordinates), a logical place (i.e. "in/with the patient"), or a coded location.
    :param patient: Patient information, if the resource is affixed to a person.
    :param url: A network address on which the device may be contacted directly.
    
    :param contact: Contact details for an organization or a particular human that is responsible for the device.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Device",
                 text=None,
                 type=None,
                 manufacturer=None,
                 model=None,
                 version=None,
                 expiry=None,
                 udi=None,
                 lotNumber=None,
                 owner=None,
                 location=None,
                 patient=None,
                 url=None,
                 contact=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.type = type                                     # , What kind of device this is
        self.manufacturer = manufacturer                                     # , Name of device manufacturer
        self.model = model                                     # , Model id assigned by the manufacturer
        self.version = version                                     # , Version number (i.e. software)
        self.expiry = expiry                                     # , Date of expiry of this device (if applicable)
        self.udi = udi                                     # , FDA Mandated Unique Device Identifier
        self.lotNumber = lotNumber                                     # , Lot number of manufacture
        self.owner = owner                                     # , Organization responsible for device
        self.location = location                                     # , Where the resource is found
        self.patient = patient                                     # , If the resource is affixed to a person
        self.url = url                                     # , Network address to contact device
        
        if contact is None:
            self.contact = []                                     # , { attb['short_desc'] }}
        

class DeviceObservationReport(Resource):
    """
    Short Description: Describes the data produced by a device at a point in time

    Formal Description: Describes the data produced by a device at a point in time.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param instant: The point in time that the values are reported.
    :param source: Identification information for the device that is the source of the data.
    :param subject: The subject of the measurement.
    :param virtualDevice_code: Describes the compartment.
    :param virtualDevice_channel_code: Describes the channel.
    
    :param virtualDevice: A medical-related subsystem of a medical device.
    :param virtualDevice_channel: Groups together physiological measurement data and derived data.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="DeviceObservationReport",
                 text=None,
                 instant=None,
                 source=None,
                 subject=None,
                 virtualDevice_code=None,
                 virtualDevice_channel_code=None,
                 virtualDevice=None,
                 virtualDevice_channel=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.instant = instant                                     # , When the data values are reported
        self.source = source                                     # , Identifies/describes where the data came from
        self.subject = subject                                     # , Subject of the measurement
        self.virtualDevice_code = virtualDevice_code                                     # , Describes the compartment
        self.virtualDevice_channel_code = virtualDevice_channel_code                                     # , Describes the channel
        
        if virtualDevice is None:
            self.virtualDevice = []                                     # , { attb['short_desc'] }}
        if virtualDevice_channel is None:
            self.virtualDevice_channel = []                                     # , { attb['short_desc'] }}
        

class DiagnosticOrder(Resource):
    """
    Short Description: A request for a diagnostic service

    Formal Description: A request for a diagnostic investigation service to be performed.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param subject: Who or what the investigation is to be performed on. This is usually a human patient, but diagnostic tests can also be requested on animals, groups of humans or animals, devices such as dialysis machines, or even locations (typically for environmental scans).
    :param orderer: The practitioner that holds legal responsibility for ordering the investigation.
    :param encounter: An encounter that provides additional informaton about the healthcare context in which this request is made.
    :param clinicalNotes: An explanation or justification for why this diagnostic investigation is being requested.
    :param status: The status of the order.
    :param priority: The clinical priority associated with this order.
    :param event_status: The status for the event.
    :param event_description: Additional information about the event that occurred - e.g. if the status remained unchanged.
    :param event_dateTime: The date/time at which the event occurred.
    :param event_actor: The person who was responsible for performing or recording the action.
    :param item_code: A code that identifies a particular diagnostic investigation, or panel of investigations, that have been requested.
    :param item_bodySite: Anatomical location where the request test should be performed.
    :param item_status: The status of this individual item within the order.
    
    :param specimen: One or more specimens that the diagnostic investigation is about.
    :param event: A summary of the events of interest that have occurred as the request is processed. E.g. when the order was made, various processing steps (specimens received), when it was completed.
    :param item: The specific diagnostic investigations that are requested as part of this request. Sometimes, there can only be one item per request, but in most contexts, more than one investigation can be requested.
    :param item_specimen: If the item is related to a specific speciment.
    :param item_event: A summary of the events of interest that have occurred as this item of the request is processed.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="DiagnosticOrder",
                 text=None,
                 subject=None,
                 orderer=None,
                 encounter=None,
                 clinicalNotes=None,
                 status=None,
                 priority=None,
                 event_status=None,
                 event_description=None,
                 event_dateTime=None,
                 event_actor=None,
                 item_code=None,
                 item_bodySite=None,
                 item_status=None,
                 specimen=None,
                 event=None,
                 item=None,
                 item_specimen=None,
                 item_event=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.subject = subject                                     # , Who and/or what test is about
        self.orderer = orderer                                     # , Who ordered the test
        self.encounter = encounter                                     # , The encounter that this diagnostic order is associated with
        self.clinicalNotes = clinicalNotes                                     # , Explanation/Justification for test
        self.status = status                                     # , requested | received | accepted | in progress | review | completed | suspended | rejected | failed
        self.priority = priority                                     # , routine | urgent | stat | asap
        self.event_status = event_status                                     # , requested | received | accepted | in progress | review | completed | suspended | rejected | failed
        self.event_description = event_description                                     # , More information about the event and it's context
        self.event_dateTime = event_dateTime                                     # , The date at which the event happened
        self.event_actor = event_actor                                     # , Who recorded or did this
        self.item_code = item_code                                     # , Code to indicate the item (test or panel) being ordered
        self.item_bodySite = item_bodySite                                     # , Location of requested test (if applicable)
        self.item_status = item_status                                     # , requested | received | accepted | in progress | review | completed | suspended | rejected | failed
        
        if specimen is None:
            self.specimen = []                                     # , { attb['short_desc'] }}
        if event is None:
            self.event = []                                     # , { attb['short_desc'] }}
        if item is None:
            self.item = []                                     # , { attb['short_desc'] }}
        if item_specimen is None:
            self.item_specimen = []                                     # , { attb['short_desc'] }}
        if item_event is None:
            self.item_event = []                                     # , { attb['short_desc'] }}
        

class DiagnosticReport(Resource):
    """
    Short Description: A Diagnostic report - a combination of request information, atomic results, images, interpretation, as well as formatted reports

    Formal Description: The findings and interpretation of diagnostic  tests performed on patients, groups of patients, devices, and locations, and/or specimens derived from these. The report includes clinical context such as requesting and provider information, and some mix of atomic results, images, textual and coded interpretation, and formatted representation of diagnostic reports.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param name: A code or name that describes this diagnostic report.
    :param status: The status of the diagnostic report as a whole.
    :param issued: The date and/or time that this version of the report was released from the source diagnostic service.
    :param subject: The subject of the report. Usually, but not always, this is a patient. However diagnostic services also perform analyses on specimens collected from a variety of other sources.
    :param performer: The diagnostic service that is responsible for issuing the report.
    :param serviceCategory: The section of the diagnostic service that performs the examination e.g. biochemistry, hematology, MRI.
    :param diagnosticdateTime: The time or time-period the observed values are related to. This is usually either the time of the procedure or of specimen collection(s), but very often the source of the date/time is not known, only the date/time itself.
    :param diagnosticPeriod: The time or time-period the observed values are related to. This is usually either the time of the procedure or of specimen collection(s), but very often the source of the date/time is not known, only the date/time itself.
    :param diagnostic: The time or time-period the observed values are related to. This is usually either the time of the procedure or of specimen collection(s), but very often the source of the date/time is not known, only the date/time itself.
    :param image_comment: A comment about the image. Typically, this is used to provide an explanation for why the image is included, or to draw the viewer's attention to important features.
    :param image_link: Reference to the image source.
    :param conclusion: Concise and clinically contextualized narrative interpretation of the diagnostic report.
    
    :param requestDetail: Details concerning a test requested.
    :param specimen: Details about the specimens on which this Disagnostic report is based.
    :param result: Observations that are part of this diagnostic report. Observations can be simple name/value pairs (e.g. "atomic" results), or they can be grouping observations that include references to other members of the group (e.g. "panels").
    :param imagingStudy: One or more links to full details of any imaging performed during the diagnostic investigation. Typically, this is imaging performed by DICOM enabled modalities, but this is not required. A fully enabled PACS viewer can use this information to provide views of the source images.
    :param image: A list of key images associated with this report. The images are generally created during the diagnostic process, and may be directly of the patient, or of treated specimens (i.e. slides of interest).
    :param codedDiagnosis: Codes for the conclusion.
    :param presentedForm: Rich text representation of the entire result as issued by the diagnostic service. Multiple formats are allowed but they SHALL be semantically equivalent.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="DiagnosticReport",
                 text=None,
                 name=None,
                 status=None,
                 issued=None,
                 subject=None,
                 performer=None,
                 serviceCategory=None,
                 diagnosticdateTime=None,
                 diagnosticPeriod=None,
                 diagnostic=None,
                 image_comment=None,
                 image_link=None,
                 conclusion=None,
                 requestDetail=None,
                 specimen=None,
                 result=None,
                 imagingStudy=None,
                 image=None,
                 codedDiagnosis=None,
                 presentedForm=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.name = name                                     # , Name/Code for this diagnostic report
        self.status = status                                     # , registered | partial | final | corrected +
        self.issued = issued                                     # , Date this version was released
        self.subject = subject                                     # , The subject of the report, usually, but not always, the patient
        self.performer = performer                                     # , Responsible Diagnostic Service
        self.serviceCategory = serviceCategory                                     # , Biochemistry, Hematology etc.
        self.diagnosticdateTime = diagnosticdateTime                                     # dateTime, Physiologically Relevant time/time-period for report
        self.diagnosticPeriod = diagnosticPeriod                                     # Period, Physiologically Relevant time/time-period for report
        self.diagnostic = diagnostic                                     # , Physiologically Relevant time/time-period for report
        self.image_comment = image_comment                                     # , Comment about the image (e.g. explanation)
        self.image_link = image_link                                     # , Reference to the image source
        self.conclusion = conclusion                                     # , Clinical Interpretation of test results
        
        if requestDetail is None:
            self.requestDetail = []                                     # , { attb['short_desc'] }}
        if specimen is None:
            self.specimen = []                                     # , { attb['short_desc'] }}
        if result is None:
            self.result = []                                     # , { attb['short_desc'] }}
        if imagingStudy is None:
            self.imagingStudy = []                                     # , { attb['short_desc'] }}
        if image is None:
            self.image = []                                     # , { attb['short_desc'] }}
        if codedDiagnosis is None:
            self.codedDiagnosis = []                                     # , { attb['short_desc'] }}
        if presentedForm is None:
            self.presentedForm = []                                     # , { attb['short_desc'] }}
        

class DocumentManifest(Resource):
    """
    Short Description: A manifest that defines a set of documents

    Formal Description: A manifest that defines a set of documents.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param masterIdentifier: A single identifier that uniquely identifies this manifest. Principally used to refer to the manifest in non-FHIR contexts.
    :param type: Specifies the kind of this set of documents (e.g. Patient Summary, Discharge Summary, Prescription, etc.). The type of a set of documents may be the same as one of the documents in it - especially if there is only one - but it may be wider.
    :param created: When the document manifest was created for submission to the server (not necessarily the same thing as the actual resource last modified time, since it may be modified, replicated etc).
    :param source: Identifies the source system, application, or software that produced the document manifest.
    :param status: The status of this document manifest.
    :param supercedes: Whether this document manifest replaces another.
    :param description: Human-readable description of the source document. This is sometimes known as the "title".
    :param confidentiality: A code specifying the level of confidentiality of this set of Documents.
    
    :param subject: Who or what the set of documents is about. The documents can be about a person, (patient or healthcare practitioner), a device (i.e. machine) or even a group of subjects (such as a document about a herd of farm animals, or a set of patients that share a common exposure). If the documents cross more than one subject, then more than one subject is allowed here (unusual use case).
    :param recipient: A patient, practitioner, or organization for which this set of documents is intended.
    :param author: Identifies who is responsible for adding the information to the document.
    :param content: The list of resources that describe the parts of this document reference. Usually, these would be document references, but direct references to binary attachments and images are also allowed.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="DocumentManifest",
                 text=None,
                 masterIdentifier=None,
                 type=None,
                 created=None,
                 source=None,
                 status=None,
                 supercedes=None,
                 description=None,
                 confidentiality=None,
                 subject=None,
                 recipient=None,
                 author=None,
                 content=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.masterIdentifier = masterIdentifier                                     # , Unique Identifier for the set of documents
        self.type = type                                     # , What kind of document set this is
        self.created = created                                     # , When this document manifest created
        self.source = source                                     # , The source system/application/software
        self.status = status                                     # , current | superceded | entered in error
        self.supercedes = supercedes                                     # , If this document manifest replaces another
        self.description = description                                     # , Human-readable description (title)
        self.confidentiality = confidentiality                                     # , Sensitivity of set of documents
        
        if subject is None:
            self.subject = []                                     # , { attb['short_desc'] }}
        if recipient is None:
            self.recipient = []                                     # , { attb['short_desc'] }}
        if author is None:
            self.author = []                                     # , { attb['short_desc'] }}
        if content is None:
            self.content = []                                     # , { attb['short_desc'] }}
        

class Encounter(Resource):
    """
    Short Description: An interaction during which services are provided to the patient

    Formal Description: An interaction between a patient and healthcare provider(s) for the purpose of providing healthcare service(s) or assessing the health status of a patient.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param status: planned | in progress | onleave | finished | cancelled.
    :param fhir_class: inpatient | outpatient | ambulatory | emergency +.
    :param subject: The patient present at the encounter.
    :param participant_individual: Persons involved in the encounter other than the patient.
    :param period: The start and end time of the encounter.
    :param length: Quantity of time the encounter lasted. This excludes the time during leaves of absence.
    :param reason: Reason the encounter takes place, expressed as a code. For admissions, this can be used for a coded admission diagnosis.
    :param indication: Reason the encounter takes place, as specified using information from another resource. For admissions, this is the admission diagnosis.
    :param priority: Indicates the urgency of the encounter.
    :param hospitalization: Details about an admission to a clinic.
    :param hospitalization_preAdmissionIdentifier: Pre-admission identifier.
    :param hospitalization_origin: The location from which the patient came before admission.
    :param hospitalization_admitSource: From where patient was admitted (physician referral, transfer).
    :param hospitalization_period: Period during which the patient was admitted.
    :param hospitalization_accomodation_bed: The bed that is assigned to the patient.
    :param hospitalization_accomodation_period: Period during which the patient was assigned the bed.
    :param hospitalization_diet: Dietary restrictions for the patient.
    :param hospitalization_destination: Location to which the patient is discharged.
    :param hospitalization_dischargeDisposition: Category or kind of location after discharge.
    :param hospitalization_dischargeDiagnosis: The final diagnosis given a patient before release from the hospital after all testing, surgery, and workup are complete.
    :param hospitalization_reAdmission: Whether this hospitalization is a readmission.
    :param location_location: The location where the encounter takes place.
    :param location_period: Time period during which the patient was present at the location.
    :param serviceProvider: Department or team providing care.
    :param partOf: Another Encounter of which this encounter is a part of (administratively or in time).
    
    :param type: Specific type of encounter (e.g. e-mail consultation, surgical day-care, skilled nursing, rehabilitation).
    :param participant: The main practitioner responsible for providing the service.
    :param participant_type: Role of participant in encounter.
    :param hospitalization_accomodation: Where the patient stays during this encounter.
    :param hospitalization_specialCourtesy: Special courtesies (VIP, board member).
    :param hospitalization_specialArrangement: Wheelchair, translator, stretcher, etc.
    :param location: List of locations at which the patient has been.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Encounter",
                 text=None,
                 status=None,
                 fhir_class=None,
                 subject=None,
                 participant_individual=None,
                 period=None,
                 length=None,
                 reason=None,
                 indication=None,
                 priority=None,
                 hospitalization=None,
                 hospitalization_preAdmissionIdentifier=None,
                 hospitalization_origin=None,
                 hospitalization_admitSource=None,
                 hospitalization_period=None,
                 hospitalization_accomodation_bed=None,
                 hospitalization_accomodation_period=None,
                 hospitalization_diet=None,
                 hospitalization_destination=None,
                 hospitalization_dischargeDisposition=None,
                 hospitalization_dischargeDiagnosis=None,
                 hospitalization_reAdmission=None,
                 location_location=None,
                 location_period=None,
                 serviceProvider=None,
                 partOf=None,
                 type=None,
                 participant=None,
                 participant_type=None,
                 hospitalization_accomodation=None,
                 hospitalization_specialCourtesy=None,
                 hospitalization_specialArrangement=None,
                 location=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.status = status                                     # , planned | in progress | onleave | finished | cancelled
        self.fhir_class = fhir_class                                     # , inpatient | outpatient | ambulatory | emergency +
        self.subject = subject                                     # , The patient present at the encounter
        self.participant_individual = participant_individual                                     # , Persons involved in the encounter other than the patient
        self.period = period                                     # , The start and end time of the encounter
        self.length = length                                     # , Quantity of time the encounter lasted
        self.reason = reason                                     # , Reason the encounter takes place (code)
        self.indication = indication                                     # , Reason the encounter takes place (resource)
        self.priority = priority                                     # , Indicates the urgency of the encounter
        self.hospitalization = hospitalization                                     # , Details about an admission to a clinic
        self.hospitalization_preAdmissionIdentifier = hospitalization_preAdmissionIdentifier                                     # , Pre-admission identifier
        self.hospitalization_origin = hospitalization_origin                                     # , The location from which the patient came before admission
        self.hospitalization_admitSource = hospitalization_admitSource                                     # , From where patient was admitted (physician referral, transfer)
        self.hospitalization_period = hospitalization_period                                     # , Period during which the patient was admitted
        self.hospitalization_accomodation_bed = hospitalization_accomodation_bed                                     # , The bed that is assigned to the patient
        self.hospitalization_accomodation_period = hospitalization_accomodation_period                                     # , Period during which the patient was assigned the bed
        self.hospitalization_diet = hospitalization_diet                                     # , Dietary restrictions for the patient
        self.hospitalization_destination = hospitalization_destination                                     # , Location to which the patient is discharged
        self.hospitalization_dischargeDisposition = hospitalization_dischargeDisposition                                     # , Category or kind of location after discharge
        self.hospitalization_dischargeDiagnosis = hospitalization_dischargeDiagnosis                                     # , The final diagnosis given a patient before release from the hospital after all testing, surgery, and workup are complete
        self.hospitalization_reAdmission = hospitalization_reAdmission                                     # , Is this hospitalization a readmission?
        self.location_location = location_location                                     # , Location the encounter takes place
        self.location_period = location_period                                     # , Time period during which the patient was present at the location
        self.serviceProvider = serviceProvider                                     # , Department or team providing care
        self.partOf = partOf                                     # , Another Encounter this encounter is part of
        
        if type is None:
            self.type = []                                     # , { attb['short_desc'] }}
        if participant is None:
            self.participant = []                                     # , { attb['short_desc'] }}
        if participant_type is None:
            self.participant_type = []                                     # , { attb['short_desc'] }}
        if hospitalization_accomodation is None:
            self.hospitalization_accomodation = []                                     # , { attb['short_desc'] }}
        if hospitalization_specialCourtesy is None:
            self.hospitalization_specialCourtesy = []                                     # , { attb['short_desc'] }}
        if hospitalization_specialArrangement is None:
            self.hospitalization_specialArrangement = []                                     # , { attb['short_desc'] }}
        if location is None:
            self.location = []                                     # , { attb['short_desc'] }}
        
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


class FamilyHistory(Resource):
    """
    Short Description: Information about patient's relatives, relevant for patient

    Formal Description: Significant health events and conditions for people related to the subject relevant in the context of care for the subject.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param subject: The person who this history concerns.
    :param note: Conveys information about family history not specific to individual relations.
    :param relation_name: This will either be a name or a description.  E.g. "Aunt Susan", "my cousin with the red hair".
    :param relation_relationship: The type of relationship this person has to the patient (father, mother, brother etc.).
    :param relation_born: The actual or approximate date of birth of the relative.
    :param relation_deceased: If this resource is indicating that the related person is deceased, then an indicator of whether the person is deceased (yes) or not (no) or the age or age range or description of age at death - can be indicated here. If the reason for death is known, then it can be indicated in the outcome code of the condition - in this case the deceased property should still be set.
    :param relation_note: This property allows a non condition-specific note to the made about the related person. Ideally, the note would be in the condition property, but this is not always possible.
    :param relation_condition_type: The actual condition specified. Could be a coded condition (like MI or Diabetes) or a less specific string like 'cancer' depending on how much is known about the condition and the capabilities of the creating system.
    :param relation_condition_outcome: Indicates what happened as a result of this condition.  If the condition resulted in death, deceased date is captured on the relation.
    :param relation_condition_onset: Either the age of onset, range of approximate age or descriptive string can be recorded.  For conditions with multiple occurrences, this describes the first known occurrence.
    :param relation_condition_note: An area where general notes can be placed about this specific condition.
    
    :param relation: The related person. Each FamilyHistory resource contains the entire family history for a single person.
    :param relation_condition: The significant Conditions (or condition) that the family member had. This is a repeating section to allow a system to represent more than one condition per resource, though there is nothing stopping multiple resources - one per condition.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="FamilyHistory",
                 text=None,
                 subject=None,
                 note=None,
                 relation_name=None,
                 relation_relationship=None,
                 relation_born=None,
                 relation_deceased=None,
                 relation_note=None,
                 relation_condition_type=None,
                 relation_condition_outcome=None,
                 relation_condition_onset=None,
                 relation_condition_note=None,
                 relation=None,
                 relation_condition=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.subject = subject                                     # , Patient history is about
        self.note = note                                     # , Additional details not covered elsewhere
        self.relation_name = relation_name                                     # , The family member described
        self.relation_relationship = relation_relationship                                     # , Relationship to the subject
        self.relation_born = relation_born                                     # , (approximate) date of birth
        self.relation_deceased = relation_deceased                                     # , Dead? How old/when?
        self.relation_note = relation_note                                     # , General note about related person
        self.relation_condition_type = relation_condition_type                                     # , Condition suffered by relation
        self.relation_condition_outcome = relation_condition_outcome                                     # , deceased | permanent disability | etc.
        self.relation_condition_onset = relation_condition_onset                                     # , When condition first manifested
        self.relation_condition_note = relation_condition_note                                     # , Extra information about condition
        
        if relation is None:
            self.relation = []                                     # , { attb['short_desc'] }}
        if relation_condition is None:
            self.relation_condition = []                                     # , { attb['short_desc'] }}
        

class Group(Resource):
    """
    Short Description: Group of multiple entities

    Formal Description: Represents a defined collection of entities that may be discussed or acted upon collectively but which are not expected to act collectively and are not formally or legally recognized.  I.e. A collection of entities that isn't an Organization.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param type: Identifies the broad classification of the kind of resources the group includes.
    :param actual: If true, indicates that the resource refers to a specific group of real individuals.  If false, the group defines a set of intended individuals.
    :param code: Provides a specific type of resource the group includes.  E.g. "cow", "syringe", etc.
    :param name: A label assigned to the group for human identification and communication.
    :param quantity: A count of the number of resource instances that are part of the group.
    :param characteristic_code: A code that identifies the kind of trait being asserted.
    :param characteristic_value: The value of the trait that holds (or does not hold - see 'exclude') for members of the group.
    :param characteristic_exclude: If true, indicates the characteristic is one that is NOT held by members of the group.
    
    :param characteristic: Identifies the traits shared by members of the group.
    :param member: Identifies the resource instances that are members of the group.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Group",
                 text=None,
                 type=None,
                 actual=None,
                 code=None,
                 name=None,
                 quantity=None,
                 characteristic_code=None,
                 characteristic_value=None,
                 characteristic_exclude=None,
                 characteristic=None,
                 member=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.type = type                                     # , person | animal | practitioner | device | medication | substance
        self.actual = actual                                     # , Descriptive or actual
        self.code = code                                     # , Kind of Group members
        self.name = name                                     # , Label for Group
        self.quantity = quantity                                     # , Number of members
        self.characteristic_code = characteristic_code                                     # , Kind of characteristic
        self.characteristic_value = characteristic_value                                     # , Value held by characteristic
        self.characteristic_exclude = characteristic_exclude                                     # , Group includes or excludes
        
        if characteristic is None:
            self.characteristic = []                                     # , { attb['short_desc'] }}
        if member is None:
            self.member = []                                     # , { attb['short_desc'] }}
        

class ImagingStudy(Resource):
    """
    Short Description: A set of images produced in single study (one or more series of references images)

    Formal Description: Manifest of a set of images produced in study. The set of images may include every image in the study, or it may be an incomplete sample, such as a list of key images.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param dateTime: Date and Time the study took place.
    :param subject: Who the images are of.
    :param uid: Formal identifier for the study.
    :param accessionNo: Accession Number.
    :param referrer: The requesting/referring physician.
    :param availability: Availability of study (online, offline or nearline).
    :param url: WADO-RS URI where Study is available.
    :param numberOfSeries: Number of Series in Study.
    :param numberOfInstances: Number of SOP Instances in Study.
    :param clinicalInformation: Diagnoses etc provided with request.
    :param interpreter: Who read study and interpreted the images.
    :param description: Institution-generated description or classification of the Study (component) performed.
    :param series_number: The number of this series in the overall sequence.
    :param series_modality: The modality of this series sequence.
    :param series_uid: Formal identifier for this series.
    :param series_description: A description of the series.
    :param series_numberOfInstances: Sequence that contains attributes from the.
    :param series_availability: Availability of series (online, offline or nearline).
    :param series_url: WADO-RS URI where Series is available.
    :param series_bodySite: Body part examined. See  DICOM Part 16 Annex L for the mapping from DICOM to Snomed.
    :param series_dateTime: When the series started.
    :param series_instance_number: The number of this image in the series.
    :param series_instance_uid: Formal identifier for this image.
    :param series_instance_sopclass: DICOM Image type.
    :param series_instance_type: Type of instance (image etc) (0004,1430).
    :param series_instance_title: Description (0070,0080 | 0040,A043 > 0008,0104 | 0042,0010 | 0008,0008).
    :param series_instance_url: WADO-RS url where image is available.
    :param series_instance_attachment: A FHIR resource with content for this instance.
    
    :param order: A list of the diagnostic orders that resulted in this imaging study being performed.
    :param modality: A list of all the Series.ImageModality values that are actual acquisition modalities, i.e. those in the DICOM Context Group 29 (value set OID 1.2.840.10008.6.1.19).
    :param procedure: Type of procedure performed.
    :param series: Each study has one or more series of image instances.
    :param series_instance: A single image taken from a patient.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="ImagingStudy",
                 text=None,
                 dateTime=None,
                 subject=None,
                 uid=None,
                 accessionNo=None,
                 referrer=None,
                 availability=None,
                 url=None,
                 numberOfSeries=None,
                 numberOfInstances=None,
                 clinicalInformation=None,
                 interpreter=None,
                 description=None,
                 series_number=None,
                 series_modality=None,
                 series_uid=None,
                 series_description=None,
                 series_numberOfInstances=None,
                 series_availability=None,
                 series_url=None,
                 series_bodySite=None,
                 series_dateTime=None,
                 series_instance_number=None,
                 series_instance_uid=None,
                 series_instance_sopclass=None,
                 series_instance_type=None,
                 series_instance_title=None,
                 series_instance_url=None,
                 series_instance_attachment=None,
                 order=None,
                 modality=None,
                 procedure=None,
                 series=None,
                 series_instance=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.dateTime = dateTime                                     # , When the study was performed
        self.subject = subject                                     # , Who the images are of
        self.uid = uid                                     # , Formal identifier for the study (0020,000D)
        self.accessionNo = accessionNo                                     # , Accession Number (0008,0050)
        self.referrer = referrer                                     # , Referring physician (0008,0090)
        self.availability = availability                                     # , ONLINE | OFFLINE | NEARLINE | UNAVAILABLE (0008,0056)
        self.url = url                                     # , Retrieve URI (0008,1190)
        self.numberOfSeries = numberOfSeries                                     # , Number of Study Related Series (0020,1206)
        self.numberOfInstances = numberOfInstances                                     # , Number of Study Related Instances (0020,1208)
        self.clinicalInformation = clinicalInformation                                     # , Diagnoses etc with request (0040,1002)
        self.interpreter = interpreter                                     # , Who interpreted images (0008,1060)
        self.description = description                                     # , Institution-generated description (0008,1030)
        self.series_number = series_number                                     # , Number of this series in overall sequence (0020,0011)
        self.series_modality = series_modality                                     # , The modality of the instances in the series (0008,0060)
        self.series_uid = series_uid                                     # , Formal identifier for this series (0020,000E)
        self.series_description = series_description                                     # , A description of the series (0008,103E)
        self.series_numberOfInstances = series_numberOfInstances                                     # , Number of Series Related Instances (0020,1209)
        self.series_availability = series_availability                                     # , ONLINE | OFFLINE | NEARLINE | UNAVAILABLE (0008,0056)
        self.series_url = series_url                                     # , Retrieve URI (0008,1115 > 0008,1190)
        self.series_bodySite = series_bodySite                                     # , Body part examined (Map from 0018,0015)
        self.series_dateTime = series_dateTime                                     # , When the series started
        self.series_instance_number = series_instance_number                                     # , The number of this instance in the series (0020,0013)
        self.series_instance_uid = series_instance_uid                                     # , Formal identifier for this instance (0008,0018)
        self.series_instance_sopclass = series_instance_sopclass                                     # , DICOM class type (0008,0016)
        self.series_instance_type = series_instance_type                                     # , Type of instance (image etc) (0004,1430)
        self.series_instance_title = series_instance_title                                     # , Description (0070,0080 | 0040,A043 > 0008,0104 | 0042,0010 | 0008,0008)
        self.series_instance_url = series_instance_url                                     # , WADO-RS service where instance is available  (0008,1199 > 0008,1190)
        self.series_instance_attachment = series_instance_attachment                                     # , A FHIR resource with content for this instance
        
        if order is None:
            self.order = []                                     # , { attb['short_desc'] }}
        if modality is None:
            self.modality = []                                     # , { attb['short_desc'] }}
        if procedure is None:
            self.procedure = []                                     # , { attb['short_desc'] }}
        if series is None:
            self.series = []                                     # , { attb['short_desc'] }}
        if series_instance is None:
            self.series_instance = []                                     # , { attb['short_desc'] }}
        

class Immunization(Resource):
    """
    Short Description: Immunization event information

    Formal Description: Immunization event information.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param date: Date vaccine administered or was to be administered.
    :param vaccineType: Vaccine that was administered or was to be administered.
    :param subject: The patient to whom the vaccine was to be administered.
    :param refusedIndicator: Indicates if the vaccination was refused.
    :param reported: True if this administration was reported rather than directly administered.
    :param performer: Clinician who administered the vaccine.
    :param requester: Clinician who ordered the vaccination.
    :param manufacturer: Name of vaccine manufacturer.
    :param location: The service delivery location where the vaccine administration occurred.
    :param lotNumber: Lot number of the  vaccine product.
    :param expirationDate: Date vaccine batch expires.
    :param site: Body site where vaccine was administered.
    :param route: The path by which the vaccine product is taken into the body.
    :param doseQuantity: The quantity of vaccine product that was administered.
    :param explanation: Reasons why a vaccine was administered or refused.
    :param reaction_date: Date of reaction to the immunization.
    :param reaction_detail: Details of the reaction.
    :param reaction_reported: Self-reported indicator.
    :param vaccinationProtocol_doseSequence: Nominal position in a series.
    :param vaccinationProtocol_description: Contains the description about the protocol under which the vaccine was administered.
    :param vaccinationProtocol_authority: Indicates the authority who published the protocol?  E.g. ACIP.
    :param vaccinationProtocol_series: One possible path to achieve presumed immunity against a disease - within the context of an authority.
    :param vaccinationProtocol_seriesDoses: The recommended number of doses to achieve immunity.
    :param vaccinationProtocol_doseTarget: The targeted disease.
    :param vaccinationProtocol_doseStatus: Indicates if the immunization event should "count" against  the protocol.
    :param vaccinationProtocol_doseStatusReason: Provides an explanation as to why a immunization event should or should not count against the protocol.
    
    :param explanation_reason: Reasons why a vaccine was administered.
    :param explanation_refusalReason: Refusal or exemption reasons.
    :param reaction: Categorical data indicating that an adverse event is associated in time to an immunization.
    :param vaccinationProtocol: Contains information about the protocol(s) under which the vaccine was administered.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Immunization",
                 text=None,
                 date=None,
                 vaccineType=None,
                 subject=None,
                 refusedIndicator=None,
                 reported=None,
                 performer=None,
                 requester=None,
                 manufacturer=None,
                 location=None,
                 lotNumber=None,
                 expirationDate=None,
                 site=None,
                 route=None,
                 doseQuantity=None,
                 explanation=None,
                 reaction_date=None,
                 reaction_detail=None,
                 reaction_reported=None,
                 vaccinationProtocol_doseSequence=None,
                 vaccinationProtocol_description=None,
                 vaccinationProtocol_authority=None,
                 vaccinationProtocol_series=None,
                 vaccinationProtocol_seriesDoses=None,
                 vaccinationProtocol_doseTarget=None,
                 vaccinationProtocol_doseStatus=None,
                 vaccinationProtocol_doseStatusReason=None,
                 explanation_reason=None,
                 explanation_refusalReason=None,
                 reaction=None,
                 vaccinationProtocol=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.date = date                                     # , Vaccination administration date
        self.vaccineType = vaccineType                                     # , Vaccine product administered
        self.subject = subject                                     # , Who was immunized?
        self.refusedIndicator = refusedIndicator                                     # , Was immunization refused?
        self.reported = reported                                     # , Is this a self-reported record?
        self.performer = performer                                     # , Who administered vaccine?
        self.requester = requester                                     # , Who ordered vaccination?
        self.manufacturer = manufacturer                                     # , Vaccine manufacturer
        self.location = location                                     # , Where did vaccination occur?
        self.lotNumber = lotNumber                                     # , Vaccine lot number
        self.expirationDate = expirationDate                                     # , Vaccine expiration date
        self.site = site                                     # , Body site vaccine  was administered
        self.route = route                                     # , How vaccine entered body
        self.doseQuantity = doseQuantity                                     # , Amount of vaccine administered
        self.explanation = explanation                                     # , Administration / refusal reasons
        self.reaction_date = reaction_date                                     # , When did reaction start?
        self.reaction_detail = reaction_detail                                     # , Additional information on reaction
        self.reaction_reported = reaction_reported                                     # , Was reaction self-reported?
        self.vaccinationProtocol_doseSequence = vaccinationProtocol_doseSequence                                     # , What dose number within series?
        self.vaccinationProtocol_description = vaccinationProtocol_description                                     # , Details of vaccine protocol
        self.vaccinationProtocol_authority = vaccinationProtocol_authority                                     # , Who is responsible for protocol
        self.vaccinationProtocol_series = vaccinationProtocol_series                                     # , Name of vaccine series
        self.vaccinationProtocol_seriesDoses = vaccinationProtocol_seriesDoses                                     # , Recommended number of doses for immunity
        self.vaccinationProtocol_doseTarget = vaccinationProtocol_doseTarget                                     # , Disease immunized against
        self.vaccinationProtocol_doseStatus = vaccinationProtocol_doseStatus                                     # , Does dose count towards immunity?
        self.vaccinationProtocol_doseStatusReason = vaccinationProtocol_doseStatusReason                                     # , Why does does count/not count?
        
        if explanation_reason is None:
            self.explanation_reason = []                                     # , { attb['short_desc'] }}
        if explanation_refusalReason is None:
            self.explanation_refusalReason = []                                     # , { attb['short_desc'] }}
        if reaction is None:
            self.reaction = []                                     # , { attb['short_desc'] }}
        if vaccinationProtocol is None:
            self.vaccinationProtocol = []                                     # , { attb['short_desc'] }}
        

class ImmunizationRecommendation(Resource):
    """
    Short Description: Immunization profile

    Formal Description: A patient's point-of-time immunization status and recommendation with optional supporting justification.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param subject: The patient who is the subject of the profile.
    :param recommendation_date: The date the immunization recommendation was created.
    :param recommendation_vaccineType: Vaccine that pertains to the recommendation.
    :param recommendation_doseNumber: This indicates the next recommended dose number (e.g. dose 2 is the next recommended dose).
    :param recommendation_forecastStatus: Vaccine administration status.
    :param recommendation_dateCriterion_code: Date classification of recommendation - e.g. earliest date to give, latest date to give, etc.
    :param recommendation_dateCriterion_value: Date recommendation.
    :param recommendation_protocol: Contains information about the protocol under which the vaccine was administered.
    :param recommendation_protocol_doseSequence: Indicates the nominal position in a series of the next dose.  This is the recommended dose number as per a specified protocol.
    :param recommendation_protocol_description: Contains the description about the protocol under which the vaccine was administered.
    :param recommendation_protocol_authority: Indicates the authority who published the protocol?  E.g. ACIP.
    :param recommendation_protocol_series: One possible path to achieve presumed immunity against a disease - within the context of an authority.
    
    :param recommendation: Vaccine administration recommendations.
    :param recommendation_dateCriterion: Vaccine date recommendations - e.g. earliest date to administer, latest date to administer, etc.
    :param recommendation_supportingImmunization: Immunization event history that supports the status and recommendation.
    :param recommendation_supportingPatientInformation: Patient Information that supports the status and recommendation.  This includes patient observations, adverse reactions and allergy/intolerance information.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="ImmunizationRecommendation",
                 text=None,
                 subject=None,
                 recommendation_date=None,
                 recommendation_vaccineType=None,
                 recommendation_doseNumber=None,
                 recommendation_forecastStatus=None,
                 recommendation_dateCriterion_code=None,
                 recommendation_dateCriterion_value=None,
                 recommendation_protocol=None,
                 recommendation_protocol_doseSequence=None,
                 recommendation_protocol_description=None,
                 recommendation_protocol_authority=None,
                 recommendation_protocol_series=None,
                 recommendation=None,
                 recommendation_dateCriterion=None,
                 recommendation_supportingImmunization=None,
                 recommendation_supportingPatientInformation=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.subject = subject                                     # , Who this profile is for
        self.recommendation_date = recommendation_date                                     # , Date recommendation created
        self.recommendation_vaccineType = recommendation_vaccineType                                     # , Vaccine recommendation applies to
        self.recommendation_doseNumber = recommendation_doseNumber                                     # , Recommended dose number
        self.recommendation_forecastStatus = recommendation_forecastStatus                                     # , Vaccine administration status
        self.recommendation_dateCriterion_code = recommendation_dateCriterion_code                                     # , Type of date
        self.recommendation_dateCriterion_value = recommendation_dateCriterion_value                                     # , Recommended date
        self.recommendation_protocol = recommendation_protocol                                     # , Protocol used by recommendation
        self.recommendation_protocol_doseSequence = recommendation_protocol_doseSequence                                     # , Number of dose within sequence
        self.recommendation_protocol_description = recommendation_protocol_description                                     # , Protocol details
        self.recommendation_protocol_authority = recommendation_protocol_authority                                     # , Who is responsible for protocol
        self.recommendation_protocol_series = recommendation_protocol_series                                     # , Name of vaccination series
        
        if recommendation is None:
            self.recommendation = []                                     # , { attb['short_desc'] }}
        if recommendation_dateCriterion is None:
            self.recommendation_dateCriterion = []                                     # , { attb['short_desc'] }}
        if recommendation_supportingImmunization is None:
            self.recommendation_supportingImmunization = []                                     # , { attb['short_desc'] }}
        if recommendation_supportingPatientInformation is None:
            self.recommendation_supportingPatientInformation = []                                     # , { attb['short_desc'] }}
        

class List(Resource):
    """
    Short Description: Information summarized from a list of other resources

    Formal Description: A set of information summarized from a list of other resources.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param code: This code defines the purpose of the list - why it was created.
    :param subject: The common subject (or patient) of the resources that are in the list, if there is one.
    :param source: The entity responsible for deciding what the contents of the list were.
    :param date: The date that the list was prepared.
    :param ordered: Whether items in the list have a meaningful order.
    :param mode: How this list was prepared - whether it is a working list that is suitable for being maintained on an ongoing basis, or if it represents a snapshot of a list of items from another source, or whether it is a prepared list where items may be marked as added, modified or deleted.
    :param entry_deleted: True if this item is marked as deleted in the list.
    :param entry_date: When this item was added to the list.
    :param entry_item: A reference to the actual resource from which data was derived.
    :param emptyReason: If the list is empty, why the list is empty.
    
    :param entry: Entries in this list.
    :param entry_flag: The flag allows the system constructing the list to make one or more statements about the role and significance of the item in the list.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="List",
                 text=None,
                 code=None,
                 subject=None,
                 source=None,
                 date=None,
                 ordered=None,
                 mode=None,
                 entry_deleted=None,
                 entry_date=None,
                 entry_item=None,
                 emptyReason=None,
                 entry=None,
                 entry_flag=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.code = code                                     # , What the purpose of this list is
        self.subject = subject                                     # , If all resources have the same subject
        self.source = source                                     # , Who and/or what defined the list contents
        self.date = date                                     # , When the list was prepared
        self.ordered = ordered                                     # , Whether items in the list have a meaningful order
        self.mode = mode                                     # , working | snapshot | changes
        self.entry_deleted = entry_deleted                                     # , If this item is actually marked as deleted
        self.entry_date = entry_date                                     # , When item added to list
        self.entry_item = entry_item                                     # , Actual entry
        self.emptyReason = emptyReason                                     # , Why list is empty
        
        if entry is None:
            self.entry = []                                     # , { attb['short_desc'] }}
        if entry_flag is None:
            self.entry_flag = []                                     # , { attb['short_desc'] }}
        

class Location(Resource):
    """
    Short Description: Details and position information for a physical place

    Formal Description: Details and position information for a physical place where services are provided  and resources and participants may be stored, found, contained or accommodated.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param name: Name of the location as used by humans. Does not need to be unique.
    :param description: Description of the Location, which helps in finding or referencing the place.
    :param type: Indicates the type of function performed at the location.
    :param address: Physical location.
    :param physicalType: Physical form of the location, e.g. building, room, vehicle, road.
    :param position: The absolute geographic location of the Location, expressed in a KML compatible manner (see notes below for KML).
    :param position_longitude: Longitude. The value domain and the interpretation are the same as for the text of the longitude element in KML (see notes below).
    :param position_latitude: Latitude. The value domain and the interpretation are the same as for the text of the latitude element in KML (see notes below).
    :param position_altitude: Altitude. The value domain and the interpretation are the same as for the text of the altitude element in KML (see notes below).
    :param managingOrganization: The organization that is responsible for the provisioning and upkeep of the location.
    :param status: active | suspended | inactive.
    :param partOf: Another Location which this Location is physically part of.
    :param mode: Indicates whether a resource instance represents a specific location or a class of locations.
    
    :param telecom: The contact details of communication devices available at the location. This can include phone numbers, fax numbers, mobile numbers, email addresses and web sites.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Location",
                 text=None,
                 name=None,
                 description=None,
                 type=None,
                 address=None,
                 physicalType=None,
                 position=None,
                 position_longitude=None,
                 position_latitude=None,
                 position_altitude=None,
                 managingOrganization=None,
                 status=None,
                 partOf=None,
                 mode=None,
                 telecom=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.name = name                                     # , Name of the location as used by humans
        self.description = description                                     # , Description of the Location, which helps in finding or referencing the place
        self.type = type                                     # , Indicates the type of function performed at the location
        self.address = address                                     # , Physical location
        self.physicalType = physicalType                                     # , Physical form of the location
        self.position = position                                     # , The absolute geographic location
        self.position_longitude = position_longitude                                     # , Longitude as expressed in KML
        self.position_latitude = position_latitude                                     # , Latitude as expressed in KML
        self.position_altitude = position_altitude                                     # , Altitude as expressed in KML
        self.managingOrganization = managingOrganization                                     # , The organization that is responsible for the provisioning and upkeep of the location
        self.status = status                                     # , active | suspended | inactive
        self.partOf = partOf                                     # , Another Location which this Location is physically part of
        self.mode = mode                                     # , instance | kind
        
        if telecom is None:
            self.telecom = []                                     # , { attb['short_desc'] }}
        

class Media(Resource):
    """
    Short Description: A photo, video, or audio recording acquired or used in healthcare. The actual content may be inline or provided by direct reference

    Formal Description: A photo, video, or audio recording acquired or used in healthcare. The actual content may be inline or provided by direct reference.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param type: Whether the media is a photo (still image), an audio recording, or a video recording.
    :param subtype: Details of the type of the media - usually, how it was acquired (what type of device). If images sourced from a DICOM system, are wrapped in a Media resource, then this is the modality.
    :param dateTime: When the media was originally recorded. For video and audio, if the length of the recording is not insignificant, this is the end of the recording.
    :param subject: Who/What this Media is a record of.
    :param operator: The person who administered the collection of the image.
    :param view: The name of the imaging view e.g Lateral or Antero-posterior (AP).
    :param deviceName: The name of the device / manufacturer of the device  that was used to make the recording.
    :param height: Height of the image in pixels(photo/video).
    :param width: Width of the image in pixels (photo/video).
    :param frames: The number of frames in a photo. This is used with a multi-page fax, or an imaging acquisition context that takes multiple slices in a single image, or an animated gif. If there is more than one frame, this SHALL have a value in order to alert interface software that a multi-frame capable rendering widget is required.
    :param length: The length of the recording in seconds - for audio and video.
    :param content: The actual content of the media - inline or by direct reference to the media source file.
    
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Media",
                 text=None,
                 type=None,
                 subtype=None,
                 dateTime=None,
                 subject=None,
                 operator=None,
                 view=None,
                 deviceName=None,
                 height=None,
                 width=None,
                 frames=None,
                 length=None,
                 content=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.type = type                                     # , photo | video | audio
        self.subtype = subtype                                     # , The type of acquisition equipment/process
        self.dateTime = dateTime                                     # , When the media was taken/recorded (end)
        self.subject = subject                                     # , Who/What this Media is a record of
        self.operator = operator                                     # , The person who generated the image
        self.view = view                                     # , Imaging view e.g Lateral or Antero-posterior
        self.deviceName = deviceName                                     # , Name of the device/manufacturer
        self.height = height                                     # , Height of the image in pixels(photo/video)
        self.width = width                                     # , Width of the image in pixels (photo/video)
        self.frames = frames                                     # , Number of frames if > 1 (photo)
        self.length = length                                     # , Length in seconds (audio / video)
        self.content = content                                     # , Actual Media - reference or data
        
        

class Medication(Resource):
    """
    Short Description: Definition of a Medication

    Formal Description: Primarily used for identification and definition of Medication, but also covers ingredients and packaging.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param name: The common/commercial name of the medication absent information such as strength, form, etc.  E.g. Acetaminophen, Tylenol 3, etc.  The fully coordinated name is communicated as the display of Medication.code.
    :param code: A code (or set of codes) that identify this medication.   Usage note: This could be a standard drug code such as a drug regulator code, RxNorm code, SNOMED CT code, etc. It could also be a local formulary code, optionally with translations to the standard drug codes.
    :param isBrand: Set to true if the item is attributable to a specific manufacturer (even if we don't know who that is).
    :param manufacturer: Describes the details of the manufacturer.
    :param kind: Medications are either a single administrable product or a package that contains one or more products.
    :param product: Information that only applies to products (not packages).
    :param product_form: Describes the form of the item.  Powder; tables; carton.
    :param product_ingredient_item: The actual ingredient - either a substance (simple ingredient) or another medication.
    :param product_ingredient_amount: Specifies how many (or how much) of the items there are in this Medication.  E.g. 250 mg per tablet.
    :param package: Information that only applies to packages (not products).
    :param package_container: The kind of container that this package comes as.
    :param package_content_item: Identifies one of the items in the package.
    :param package_content_amount: The amount of the product that is in the package.
    
    :param product_ingredient: Identifies a particular constituent of interest in the product.
    :param package_content: A set of components that go to make up the described item.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Medication",
                 text=None,
                 name=None,
                 code=None,
                 isBrand=None,
                 manufacturer=None,
                 kind=None,
                 product=None,
                 product_form=None,
                 product_ingredient_item=None,
                 product_ingredient_amount=None,
                 package=None,
                 package_container=None,
                 package_content_item=None,
                 package_content_amount=None,
                 product_ingredient=None,
                 package_content=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.name = name                                     # , Common / Commercial name
        self.code = code                                     # , Codes that identify this medication
        self.isBrand = isBrand                                     # , True if a brand
        self.manufacturer = manufacturer                                     # , Manufacturer of the item
        self.kind = kind                                     # , product | package
        self.product = product                                     # , Administrable medication details
        self.product_form = product_form                                     # , powder | tablets | carton +
        self.product_ingredient_item = product_ingredient_item                                     # , The product contained
        self.product_ingredient_amount = product_ingredient_amount                                     # , How much ingredient in product
        self.package = package                                     # , Details about packaged medications
        self.package_container = package_container                                     # , E.g. box, vial, blister-pack
        self.package_content_item = package_content_item                                     # , A product in the package
        self.package_content_amount = package_content_amount                                     # , How many are in the package?
        
        if product_ingredient is None:
            self.product_ingredient = []                                     # , { attb['short_desc'] }}
        if package_content is None:
            self.package_content = []                                     # , { attb['short_desc'] }}
        

class MedicationAdministration(Resource):
    """
    Short Description: Administration of medication to a patient

    Formal Description: Describes the event of a patient being given a dose of a medication.  This may be as simple as swallowing a tablet or it may be a long running infusion.

Related resources tie this event to the authorizing prescription, and the specific encounter between patient and health care practitioner.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param status: Will generally be set to show that the administration has been completed.  For some long running administrations such as infusions it is possible for an administration to be started but not completed or it may be paused while some other process is under way.
    :param patient: The person or animal to whom the medication was given.
    :param practitioner: The individual who was responsible for giving the medication to the patient.
    :param encounter: The visit or admission the or other contact between patient and health care provider the medication administration was performed as part of.
    :param prescription: The original request, instruction or authority to perform the administration.
    :param wasNotGiven: Set this to true if the record is saying that the medication was NOT administered.
    :param whenGiven: An interval of time during which the administration took place.  For many administrations, such as swallowing a tablet the lower and upper values of the interval will be the same.
    :param medication: Identifies the medication that was administered. This is either a link to a resource representing the details of the medication or a simple attribute carrying a code that identifies the medication from a known list of medications.
    :param dosage_timing: The timing schedule for giving the medication to the patient.  This may be a single time point (using dateTime) or it may be a start and end dateTime (Period).
    :param dosage_asNeeded: If set to true or if specified as a CodeableConcept, indicates that the medication is only taken when needed within the specified schedule rather than at every scheduled dose.  If a CodeableConcept is present, it indicates the pre-condition for taking the Medication.
    :param dosage_site: A coded specification of the anatomic site where the medication first entered the body.  E.g. "left arm".
    :param dosage_route: A code specifying the route or physiological path of administration of a therapeutic agent into or onto the patient.   E.g. topical, intravenous, etc.
    :param dosage_method: A coded value indicating the method by which the medication was introduced into or onto the body. Most commonly used for injections.  Examples:  Slow Push; Deep IV.

Terminologies used often pre-coordinate this term with the route and or form of administration.
    :param dosage_quantity: The amount of the medication given at one administration event.   Use this value when the administration is essentially an instantaneous event such as a swallowing a tablet or giving an injection.
    :param dosage_rate: Identifies the speed with which the medication was introduced into the patient. Typically the rate for an infusion e.g. 200ml in 2 hours.  May also expressed as a rate per unit of time such as 100ml per hour - the duration is then not specified, or is specified in the quantity.
    :param dosage_maxDosePerPeriod: The maximum total quantity of a therapeutic substance that was administered to the patient over the specified period of time. E.g. 1000mg in 24 hours.
    
    :param reasonNotGiven: A code indicating why the administration was not performed.
    :param device: The device used in administering the medication to the patient.  E.g. a particular infusion pump.
    :param dosage: Provides details of how much of the medication was administered.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="MedicationAdministration",
                 text=None,
                 status=None,
                 patient=None,
                 practitioner=None,
                 encounter=None,
                 prescription=None,
                 wasNotGiven=None,
                 whenGiven=None,
                 medication=None,
                 dosage_timing=None,
                 dosage_asNeeded=None,
                 dosage_site=None,
                 dosage_route=None,
                 dosage_method=None,
                 dosage_quantity=None,
                 dosage_rate=None,
                 dosage_maxDosePerPeriod=None,
                 reasonNotGiven=None,
                 device=None,
                 dosage=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.status = status                                     # , in progress | on hold | completed | entered in error | stopped
        self.patient = patient                                     # , Who received medication?
        self.practitioner = practitioner                                     # , Who administered substance?
        self.encounter = encounter                                     # , Encounter administered as part of
        self.prescription = prescription                                     # , Order administration performed against
        self.wasNotGiven = wasNotGiven                                     # , True if medication not administered
        self.whenGiven = whenGiven                                     # , Start and end time of administration
        self.medication = medication                                     # , What was administered?
        self.dosage_timing = dosage_timing                                     # , When dose(s) were given
        self.dosage_asNeeded = dosage_asNeeded                                     # , Take "as needed" f(or x)
        self.dosage_site = dosage_site                                     # , Body site administered to
        self.dosage_route = dosage_route                                     # , Path of substance into body
        self.dosage_method = dosage_method                                     # , How drug was administered
        self.dosage_quantity = dosage_quantity                                     # , Amount administered in one dose
        self.dosage_rate = dosage_rate                                     # , Dose quantity per unit of time
        self.dosage_maxDosePerPeriod = dosage_maxDosePerPeriod                                     # , Total dose that was consumed per unit of time
        
        if reasonNotGiven is None:
            self.reasonNotGiven = []                                     # , { attb['short_desc'] }}
        if device is None:
            self.device = []                                     # , { attb['short_desc'] }}
        if dosage is None:
            self.dosage = []                                     # , { attb['short_desc'] }}
        

class MedicationDispense(Resource):
    """
    Short Description: Dispensing a medication to a named patient

    Formal Description: Dispensing a medication to a named patient.  This includes a description of the supply provided and the instructions for administering the medication.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param status: A code specifying the state of the set of dispense events.
    :param patient: A link to a resource representing the person to whom the medication will be given.
    :param dispenser: The individual responsible for dispensing the medication.
    :param dispense_status: A code specifying the state of the dispense event.
    :param dispense_type: Indicates the type of dispensing event that is performed. Examples include: Trial Fill, Completion of Trial, Partial Fill, Emergency Fill, Samples, etc.
    :param dispense_quantity: The amount of medication that has been dispensed. Includes unit of measure.
    :param dispense_medication: Identifies the medication being administered. This is either a link to a resource representing the details of the medication or a simple attribute carrying a code that identifies the medication from a known list of medications.
    :param dispense_whenPrepared: The time when the dispensed product was packaged and reviewed.
    :param dispense_whenHandedOver: The time the dispensed product was provided to the patient or their representative.
    :param dispense_destination: Identification of the facility/location where the medication was shipped to, as part of the dispense event.
    :param dispense_dosage_additionalInstructions: Additional instructions such as "Swallow with plenty of water" which may or may not be coded.
    :param dispense_dosage_timing: The timing schedule for giving the medication to the patient.  The Schedule data type allows many different expressions, for example.  "Every  8 hours"; "Three times a day"; "1/2 an hour before breakfast for 10 days from 23-Dec 2011:";  "15 Oct 2013, 17 Oct 2013 and 1 Nov 2013".
    :param dispense_dosage_asNeeded: If set to true or if specified as a CodeableConcept, indicates that the medication is only taken when needed within the specified schedule rather than at every scheduled dose.  If a CodeableConcept is present, it indicates the pre-condition for taking the Medication.
    :param dispense_dosage_site: A coded specification of the anatomic site where the medication first enters the body.
    :param dispense_dosage_route: A code specifying the route or physiological path of administration of a therapeutic agent into or onto a subject.
    :param dispense_dosage_method: A coded value indicating the method by which the medication is introduced into or onto the body. Most commonly used for injections.  Examples:  Slow Push; Deep IV.

Terminologies used often pre-coordinate this term with the route and or form of administration.
    :param dispense_dosage_quantity: The amount of therapeutic or other substance given at one administration event.
    :param dispense_dosage_rate: Identifies the speed with which the substance is introduced into the subject. Typically the rate for an infusion. 200ml in 2 hours.
    :param dispense_dosage_maxDosePerPeriod: The maximum total quantity of a therapeutic substance that may be administered to a subject over the period of time,  e.g. 1000mg in 24 hours.
    :param substitution: Indicates whether or not substitution was made as part of the dispense.  In some cases substitution will be expected but doesn't happen, in other cases substitution is not expected but does happen.  This block explains what substitition did or did not happen and why.
    :param substitution_type: A code signifying whether a different drug was dispensed from what was prescribed.
    
    :param authorizingPrescription: Indicates the medication order that is being dispensed against.
    :param dispense: Indicates the details of the dispense event such as the days supply and quantity of medication dispensed.
    :param dispense_receiver: Identifies the person who picked up the medication.  This will usually be a patient or their carer, but some cases exist where it can be a healthcare professional.
    :param dispense_dosage: Indicates how the medication is to be used by the patient.
    :param substitution_reason: Indicates the reason for the substitution of (or lack of substitution) from what was prescribed.
    :param substitution_responsibleParty: The person or organization that has primary responsibility for the substitution.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="MedicationDispense",
                 text=None,
                 status=None,
                 patient=None,
                 dispenser=None,
                 dispense_status=None,
                 dispense_type=None,
                 dispense_quantity=None,
                 dispense_medication=None,
                 dispense_whenPrepared=None,
                 dispense_whenHandedOver=None,
                 dispense_destination=None,
                 dispense_dosage_additionalInstructions=None,
                 dispense_dosage_timing=None,
                 dispense_dosage_asNeeded=None,
                 dispense_dosage_site=None,
                 dispense_dosage_route=None,
                 dispense_dosage_method=None,
                 dispense_dosage_quantity=None,
                 dispense_dosage_rate=None,
                 dispense_dosage_maxDosePerPeriod=None,
                 substitution=None,
                 substitution_type=None,
                 authorizingPrescription=None,
                 dispense=None,
                 dispense_receiver=None,
                 dispense_dosage=None,
                 substitution_reason=None,
                 substitution_responsibleParty=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.status = status                                     # , in progress | on hold | completed | entered in error | stopped
        self.patient = patient                                     # , Who the dispense is for
        self.dispenser = dispenser                                     # , Practitioner responsible for dispensing medication
        self.dispense_status = dispense_status                                     # , in progress | on hold | completed | entered in error | stopped
        self.dispense_type = dispense_type                                     # , Trial fill, partial fill, emergency fill, etc.
        self.dispense_quantity = dispense_quantity                                     # , Amount dispensed
        self.dispense_medication = dispense_medication                                     # , What medication was supplied
        self.dispense_whenPrepared = dispense_whenPrepared                                     # , Dispense processing time
        self.dispense_whenHandedOver = dispense_whenHandedOver                                     # , Handover time
        self.dispense_destination = dispense_destination                                     # , Where the medication was sent
        self.dispense_dosage_additionalInstructions = dispense_dosage_additionalInstructions                                     # , E.g. "Take with food"
        self.dispense_dosage_timing = dispense_dosage_timing                                     # , When medication should be administered
        self.dispense_dosage_asNeeded = dispense_dosage_asNeeded                                     # , Take "as needed" f(or x)
        self.dispense_dosage_site = dispense_dosage_site                                     # , Body site to administer to
        self.dispense_dosage_route = dispense_dosage_route                                     # , How drug should enter body
        self.dispense_dosage_method = dispense_dosage_method                                     # , Technique for administering medication
        self.dispense_dosage_quantity = dispense_dosage_quantity                                     # , Amount of medication per dose
        self.dispense_dosage_rate = dispense_dosage_rate                                     # , Amount of medication per unit of time
        self.dispense_dosage_maxDosePerPeriod = dispense_dosage_maxDosePerPeriod                                     # , Upper limit on medication per unit of time
        self.substitution = substitution                                     # , Deals with substitution of one medicine for another
        self.substitution_type = substitution_type                                     # , Type of substitiution
        
        if authorizingPrescription is None:
            self.authorizingPrescription = []                                     # , { attb['short_desc'] }}
        if dispense is None:
            self.dispense = []                                     # , { attb['short_desc'] }}
        if dispense_receiver is None:
            self.dispense_receiver = []                                     # , { attb['short_desc'] }}
        if dispense_dosage is None:
            self.dispense_dosage = []                                     # , { attb['short_desc'] }}
        if substitution_reason is None:
            self.substitution_reason = []                                     # , { attb['short_desc'] }}
        if substitution_responsibleParty is None:
            self.substitution_responsibleParty = []                                     # , { attb['short_desc'] }}
        

class MedicationPrescription(Resource):
    """
    Short Description: Prescription of medication to for patient

    Formal Description: An order for both supply of the medication and the instructions for administration of the medicine to a patient.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param dateWritten: The date (and perhaps time) when the prescription was written.
    :param status: A code specifying the state of the order.  Generally this will be active or completed state.
    :param patient: A link to a resource representing the person to whom the medication will be given.
    :param prescriber: The healthcare professional responsible for authorizing the prescription.
    :param encounter: A link to a resource that identifies the particular occurrence of contact between patient and health care provider.
    :param reasonCodeableConcept: Can be the reason or the indication for writing the prescription.
    :param reasonResourceReference: Can be the reason or the indication for writing the prescription.
    :param reason: Can be the reason or the indication for writing the prescription.
    :param medication: Identifies the medication being administered. This is either a link to a resource representing the details of the medication or a simple attribute carrying a code that identifies the medication from a known list of medications.
    :param dosageInstruction_text: Free text dosage instructions for cases where the instructions are too complex to code.
    :param dosageInstruction_additionalInstructions: Additional instructions such as "Swallow with plenty of water" which may or may not be coded.
    :param dosageInstruction_timing: The timing schedule for giving the medication to the patient.  The Schedule data type allows many different expressions, for example.  "Every  8 hours"; "Three times a day"; "1/2 an hour before breakfast for 10 days from 23-Dec 2011:";  "15 Oct 2013, 17 Oct 2013 and 1 Nov 2013".
    :param dosageInstruction_asNeeded: If set to true or if specified as a CodeableConcept, indicates that the medication is only taken when needed within the specified schedule rather than at every scheduled dose.  If a CodeableConcept is present, it indicates the pre-condition for taking the Medication.
    :param dosageInstruction_site: A coded specification of the anatomic site where the medication first enters the body.
    :param dosageInstruction_route: A code specifying the route or physiological path of administration of a therapeutic agent into or onto a patient.
    :param dosageInstruction_method: A coded value indicating the method by which the medication is introduced into or onto the body. Most commonly used for injections.  Examples:  Slow Push; Deep IV.

Terminologies used often pre-coordinate this term with the route and or form of administration.
    :param dosageInstruction_doseQuantity: The amount of therapeutic or other substance given at one administration event.
    :param dosageInstruction_rate: Identifies the speed with which the substance is introduced into the subject. Typically the rate for an infusion. 200ml in 2 hours.
    :param dosageInstruction_maxDosePerPeriod: The maximum total quantity of a therapeutic substance that may be administered to a subject over the period of time. E.g. 1000mg in 24 hours.
    :param dispense: Deals with details of the dispense part of the order.
    :param dispense_medication: Identifies the medication that is to be dispensed.  This may be a more specifically defined than the medicationPrescription.medication . This is either a link to a resource representing the details of the medication or a simple attribute carrying a code that identifies the medication from a known list of medications.
    :param dispense_validityPeriod: Design Comments: This indicates the validity period of a prescription (stale dating the Prescription) 
It reflects the prescriber perspective for the validity of the prescription. Dispenses must not be made against the prescription outside of this period. The lower-bound of the Dispensing Window signifies the earliest date that the prescription can be filled for the first time. If an upper-bound is not specified then the Prescription is open-ended or will default to a stale-date based on regulations. 
Rationale: Indicates when the Prescription becomes valid, and when it ceases to be a dispensable Prescription.
    :param dispense_numberOfRepeatsAllowed: An integer indicating the number of repeats of the Dispense. 
UsageNotes: For example, the number of times the prescribed quantity is to be supplied including the initial standard fill.
    :param dispense_quantity: The amount that is to be dispensed.
    :param dispense_expectedSupplyDuration: Identifies the period time over which the supplied product is expected to be used, or the length of time the dispense is expected to last. 
In some situations, this attribute may be used instead of quantity to identify the amount supplied by how long it is expected to last, rather than the physical quantity issued, e.g. 90 days supply of medication (based on an ordered dosage) When possible, it is always better to specify quantity, as this tends to be more precise. expectedSupplyDuration will always be an estimate that can be influenced by external factors.
    :param substitution: Indicates whether or not substitution can or should be part of the dispense. In some cases substitution must happen, in other cases substitution must not happen, and in others it does not matter. This block explains the prescriber's intent. If nothing is specified substitution may be done.
    :param substitution_type: A code signifying whether a different drug should be dispensed from what was prescribed.
    :param substitution_reason: Indicates the reason for the substitution, or why substitution must or must not be performed.
    
    :param dosageInstruction: Indicates how the medication is to be used by the patient.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="MedicationPrescription",
                 text=None,
                 dateWritten=None,
                 status=None,
                 patient=None,
                 prescriber=None,
                 encounter=None,
                 reasonCodeableConcept=None,
                 reasonResourceReference=None,
                 reason=None,
                 medication=None,
                 dosageInstruction_text=None,
                 dosageInstruction_additionalInstructions=None,
                 dosageInstruction_timing=None,
                 dosageInstruction_asNeeded=None,
                 dosageInstruction_site=None,
                 dosageInstruction_route=None,
                 dosageInstruction_method=None,
                 dosageInstruction_doseQuantity=None,
                 dosageInstruction_rate=None,
                 dosageInstruction_maxDosePerPeriod=None,
                 dispense=None,
                 dispense_medication=None,
                 dispense_validityPeriod=None,
                 dispense_numberOfRepeatsAllowed=None,
                 dispense_quantity=None,
                 dispense_expectedSupplyDuration=None,
                 substitution=None,
                 substitution_type=None,
                 substitution_reason=None,
                 dosageInstruction=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.dateWritten = dateWritten                                     # , When prescription was authorized
        self.status = status                                     # , active | on hold | completed | entered in error | stopped | superceded
        self.patient = patient                                     # , Who prescription is for
        self.prescriber = prescriber                                     # , Who ordered the medication(s)
        self.encounter = encounter                                     # , Created during encounter / admission / stay
        self.reasonCodeableConcept = reasonCodeableConcept                                     # CodeableConcept, Reason or indication for writing the prescription
        self.reasonResourceReference = reasonResourceReference                                     # ResourceReference, Reason or indication for writing the prescription
        self.reason = reason                                     # , Reason or indication for writing the prescription
        self.medication = medication                                     # , Medication to be taken
        self.dosageInstruction_text = dosageInstruction_text                                     # , Dosage instructions expressed as text
        self.dosageInstruction_additionalInstructions = dosageInstruction_additionalInstructions                                     # , Supplemental instructions - e.g. "with meals"
        self.dosageInstruction_timing = dosageInstruction_timing                                     # , When medication should be administered
        self.dosageInstruction_asNeeded = dosageInstruction_asNeeded                                     # , Take "as needed" f(or x)
        self.dosageInstruction_site = dosageInstruction_site                                     # , Body site to administer to
        self.dosageInstruction_route = dosageInstruction_route                                     # , How drug should enter body
        self.dosageInstruction_method = dosageInstruction_method                                     # , Technique for administering medication
        self.dosageInstruction_doseQuantity = dosageInstruction_doseQuantity                                     # , Amount of medication per dose
        self.dosageInstruction_rate = dosageInstruction_rate                                     # , Amount of medication per unit of time
        self.dosageInstruction_maxDosePerPeriod = dosageInstruction_maxDosePerPeriod                                     # , Upper limit on medication per unit of time
        self.dispense = dispense                                     # , Medication supply authorization
        self.dispense_medication = dispense_medication                                     # , Product to be supplied
        self.dispense_validityPeriod = dispense_validityPeriod                                     # , Time period supply is authorized for
        self.dispense_numberOfRepeatsAllowed = dispense_numberOfRepeatsAllowed                                     # , # of refills authorized
        self.dispense_quantity = dispense_quantity                                     # , Amount of medication to supply per dispense
        self.dispense_expectedSupplyDuration = dispense_expectedSupplyDuration                                     # , Days supply per dispense
        self.substitution = substitution                                     # , Any restrictions on medication substitution?
        self.substitution_type = substitution_type                                     # , generic | formulary +
        self.substitution_reason = substitution_reason                                     # , Why should substitution (not) be made
        
        if dosageInstruction is None:
            self.dosageInstruction = []                                     # , { attb['short_desc'] }}
        

class MedicationStatement(Resource):
    """
    Short Description: Administration of medication to a patient

    Formal Description: A record of medication being taken by a patient, or that the medication has been given to a patient where the record is the result of a report from the patient or another clinician.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param patient: The person or animal who is /was taking the medication.
    :param wasNotGiven: Set this to true if the record is saying that the medication was NOT taken.
    :param whenGiven: The interval of time during which it is being asserted that the patient was taking the medication.
    :param medication: Identifies the medication being administered. This is either a link to a resource representing the details of the medication or a simple attribute carrying a code that identifies the medication from a known list of medications.
    :param dosage_timing: The timing schedule for giving the medication to the patient.  The Schedule data type allows many different expressions, for example.  "Every  8 hours"; "Three times a day"; "1/2 an hour before breakfast for 10 days from 23-Dec 2011:";  "15 Oct 2013, 17 Oct 2013 and 1 Nov 2013".
    :param dosage_asNeeded: If set to true or if specified as a CodeableConcept, indicates that the medication is only taken when needed within the specified schedule rather than at every scheduled dose.  If a CodeableConcept is present, it indicates the pre-condition for taking the Medication.
    :param dosage_site: A coded specification of the anatomic site where the medication first enters the body.
    :param dosage_route: A code specifying the route or physiological path of administration of a therapeutic agent into or onto a subject.
    :param dosage_method: A coded value indicating the method by which the medication is introduced into or onto the body. Most commonly used for injections.  Examples:  Slow Push; Deep IV.

Terminologies used often pre-coordinate this term with the route and or form of administration.
    :param dosage_quantity: The amount of therapeutic or other substance given at one administration event.
    :param dosage_rate: Identifies the speed with which the substance is introduced into the subject. Typically the rate for an infusion. 200ml in 2 hours.
    :param dosage_maxDosePerPeriod: The maximum total quantity of a therapeutic substance that may be administered to a subject over the period of time. E.g. 1000mg in 24 hours.
    
    :param reasonNotGiven: A code indicating why the medication was not taken.
    :param device: An identifier or a link to a resource that identifies a device used in administering the medication to the patient.
    :param dosage: Indicates how the medication is/was used by the patient.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="MedicationStatement",
                 text=None,
                 patient=None,
                 wasNotGiven=None,
                 whenGiven=None,
                 medication=None,
                 dosage_timing=None,
                 dosage_asNeeded=None,
                 dosage_site=None,
                 dosage_route=None,
                 dosage_method=None,
                 dosage_quantity=None,
                 dosage_rate=None,
                 dosage_maxDosePerPeriod=None,
                 reasonNotGiven=None,
                 device=None,
                 dosage=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.patient = patient                                     # , Who was/is taking medication
        self.wasNotGiven = wasNotGiven                                     # , True if medication is/was not being taken
        self.whenGiven = whenGiven                                     # , Over what period was medication consumed?
        self.medication = medication                                     # , What medication was taken?
        self.dosage_timing = dosage_timing                                     # , When/how often was medication taken?
        self.dosage_asNeeded = dosage_asNeeded                                     # , Take "as needed" f(or x)
        self.dosage_site = dosage_site                                     # , Where on body was medication administered?
        self.dosage_route = dosage_route                                     # , How did the medication enter the body?
        self.dosage_method = dosage_method                                     # , Technique used to administer medication
        self.dosage_quantity = dosage_quantity                                     # , Amount administered in one dose
        self.dosage_rate = dosage_rate                                     # , Dose quantity per unit of time
        self.dosage_maxDosePerPeriod = dosage_maxDosePerPeriod                                     # , Maximum dose that was consumed per unit of time
        
        if reasonNotGiven is None:
            self.reasonNotGiven = []                                     # , { attb['short_desc'] }}
        if device is None:
            self.device = []                                     # , { attb['short_desc'] }}
        if dosage is None:
            self.dosage = []                                     # , { attb['short_desc'] }}
        

class MessageHeader(Resource):
    """
    Short Description: A resource that describes a message that is exchanged between systems

    Formal Description: The header for a message exchange that is either requesting or responding to an action.  The resource(s) that are the subject of the action as well as other Information related to the action are typically transmitted in a bundle in which the MessageHeader resource instance is the first resource in the bundle.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param timestamp: The time that the message was sent.
    :param event: Code that identifies the event this message represents and connects it with it's definition. Events defined as part of the FHIR specification have the system value "http://hl7.org/pyfhir/message-type".
    :param response: Information about the message that this message is a response to.  Only present if this message is a response.
    :param response_code: Code that identifies the type of response to the message - whether it was successful or not, and whether it should be resent or not.
    :param response_details: Full details of any issues found in the message.
    :param source: The source application from which this message originated.
    :param source_name: Human-readable name for the target system.
    :param source_software: May include configuration or other information useful in debugging.
    :param source_version: Can convey versions of multiple systems in situations where a message passes through multiple hands.
    :param source_contact: An e-mail, phone, website or other contact point to use to resolve issues with message communications.
    :param source_endpoint: Identifies the routing target to send acknowledgements to.
    :param destination_name: Human-readable name for the source system.
    :param destination_target: Identifies the target end system in situations where the initial message transmission is to an intermediary system.
    :param destination_endpoint: Indicates where the message should be routed to.
    :param enterer: The person or device that performed the data entry leading to this message. Where there is more than one candidate, pick the most proximal to the message. Can provide other enterers in extensions.
    :param author: The logical author of the message - the person or device that decided the described event should happen. Where there is more than one candidate, pick the most proximal to the MessageHeader. Can provide other authors in extensions.
    :param receiver: Allows data conveyed by a message to be addressed to a particular person or department when routing to a specific application isn't sufficient.
    :param responsible: The person or organization that accepts overall responsibility for the contents of the message. The implication is that the message event happened under the policies of the responsible party.
    :param reason: Coded indication of the cause for the event - indicates  a reason for the occurance of the event that is a focus of this message.
    
    :param destination: The destination application which the message is intended for.
    :param data: The actual data of the message - a reference to the root/focus class of the event.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="MessageHeader",
                 text=None,
                 timestamp=None,
                 event=None,
                 response=None,
                 response_code=None,
                 response_details=None,
                 source=None,
                 source_name=None,
                 source_software=None,
                 source_version=None,
                 source_contact=None,
                 source_endpoint=None,
                 destination_name=None,
                 destination_target=None,
                 destination_endpoint=None,
                 enterer=None,
                 author=None,
                 receiver=None,
                 responsible=None,
                 reason=None,
                 destination=None,
                 data=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.timestamp = timestamp                                     # , Time that the message was sent
        self.event = event                                     # , Code for the event this message represents
        self.response = response                                     # , If this is a reply to prior message
        self.response_code = response_code                                     # , ok | transient-error | fatal-error
        self.response_details = response_details                                     # , Specific list of hints/warnings/errors
        self.source = source                                     # , Message Source Application
        self.source_name = source_name                                     # , Name of system
        self.source_software = source_software                                     # , Name of software running the system
        self.source_version = source_version                                     # , Version of software running
        self.source_contact = source_contact                                     # , Human contact for problems
        self.source_endpoint = source_endpoint                                     # , Actual message source address or id
        self.destination_name = destination_name                                     # , Name of system
        self.destination_target = destination_target                                     # , Particular delivery destination within the destination
        self.destination_endpoint = destination_endpoint                                     # , Actual destination address or id
        self.enterer = enterer                                     # , The source of the data entry
        self.author = author                                     # , The source of the decision
        self.receiver = receiver                                     # , Intended "real-world" recipient for the data
        self.responsible = responsible                                     # , Final responsibility for event
        self.reason = reason                                     # , Cause of event
        
        if destination is None:
            self.destination = []                                     # , { attb['short_desc'] }}
        if data is None:
            self.data = []                                     # , { attb['short_desc'] }}
        

class Observation(Resource):
    """
    Short Description: Measurements and simple assertions

    Formal Description: Measurements and simple assertions made about a patient, device or other subject.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param name: Describes what was observed. Sometimes this is called the observation "code".
    :param valueQuantity: The information determined as a result of making the observation, if the information has a simple value.
    :param valueCodeableConcept: The information determined as a result of making the observation, if the information has a simple value.
    :param valueAttachment: The information determined as a result of making the observation, if the information has a simple value.
    :param valueRatio: The information determined as a result of making the observation, if the information has a simple value.
    :param valuePeriod: The information determined as a result of making the observation, if the information has a simple value.
    :param valueSampledData: The information determined as a result of making the observation, if the information has a simple value.
    :param valueString: The information determined as a result of making the observation, if the information has a simple value.
    :param value: The information determined as a result of making the observation, if the information has a simple value.
    :param interpretation: The assessment made based on the result of the observation.
    :param comments: May include statements about significant, unexpected or unreliable values, or information about the source of the value where this may be relevant to the interpretation of the result.
    :param appliesdateTime: The time or time-period the observed value is asserted as being true. For biological subjects - e.g. human patients - this is usually called the "physiologically relevant time". This is usually either the time of the procedure or of specimen collection, but very often the source of the date/time is not known, only the date/time itself.
    :param appliesPeriod: The time or time-period the observed value is asserted as being true. For biological subjects - e.g. human patients - this is usually called the "physiologically relevant time". This is usually either the time of the procedure or of specimen collection, but very often the source of the date/time is not known, only the date/time itself.
    :param applies: The time or time-period the observed value is asserted as being true. For biological subjects - e.g. human patients - this is usually called the "physiologically relevant time". This is usually either the time of the procedure or of specimen collection, but very often the source of the date/time is not known, only the date/time itself.
    :param issued: Date/Time this was made available.
    :param status: The status of the result value.
    :param reliability: An estimate of the degree to which quality issues have impacted on the value reported.
    :param bodySite: Indicates where on the subject's body the observation was made.
    :param method: Indicates the mechanism used to perform the observation.
    :param subject: The thing the observation is being made about.
    :param specimen: The specimen that was used when this observation was made.
    :param referenceRange_low: The value of the low bound of the reference range. If this is omitted, the low bound of the reference range is assumed to be meaningless. E.g. <2.3.
    :param referenceRange_high: The value of the high bound of the reference range. If this is omitted, the high bound of the reference range is assumed to be meaningless. E.g. >5.
    :param referenceRange_meaning: Code for the meaning of the reference range.
    :param referenceRange_age: The age at which this reference range is applicable. This is a neonatal age (e.g. number of weeks at term) if the meaning says so.
    :param related_type: A code specifying the kind of relationship that exists with the target observation.
    :param related_target: A reference to the observation that is related to this observation.
    
    :param performer: Who was responsible for asserting the observed value as "true".
    :param referenceRange: Guidance on how to interpret the value by comparison to a normal or recommended range.
    :param related: Related observations - either components, or previous observations, or statements of derivation.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Observation",
                 text=None,
                 name=None,
                 valueQuantity=None,
                 valueCodeableConcept=None,
                 valueAttachment=None,
                 valueRatio=None,
                 valuePeriod=None,
                 valueSampledData=None,
                 valueString=None,
                 value=None,
                 interpretation=None,
                 comments=None,
                 appliesdateTime=None,
                 appliesPeriod=None,
                 applies=None,
                 issued=None,
                 status=None,
                 reliability=None,
                 bodySite=None,
                 method=None,
                 subject=None,
                 specimen=None,
                 referenceRange_low=None,
                 referenceRange_high=None,
                 referenceRange_meaning=None,
                 referenceRange_age=None,
                 related_type=None,
                 related_target=None,
                 performer=None,
                 referenceRange=None,
                 related=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.name = name                                     # , Type of observation (code / type)
        self.valueQuantity = valueQuantity                                     # Quantity, Actual result
        self.valueCodeableConcept = valueCodeableConcept                                     # CodeableConcept, Actual result
        self.valueAttachment = valueAttachment                                     # Attachment, Actual result
        self.valueRatio = valueRatio                                     # Ratio, Actual result
        self.valuePeriod = valuePeriod                                     # Period, Actual result
        self.valueSampledData = valueSampledData                                     # SampledData, Actual result
        self.valueString = valueString                                     # string, Actual result
        self.value = value                                     # , Actual result
        self.interpretation = interpretation                                     # , High, low, normal, etc.
        self.comments = comments                                     # , Comments about result
        self.appliesdateTime = appliesdateTime                                     # dateTime, Physiologically Relevant time/time-period for observation
        self.appliesPeriod = appliesPeriod                                     # Period, Physiologically Relevant time/time-period for observation
        self.applies = applies                                     # , Physiologically Relevant time/time-period for observation
        self.issued = issued                                     # , Date/Time this was made available
        self.status = status                                     # , registered | preliminary | final | amended +
        self.reliability = reliability                                     # , ok | ongoing | early | questionable | calibrating | error +
        self.bodySite = bodySite                                     # , Observed body part
        self.method = method                                     # , How it was done
        self.subject = subject                                     # , Who and/or what this is about
        self.specimen = specimen                                     # , Specimen used for this observation
        self.referenceRange_low = referenceRange_low                                     # , Low Range, if relevant
        self.referenceRange_high = referenceRange_high                                     # , High Range, if relevant
        self.referenceRange_meaning = referenceRange_meaning                                     # , Indicates the meaning/use of this range of this range
        self.referenceRange_age = referenceRange_age                                     # , Applicable age range, if relevant
        self.related_type = related_type                                     # , has-component | has-member | derived-from | sequel-to | replaces | qualified-by | interfered-by
        self.related_target = related_target                                     # , Observation that is related to this one
        
        if performer is None:
            self.performer = []                                     # , { attb['short_desc'] }}
        if referenceRange is None:
            self.referenceRange = []                                     # , { attb['short_desc'] }}
        if related is None:
            self.related = []                                     # , { attb['short_desc'] }}
        

class OperationOutcome(Resource):
    """
    Short Description: Information about the success/failure of an action

    Formal Description: A collection of error, warning or information messages that result from a system action.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param issue_severity: Indicates whether the issue indicates a variation from successful processing.
    :param issue_type: A code indicating the type of error, warning or information message.
    :param issue_details: Additional description of the issue.
    
    :param issue: An error, warning or information message that results from a system action.
    :param issue_location: A simple XPath limited to element names, repetition indicators and the default child access that identifies one of the elements in the resource that caused this issue to be raised.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="OperationOutcome",
                 text=None,
                 issue_severity=None,
                 issue_type=None,
                 issue_details=None,
                 issue=None,
                 issue_location=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.issue_severity = issue_severity                                     # , fatal | error | warning | information
        self.issue_type = issue_type                                     # , Error or warning code
        self.issue_details = issue_details                                     # , Additional description of the issue
        
        if issue is None:
            self.issue = []                                     # , { attb['short_desc'] }}
        if issue_location is None:
            self.issue_location = []                                     # , { attb['short_desc'] }}
        

class Order(Resource):
    """
    Short Description: A request to perform an action

    Formal Description: A request to perform an action.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param date: When the order was made.
    :param subject: Patient this order is about.
    :param source: Who initiated the order.
    :param target: Who is intended to fulfill the order.
    :param reasonCodeableConcept: Text - why the order was made.
    :param reasonResourceReference: Text - why the order was made.
    :param reason: Text - why the order was made.
    :param authority: If required by policy.
    :param when: When order should be fulfilled.
    :param when_code: Code specifies when request should be done. The code may simply be a priority code.
    :param when_schedule: A formal schedule.
    
    :param detail: What action is being ordered.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Order",
                 text=None,
                 date=None,
                 subject=None,
                 source=None,
                 target=None,
                 reasonCodeableConcept=None,
                 reasonResourceReference=None,
                 reason=None,
                 authority=None,
                 when=None,
                 when_code=None,
                 when_schedule=None,
                 detail=None,
                 totalCost=None
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.date = date                                     # , When the order was made
        self.subject = subject                                     # , Patient this order is about
        self.source = source                                     # , Who initiated the order
        self.target = target                                     # , Who is intended to fulfill the order
        self.reasonCodeableConcept = reasonCodeableConcept                                     # CodeableConcept, Text - why the order was made
        self.reasonResourceReference = reasonResourceReference                                     # ResourceReference, Text - why the order was made
        self.reason = reason                                     # , Text - why the order was made
        self.authority = authority                                     # , If required by policy
        self.when = when                                     # , When order should be fulfilled
        self.when_code = when_code                                     # , Code specifies when request should be done. The code may simply be a priority code
        self.when_schedule = when_schedule                                     # , A formal schedule
        self.totalCost = totalCost
        
        if detail is None:
            self.detail = []                                     # , { attb['short_desc'] }}
        else:
            self.detail = detail
        

class DiagnosticOrder(Resource):
    """
    Short Description: A request for a diagnostic service

    Formal Description: A request for a diagnostic investigation service to be performed.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param subject: Who or what the investigation is to be performed on. This is usually a human patient, but diagnostic tests can also be requested on animals, groups of humans or animals, devices such as dialysis machines, or even locations (typically for environmental scans).
    :param orderer: The practitioner that holds legal responsibility for ordering the investigation.
    :param encounter: An encounter that provides additional informaton about the healthcare context in which this request is made.
    :param clinicalNotes: An explanation or justification for why this diagnostic investigation is being requested.
    :param status: The status of the order.
    :param priority: The clinical priority associated with this order.
    :param event_status: The status for the event.
    :param event_description: Additional information about the event that occurred - e.g. if the status remained unchanged.
    :param event_dateTime: The date/time at which the event occurred.
    :param event_actor: The person who was responsible for performing or recording the action.
    :param item_code: A code that identifies a particular diagnostic investigation, or panel of investigations, that have been requested.
    :param item_bodySite: Anatomical location where the request test should be performed.
    :param item_status: The status of this individual item within the order.
    
    :param specimen: One or more specimens that the diagnostic investigation is about.
    :param event: A summary of the events of interest that have occurred as the request is processed. E.g. when the order was made, various processing steps (specimens received), when it was completed.
    :param item: The specific diagnostic investigations that are requested as part of this request. Sometimes, there can only be one item per request, but in most contexts, more than one investigation can be requested.
    :param item_specimen: If the item is related to a specific speciment.
    :param item_event: A summary of the events of interest that have occurred as this item of the request is processed.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="DiagnosticOrder",
                 text=None,
                 subject=None,
                 orderer=None,
                 encounter=None,
                 clinicalNotes=None,
                 status=None,
                 priority=None,
                 event_status=None,
                 event_description=None,
                 event_dateTime=None,
                 event_actor=None,
                 item_code=None,
                 item_bodySite=None,
                 item_status=None,
                 specimen=None,
                 event=None,
                 item=None,
                 item_specimen=None,
                 item_event=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.subject = subject                                     # , Who and/or what test is about
        self.orderer = orderer                                     # , Who ordered the test
        self.encounter = encounter                                     # , The encounter that this diagnostic order is associated with
        self.clinicalNotes = clinicalNotes                                     # , Explanation/Justification for test
        self.status = status                                     # , requested | received | accepted | in progress | review | completed | suspended | rejected | failed
        self.priority = priority                                     # , routine | urgent | stat | asap
        self.event_status = event_status                                     # , requested | received | accepted | in progress | review | completed | suspended | rejected | failed
        self.event_description = event_description                                     # , More information about the event and it's context
        self.event_dateTime = event_dateTime                                     # , The date at which the event happened
        self.event_actor = event_actor                                     # , Who recorded or did this
        self.item_code = item_code                                     # , Code to indicate the item (test or panel) being ordered
        self.item_bodySite = item_bodySite                                     # , Location of requested test (if applicable)
        self.item_status = item_status                                     # , requested | received | accepted | in progress | review | completed | suspended | rejected | failed
        
        if specimen is None:
            self.specimen = []                                     # , { attb['short_desc'] }}
        if event is None:
            self.event = []                                     # , { attb['short_desc'] }}
        if item is None:
            self.item = []                                     # , { attb['short_desc'] }}
        if item_specimen is None:
            self.item_specimen = []                                     # , { attb['short_desc'] }}
        if item_event is None:
            self.item_event = []                                     # , { attb['short_desc'] }}
        

class OrderResponse(Resource):
    """
    Short Description: A response to an order

    Formal Description: A response to an order.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param request: A reference to the order that this is in response to.
    :param date: The date and time at which this order response was made (created/posted).
    :param who: The person, organization, or device credited with making the response.
    :param authorityCodeableConcept: A reference to an authority policy that is the reason for the response. Usually this is used when the order is rejected, to provide a reason for rejection.
    :param authorityResourceReference: A reference to an authority policy that is the reason for the response. Usually this is used when the order is rejected, to provide a reason for rejection.
    :param authority: A reference to an authority policy that is the reason for the response. Usually this is used when the order is rejected, to provide a reason for rejection.
    :param code: What this response says about the status of the original order.
    :param description: Additional description about the response - e.g. a text description provided by a human user when making decisions about the order.
    
    :param fulfillment: Links to resources that provide details of the outcome of performing the order. E.g. Diagnostic Reports in a response that is made to an order that referenced a diagnostic order.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="OrderResponse",
                 text=None,
                 request=None,
                 date=None,
                 who=None,
                 authorityCodeableConcept=None,
                 authorityResourceReference=None,
                 authority=None,
                 code=None,
                 description=None,
                 fulfillment=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.request = request                                     # , The order that this is a response to
        self.date = date                                     # , When the response was made
        self.who = who                                     # , Who made the response
        self.authorityCodeableConcept = authorityCodeableConcept                                     # CodeableConcept, If required by policy
        self.authorityResourceReference = authorityResourceReference                                     # ResourceReference, If required by policy
        self.authority = authority                                     # , If required by policy
        self.code = code                                     # , pending | review | rejected | error | accepted | cancelled | replaced | aborted | complete
        self.description = description                                     # , Additional description of the response
        
        if fulfillment is None:
            self.fulfillment = []                                     # , { attb['short_desc'] }}
        

class Organization(Resource):
    """
    Short Description: A grouping of people or organizations with a common purpose

    Formal Description: A formally or informally recognized grouping of people or organizations formed for the purpose of achieving some form of collective action.  Includes companies, institutions, corporations, departments, community groups, healthcare practice groups, etc.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param name: A name associated with the organization.
    :param type: The kind of organization that this is.
    :param partOf: The organization of which this organization forms a part.
    :param contact_purpose: Indicates a purpose for which the contact can be reached.
    :param contact_name: A name associated with the contact.
    :param contact_address: Visiting or postal addresses for the contact.
    :param contact_gender: Administrative Gender - the gender that the person is considered to have for administration and record keeping purposes.
    :param active: Whether the organization's record is still in active use.
    
    :param telecom: A contact detail for the organization.
    :param address: An address for the organization.
    :param contact: Contact for the organization for a certain purpose.
    :param contact_telecom: A contact detail (e.g. a telephone number or an email address) by which the party may be contacted.
    :param location: Location(s) the organization uses to provide services.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Organization",
                 text=None,
                 name=None,
                 type=None,
                 partOf=None,
                 contact_purpose=None,
                 contact_name=None,
                 contact_address=None,
                 contact_gender=None,
                 active=None,
                 telecom=None,
                 address=None,
                 contact=None,
                 contact_telecom=None,
                 location=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.name = name                                     # , Name used for the organization
        self.type = type                                     # , Kind of organization
        self.partOf = partOf                                     # , The organization of which this organization forms a part
        self.contact_purpose = contact_purpose                                     # , The type of contact
        self.contact_name = contact_name                                     # , A name associated with the contact
        self.contact_address = contact_address                                     # , Visiting or postal addresses for the contact
        self.contact_gender = contact_gender                                     # , Gender for administrative purposes
        self.active = active                                     # , Whether the organization's record is still in active use
        
        if telecom is None:
            self.telecom = []                                     # , { attb['short_desc'] }}
        if address is None:
            self.address = []                                     # , { attb['short_desc'] }}
        if contact is None:
            self.contact = []                                     # , { attb['short_desc'] }}
        if contact_telecom is None:
            self.contact_telecom = []                                     # , { attb['short_desc'] }}
        if location is None:
            self.location = []                                     # , { attb['short_desc'] }}
        

class Other(Resource):
    """
    Short Description: Resource for non-supported content

    Formal Description: Other is a conformant for handling resource concepts not yet defined for FHIR or outside HL7's scope of interest.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param code: Identifies the 'type' of resource - equivalent to the resource name for other resources.
    :param subject: Identifies the patient, practitioner, device or any other resource that is the "focus" of this resoruce.
    :param author: Indicates who was responsible for creating the resource instance.
    :param created: Identifies when the resource was first created.
    
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Other",
                 text=None,
                 code=None,
                 subject=None,
                 author=None,
                 created=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.code = code                                     # , Kind of Resource
        self.subject = subject                                     # , Identifies the
        self.author = author                                     # , Who created
        self.created = created                                     # , When created
        
        

class Patient(Resource):
    """
    Short Description: Information about a person or animal receiving health care services

    Formal Description: Demographics and other administrative information about a person or animal receiving care or other health-related services.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param gender: Administrative Gender - the gender that the patient is considered to have for administration and record keeping purposes.
    :param birthDate: The date and time of birth for the individual.
    :param deceasedboolean: Indicates if the individual is deceased or not.
    :param deceaseddateTime: Indicates if the individual is deceased or not.
    :param deceased: Indicates if the individual is deceased or not.
    :param maritalStatus: This field contains a patient's most recent marital (civil) status.
    :param multipleBirthboolean: Indicates whether the patient is part of a multiple or indicates the actual birth order.
    :param multipleBirthinteger: Indicates whether the patient is part of a multiple or indicates the actual birth order.
    :param multipleBirth: Indicates whether the patient is part of a multiple or indicates the actual birth order.
    :param contact_name: A name associated with the person.
    :param contact_address: Address for the contact person.
    :param contact_gender: Administrative Gender - the gender that the person is considered to have for administration and record keeping purposes.
    :param contact_organization: Organization on behalf of which the contact is acting or for which the contact is working.
    :param animal: This element has a value if the patient is an animal.
    :param animal_species: Identifies the high level categorization of the kind of animal.
    :param animal_breed: Identifies the detailed categorization of the kind of animal.
    :param animal_genderStatus: Indicates the current state of the animal's reproductive organs.
    :param managingOrganization: Organization that is the custodian of the patient record.
    :param link_other: The other patient resource that the link refers to.
    :param link_type: The type of link between this patient resource and another patient resource.
    :param active: Whether this patient record is in active use.
    
    :param name: A name associated with the individual.
    :param telecom: A contact detail (e.g. a telephone number or an email address) by which the individual may be contacted.
    :param address: Addresses for the individual.
    :param photo: Image of the person.
    :param contact: A contact party (e.g. guardian, partner, friend) for the patient.
    :param contact_relationship: The nature of the relationship between the patient and the contact person.
    :param contact_telecom: A contact detail for the person, e.g. a telephone number or an email address.
    :param communication: Languages which may be used to communicate with the patient about his or her health.
    :param careProvider: Patient's nominated care provider.
    :param link: Link to another patient resource that concerns the same actual person.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Patient",
                 text=None,
                 gender=None,
                 birthDate=None,
                 deceasedboolean=None,
                 deceaseddateTime=None,
                 deceased=None,
                 maritalStatus=None,
                 multipleBirthboolean=None,
                 multipleBirthinteger=None,
                 multipleBirth=None,
                 contact_name=None,
                 contact_address=None,
                 contact_gender=None,
                 contact_organization=None,
                 animal=None,
                 animal_species=None,
                 animal_breed=None,
                 animal_genderStatus=None,
                 managingOrganization=None,
                 link_other=None,
                 link_type=None,
                 active=None,
                 name=None,
                 telecom=None,
                 address=None,
                 photo=None,
                 contact=None,
                 contact_relationship=None,
                 contact_telecom=None,
                 communication=None,
                 careProvider=None,
                 link=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.gender = gender                                     # , Gender for administrative purposes
        self.birthDate = birthDate                                     # , The date and time of birth for the individual
        self.deceasedboolean = deceasedboolean                                     # boolean, Indicates if the individual is deceased or not
        self.deceaseddateTime = deceaseddateTime                                     # dateTime, Indicates if the individual is deceased or not
        self.deceased = deceased                                     # , Indicates if the individual is deceased or not
        self.maritalStatus = maritalStatus                                     # , Marital (civil) status of a person
        self.multipleBirthboolean = multipleBirthboolean                                     # boolean, Whether patient is part of a multiple birth
        self.multipleBirthinteger = multipleBirthinteger                                     # integer, Whether patient is part of a multiple birth
        self.multipleBirth = multipleBirth                                     # , Whether patient is part of a multiple birth
        self.contact_name = contact_name                                     # , A name associated with the person
        self.contact_address = contact_address                                     # , Address for the contact person
        self.contact_gender = contact_gender                                     # , Gender for administrative purposes
        self.contact_organization = contact_organization                                     # , Organization that is associated with the contact
        self.animal = animal                                     # , If this patient is an animal (non-human)
        self.animal_species = animal_species                                     # , E.g. Dog, Cow
        self.animal_breed = animal_breed                                     # , E.g. Poodle, Angus
        self.animal_genderStatus = animal_genderStatus                                     # , E.g. Neutered, Intact
        self.managingOrganization = managingOrganization                                     # , Organization that is the custodian of the patient record
        self.link_other = link_other                                     # , The other patient resource that the link refers to
        self.link_type = link_type                                     # , replace | refer | seealso - type of link
        self.active = active                                     # , Whether this patient's record is in active use
        
        if name is None:
            self.name = []                                     # , { attb['short_desc'] }}
        if telecom is None:
            self.telecom = []                                     # , { attb['short_desc'] }}
        if address is None:
            self.address = []                                     # , { attb['short_desc'] }}
        if photo is None:
            self.photo = []                                     # , { attb['short_desc'] }}
        if contact is None:
            self.contact = []                                     # , { attb['short_desc'] }}
        if contact_relationship is None:
            self.contact_relationship = []                                     # , { attb['short_desc'] }}
        if contact_telecom is None:
            self.contact_telecom = []                                     # , { attb['short_desc'] }}
        if communication is None:
            self.communication = []                                     # , { attb['short_desc'] }}
        if careProvider is None:
            self.careProvider = []                                     # , { attb['short_desc'] }}
        if link is None:
            self.link = []                                     # , { attb['short_desc'] }}
        
    def add_careProvider(self, orgclinician):
        self.careProvider.append(orgclinician)

    def get_current_pcp(self):
        #TODO add for loop to look up current pcp
        return "304923812"

    def add_name(self, given, family, use=None, text=None, prefix=None, suffix=None, period=None):
        patient_name = HumanName()
        patient_name.family.append(family)
        patient_name.given.append(given)
        self.name.append(patient_name)

    def get_name(self):

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
    """
    Short Description: A person with a  formal responsibility in the provisioning of healthcare or related services

    Formal Description: A person who is directly or indirectly involved in the provisioning of healthcare.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param name: A name associated with the person.
    :param address: The postal address where the practitioner can be found or visited or to which mail can be delivered.
    :param gender: Administrative Gender - the gender that the person is considered to have for administration and record keeping purposes.
    :param birthDate: The date and time of birth for the practitioner.
    :param organization: The organization that the practitioner represents.
    :param period: The period during which the person is authorized to act as a practitioner in these role(s) for the organization.
    :param qualification_code: Coded representation of the qualification.
    :param qualification_period: Period during which the qualification is valid.
    :param qualification_issuer: Organization that regulates and issues the qualification.
    
    :param telecom: A contact detail for the practitioner, e.g. a telephone number or an email address.
    :param photo: Image of the person.
    :param role: Roles which this practitioner is authorized to perform for the organization.
    :param specialty: Specific specialty of the practitioner.
    :param location: The location(s) at which this practitioner provides care.
    :param qualification: Qualifications obtained by training and certification.
    :param communication: A language the practitioner is able to use in patient communication.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Practitioner",
                 text=None,
                 name=None,
                 address=None,
                 gender=None,
                 birthDate=None,
                 organization=None,
                 period=None,
                 qualification_code=None,
                 qualification_period=None,
                 qualification_issuer=None,
                 telecom=None,
                 photo=None,
                 role=None,
                 specialty=None,
                 location=None,
                 qualification=None,
                 communication=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.name = name                                     # , A name associated with the person
        self.address = address                                     # , Where practitioner can be found/visited
        self.gender = gender                                     # , Gender for administrative purposes
        self.birthDate = birthDate                                     # , The date and time of birth for the practitioner
        self.organization = organization                                     # , The represented organization
        self.period = period                                     # , The period during which the practitioner is authorized to perform in these role(s)
        self.qualification_code = qualification_code                                     # , Coded representation of the qualification
        self.qualification_period = qualification_period                                     # , Period during which the qualification is valid
        self.qualification_issuer = qualification_issuer                                     # , Organization that regulates and issues the qualification
        
        if telecom is None:
            self.telecom = []                                     # , { attb['short_desc'] }}
        if photo is None:
            self.photo = []                                     # , { attb['short_desc'] }}
        if role is None:
            self.role = []                                     # , { attb['short_desc'] }}
        if specialty is None:
            self.specialty = []                                     # , { attb['short_desc'] }}
        if location is None:
            self.location = []                                     # , { attb['short_desc'] }}
        if qualification is None:
            self.qualification = []                                     # , { attb['short_desc'] }}
        if communication is None:
            self.communication = []                                     # , { attb['short_desc'] }}
        

class Procedure(Resource):
    """
    Short Description: An action that is performed on a patient

    Formal Description: An action that is performed on a patient. This can be a physical 'thing' like an operation, or less invasive like counseling or hypnotherapy.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param subject: The person on whom the procedure was performed.
    :param type: The specific procedure that is performed. Use text if the exact nature of the procedure can't be coded.
    :param performer_person: The practitioner who was involved in the procedure.
    :param performer_role: E.g. surgeon, anaethetist, endoscopist.
    :param date: The dates over which the procedure was performed. Allows a period to support complex procedures that span more that one date, and also allows for the length of the procedure to be captured.
    :param encounter: The encounter during which the procedure was performed.
    :param outcome: What was the outcome of the procedure - did it resolve reasons why the procedure was performed?.
    :param followUp: If the procedure required specific follow up - e.g. removal of sutures. The followup may be represented as a simple note, or potentially could be more complex in which case the CarePlan resource can be used.
    :param relatedItem_type: The nature of the relationship.
    :param relatedItem_target: The related item - e.g. a procedure.
    :param notes: Any other notes about the procedure - e.g. the operative notes.
    
    :param bodySite: Detailed and structured anatomical location information. Multiple locations are allowed - e.g. multiple punch biopsies of a lesion.
    :param indication: The reason why the procedure was performed. This may be due to a Condition, may be coded entity of some type, or may simply be present as text.
    :param performer: Limited to 'real' people rather than equipment.
    :param report: This could be a histology result. There could potentially be multiple reports - e.g. if this was a procedure that made multiple biopsies.
    :param complication: Any complications that occurred during the procedure, or in the immediate post-operative period. These are generally tracked separately from the notes, which typically will describe the procedure itself rather than any 'post procedure' issues.
    :param relatedItem: Procedures may be related to other items such as procedures or medications. For example treating wound dehiscence following a previous procedure.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Procedure",
                 text=None,
                 subject=None,
                 type=None,
                 performer_person=None,
                 performer_role=None,
                 date=None,
                 encounter=None,
                 outcome=None,
                 followUp=None,
                 relatedItem_type=None,
                 relatedItem_target=None,
                 notes=None,
                 bodySite=None,
                 indication=None,
                 performer=None,
                 report=None,
                 complication=None,
                 relatedItem=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.subject = subject                                     # , Who procedure was performed on
        self.type = type                                     # , Identification of the procedure
        self.performer_person = performer_person                                     # , The reference to the practitioner
        self.performer_role = performer_role                                     # , The role the person was in
        self.date = date                                     # , The date the procedure was performed
        self.encounter = encounter                                     # , The encounter when procedure performed
        self.outcome = outcome                                     # , What was result of procedure?
        self.followUp = followUp                                     # , Instructions for follow up
        self.relatedItem_type = relatedItem_type                                     # , caused-by | because-of
        self.relatedItem_target = relatedItem_target                                     # , The related item - e.g. a procedure
        self.notes = notes                                     # , Additional information about procedure
        
        if bodySite is None:
            self.bodySite = []                                     # , { attb['short_desc'] }}
        if indication is None:
            self.indication = []                                     # , { attb['short_desc'] }}
        if performer is None:
            self.performer = []                                     # , { attb['short_desc'] }}
        if report is None:
            self.report = []                                     # , { attb['short_desc'] }}
        if complication is None:
            self.complication = []                                     # , { attb['short_desc'] }}
        if relatedItem is None:
            self.relatedItem = []                                     # , { attb['short_desc'] }}
        

class Profile(Resource):
    """
    Short Description: Resource Profile

    Formal Description: A Resource Profile - a statement of use of one or more FHIR Resources.  It may include constraints on Resources and Data Types, Terminology Binding Statements and Extension Definitions.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param version: The identifier that is used to identify this version of the profile when it is referenced in a specification, model, design or instance. This is an arbitrary value managed by the profile author manually and the value should be a timestamp.
    :param name: A free text natural language name identifying the Profile.
    :param publisher: Details of the individual or organization who accepts responsibility for publishing the profile.
    :param description: A free text natural language description of the profile and its use.
    :param status: The status of the profile.
    :param experimental: This profile was authored for testing purposes (or education/evaluation/marketing), and is not intended to be used for genuine usage.
    :param date: The date that this version of the profile was published.
    :param requirements: The Scope and Usage that this profile was created to meet.
    :param fhirVersion: The version of the FHIR specification on which this profile is based.
    :param mapping_identity: An Internal id that is used to identify this mapping set when specific mappings are made.
    :param mapping_uri: A URI that identifies the specification that this mapping is expressed to.
    :param mapping_name: A name for the specification that is being mapped to.
    :param mapping_comments: Comments about this mapping, including version notes, issues, scope limitations, and other important notes for usage.
    :param structure_type: The Resource or Data type being described.
    :param structure_name: The name of this resource constraint statement (to refer to it from other resource constraints - from Profile.structure.element.definition.type.profile).
    :param structure_publish: This definition of a profile on a structure is published as a formal statement. Some structural definitions might be defined purely for internal use within the profile, and not intended to be used outside that context.
    :param structure_purpose: Human summary: why describe this resource?.
    :param structure_element_path: The path identifies the element and is expressed as a "."-separated list of ancestor elements, beginning with the name of the resource.
    :param structure_element_name: The name of this element definition (to refer to it from other element definitions using Profile.structure.element.definition.nameReference). This is a unique name referring to a specific set of constraints applied to this element. One use of this is to provide a name to different slices of the same element.
    :param structure_element_slicing: Indicates that the element is sliced into a set of alternative definitions (there are multiple definitions on a single element in the base resource). The set of slices is any elements that come after this in the element sequence that have the same path, until a shorter path occurs (the shorter path terminates the set).
    :param structure_element_definition: Definition of the content of the element to provide a more specific definition than that contained for the element in the base resource.
    :param structure_searchParam_name: The name of the standard or custom search parameter.
    :param structure_searchParam_type: The type of value a search parameter refers to, and how the content is interpreted.
    :param structure_searchParam_documentation: A specification for search parameters. For standard parameters, provides additional information on how the parameter is used in this solution.  For custom parameters, provides a description of what the parameter does.
    :param structure_searchParam_path: An XPath expression that returns a set of elements for the search parameter.
    :param query_name: The name of a query, which is used in the URI from Conformance statements declaring use of the query.  Typically this will also be the name for the _query parameter when the query is called, though in some cases it may be aliased by a server to avoid collisions.
    :param query_documentation: Description of the query - the functionality it offers, and considerations about how it functions and to use it.
    
    :param telecom: Contact details to assist a user in finding and communicating with the publisher.
    :param code: A set of terms from external terminologies that may be used to assist with indexing and searching of templates.
    :param mapping: An external specification that the content is mapped to.
    :param structure: A constraint statement about what contents a resource or data type may have.
    :param structure_element: Captures constraints on each element within the resource.
    :param structure_searchParam: Additional search parameters for implementations to support and/or make use of.
    :param query: Definition of a named query and its parameters and their meaning.
    :param query_parameter: A parameter of a named query.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Profile",
                 text=None,
                 version=None,
                 name=None,
                 publisher=None,
                 description=None,
                 status=None,
                 experimental=None,
                 date=None,
                 requirements=None,
                 fhirVersion=None,
                 mapping_identity=None,
                 mapping_uri=None,
                 mapping_name=None,
                 mapping_comments=None,
                 structure_type=None,
                 structure_name=None,
                 structure_publish=None,
                 structure_purpose=None,
                 structure_element_path=None,
                 structure_element_name=None,
                 structure_element_slicing=None,
                 structure_element_definition=None,
                 structure_searchParam_name=None,
                 structure_searchParam_type=None,
                 structure_searchParam_documentation=None,
                 structure_searchParam_path=None,
                 query_name=None,
                 query_documentation=None,
                 telecom=None,
                 code=None,
                 mapping=None,
                 structure=None,
                 structure_element=None,
                 structure_searchParam=None,
                 query=None,
                 query_parameter=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.version = version                                     # , Logical id for this version of the profile
        self.name = name                                     # , Informal name for this profile
        self.publisher = publisher                                     # , Name of the publisher (Organization or individual)
        self.description = description                                     # , Natural language description of the profile
        self.status = status                                     # , draft | active | retired
        self.experimental = experimental                                     # , If for testing purposes, not real usage
        self.date = date                                     # , Date for this version of the profile
        self.requirements = requirements                                     # , Scope and Usage this profile is for
        self.fhirVersion = fhirVersion                                     # , FHIR Version this profile targets
        self.mapping_identity = mapping_identity                                     # , Internal id when this mapping is used
        self.mapping_uri = mapping_uri                                     # , Identifies what this mapping refers to
        self.mapping_name = mapping_name                                     # , Names what this mapping refers to
        self.mapping_comments = mapping_comments                                     # , Versions, Issues, Scope limitations etc
        self.structure_type = structure_type                                     # , The Resource or Data Type being described
        self.structure_name = structure_name                                     # , Name for this particular structure (reference target)
        self.structure_publish = structure_publish                                     # , This definition is published (i.e. for validation)
        self.structure_purpose = structure_purpose                                     # , Human summary: why describe this resource?
        self.structure_element_path = structure_element_path                                     # , The path of the element (see the formal definitions)
        self.structure_element_name = structure_element_name                                     # , Name for this particular element definition (reference target)
        self.structure_element_slicing = structure_element_slicing                                     # , This element is sliced - slices follow
        self.structure_element_definition = structure_element_definition                                     # , More specific definition of the element
        self.structure_searchParam_name = structure_searchParam_name                                     # , Name of search parameter
        self.structure_searchParam_type = structure_searchParam_type                                     # , number | date | string | token | reference | composite | quantity
        self.structure_searchParam_documentation = structure_searchParam_documentation                                     # , Contents and meaning of search parameter
        self.structure_searchParam_path = structure_searchParam_path                                     # , XPath that extracts the parameter set
        self.query_name = query_name                                     # , Special named queries (_query=)
        self.query_documentation = query_documentation                                     # , Describes the named query
        
        if telecom is None:
            self.telecom = []                                     # , { attb['short_desc'] }}
        if code is None:
            self.code = []                                     # , { attb['short_desc'] }}
        if mapping is None:
            self.mapping = []                                     # , { attb['short_desc'] }}
        if structure is None:
            self.structure = []                                     # , { attb['short_desc'] }}
        if structure_element is None:
            self.structure_element = []                                     # , { attb['short_desc'] }}
        if structure_searchParam is None:
            self.structure_searchParam = []                                     # , { attb['short_desc'] }}
        if query is None:
            self.query = []                                     # , { attb['short_desc'] }}
        if query_parameter is None:
            self.query_parameter = []                                     # , { attb['short_desc'] }}
        

class Provenance(Resource):
    """
    Short Description: Who, What, When for a set of resources

    Formal Description: Provenance information that describes the activity that led to the creation of a set of resources. This information can be used to help determine their reliability or trace where the information in them came from. The focus of the provenance resource is record keeping, audit and traceability, and not explicit statements of clinical significance.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param period: The period during which the activity occurred.
    :param recorded: The instant of time at which the activity was recorded.
    :param reason: The reason that the activity was taking place.
    :param location: Where the activity occurred, if relevant.
    :param agent_role: The role that the participant played.
    :param agent_type: The type of the participant.
    :param agent_reference: Identity of participant. May be a logical or physical uri and maybe absolute or relative.
    :param agent_display: Human-readable description of the participant.
    :param entity_role: How the entity was used during the activity.
    :param entity_type: The type of the entity. If the entity is a resource, then this is a resource type.
    :param entity_reference: Identity of participant. May be a logical or physical uri and maybe absolute or relative.
    :param entity_display: Human-readable description of the entity.
    :param entity_agent: The entity is attributed to an agent to express the agent's responsibility for that entity, possibly along with other agents. This description can be understood as shorthand for saying that the agent was responsible for the activity which generated the entity.
    :param integritySignature: A digital signature on the target resource(s). The signature should match a Provenance.agent.reference in the provenance resource. The signature is only added to support checking cryptographic integrity of the resource, and not to represent workflow and clinical aspects of the signing process, or to support non-repudiation.
    
    :param target: The resource(s) that were generated by  the activity described in this resource. A provenance can point to more than one target if multiple resources were created/updated by the same activity.
    :param policy: Policy or plan the activity was defined by. Typically, a single activity may have multiple applicable policy documents, such as patient consent, guarantor funding, etc.
    :param agent: An agent takes a role in an activity such that the agent can be assigned some degree of responsibility for the activity taking place. An agent can be a person, a piece of software, an inanimate object, an organization, or other entities that may be ascribed responsibility.
    :param entity: An entity used in this activity.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Provenance",
                 text=None,
                 period=None,
                 recorded=None,
                 reason=None,
                 location=None,
                 agent_role=None,
                 agent_type=None,
                 agent_reference=None,
                 agent_display=None,
                 entity_role=None,
                 entity_type=None,
                 entity_reference=None,
                 entity_display=None,
                 entity_agent=None,
                 integritySignature=None,
                 target=None,
                 policy=None,
                 agent=None,
                 entity=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.period = period                                     # , When the activity occurred
        self.recorded = recorded                                     # , When the activity was recorded / updated
        self.reason = reason                                     # , Reason the activity is occurring
        self.location = location                                     # , Where the activity occurred, if relevant
        self.agent_role = agent_role                                     # , e.g. author | overseer | enterer | attester | source | cc: +
        self.agent_type = agent_type                                     # , e.g. Resource | Person | Application | Record | Document +
        self.agent_reference = agent_reference                                     # , Identity of agent (urn or url)
        self.agent_display = agent_display                                     # , Human description of participant
        self.entity_role = entity_role                                     # , derivation | revision | quotation | source
        self.entity_type = entity_type                                     # , Resource Type, or something else
        self.entity_reference = entity_reference                                     # , Identity of participant (urn or url)
        self.entity_display = entity_display                                     # , Human description of participant
        self.entity_agent = entity_agent                                     # , Entity is attributed to this agent
        self.integritySignature = integritySignature                                     # , Base64 signature (DigSig) - integrity check
        
        if target is None:
            self.target = []                                     # , { attb['short_desc'] }}
        if policy is None:
            self.policy = []                                     # , { attb['short_desc'] }}
        if agent is None:
            self.agent = []                                     # , { attb['short_desc'] }}
        if entity is None:
            self.entity = []                                     # , { attb['short_desc'] }}
        

class Query(Resource):
    """
    Short Description: A description of a query with a set of parameters

    Formal Description: A description of a query with a set of parameters.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param response: If this is a response to a query.
    :param response_outcome: Outcome of processing the query.
    :param response_total: Total number of matching records.
    
    :param parameter: Set of query parameters with values.
    :param response_parameter: Parameters server used.
    :param response_first: To get first page (if paged).
    :param response_previous: To get previous page (if paged).
    :param response_next: To get next page (if paged).
    :param response_last: To get last page (if paged).
    :param response_reference: Resources that are the results of the search.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Query",
                 text=None,
                 response=None,
                 response_outcome=None,
                 response_total=None,
                 parameter=None,
                 response_parameter=None,
                 response_first=None,
                 response_previous=None,
                 response_next=None,
                 response_last=None,
                 response_reference=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.response = response                                     # , If this is a response to a query
        self.response_outcome = response_outcome                                     # , ok | limited | refused | error
        self.response_total = response_total                                     # , Total number of matching records
        
        if parameter is None:
            self.parameter = []                                     # , { attb['short_desc'] }}
        if response_parameter is None:
            self.response_parameter = []                                     # , { attb['short_desc'] }}
        if response_first is None:
            self.response_first = []                                     # , { attb['short_desc'] }}
        if response_previous is None:
            self.response_previous = []                                     # , { attb['short_desc'] }}
        if response_next is None:
            self.response_next = []                                     # , { attb['short_desc'] }}
        if response_last is None:
            self.response_last = []                                     # , { attb['short_desc'] }}
        if response_reference is None:
            self.response_reference = []                                     # , { attb['short_desc'] }}
        

class Questionnaire(Resource):
    """
    Short Description: A structured set of questions and their answers

    Formal Description: A structured set of questions and their answers. The Questionnaire may contain questions, answers or both. The questions are ordered and grouped into coherent subsets, corresponding to the structure of the grouping of the underlying questions.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param status: The lifecycle status of the questionnaire as a whole.
    :param authored: The date and/or time that this version of the questionnaire was authored.
    :param subject: The subject of the questionnaires: this is the patient that the answers apply to, but this person is not necessarily the source of information.
    :param author: Person who received the answers to the questions in the Questionnaire and recorded them in the system.
    :param source: The person who answered the questions about the subject. Only used when this is not the subject him/herself.
    :param name: Structured name for a predefined list of questions this questionnaire is responding to.
    :param encounter: Encounter during which this questionnaire answers were collected. When there were multiple encounters, this is the one considered most relevant to the context of the answers.
    :param group: A group of questions to a possibly similarly grouped set of questions in the questionnaire.
    :param group_name: Structured name for a section of a predefined list of questions this questionnaire is responding to.
    :param group_header: Text that is displayed above the contents of the group.
    :param group_text: Additional text for the group, used for display purposes.
    :param group_subject: More specific subject this section's answers are about, details the subject given in Questionnaire.
    :param group_question_name: Structured name for the question that identifies this question within the Questionnaire or Group.
    :param group_question_text: Text of the question as it is shown to the user.
    :param group_question_answer: Single-valued answer to the question.
    :param group_question_options: Reference to a valueset containing the possible options.
    :param group_question_data: Structured answer in the form of a FHIR Resource or datatype.
    :param group_question_remarks: The remark contains information about the answer given. This is additional information about the answer the author wishes to convey, but should not be used to contain information that is part of the answer itself.
    
    :param group_group: A sub-group within a group. The ordering of groups within this group is relevant.
    :param group_question: Set of questions within this group. The order of questions within the group is relevant.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Questionnaire",
                 text=None,
                 status=None,
                 authored=None,
                 subject=None,
                 author=None,
                 source=None,
                 name=None,
                 encounter=None,
                 group=None,
                 group_name=None,
                 group_header=None,
                 group_text=None,
                 group_subject=None,
                 group_question_name=None,
                 group_question_text=None,
                 group_question_answer=None,
                 group_question_options=None,
                 group_question_data=None,
                 group_question_remarks=None,
                 group_group=None,
                 group_question=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.status = status                                     # , draft | published | retired | in progress | completed | amended
        self.authored = authored                                     # , Date this version was authored
        self.subject = subject                                     # , The subject of the questions
        self.author = author                                     # , Person who received and recorded the answers
        self.source = source                                     # , The person who answered the questions
        self.name = name                                     # , Name/code for a predefined list of questions
        self.encounter = encounter                                     # , Primary encounter during which the answers were collected
        self.group = group                                     # , Grouped questions
        self.group_name = group_name                                     # , Code or name of the section on a questionnaire
        self.group_header = group_header                                     # , Text that is displayed above the contents of the group
        self.group_text = group_text                                     # , Additional text for the group
        self.group_subject = group_subject                                     # , The subject this group's answers are about
        self.group_question_name = group_question_name                                     # , Code or name of the question
        self.group_question_text = group_question_text                                     # , Text of the question as it is shown to the user
        self.group_question_answer = group_question_answer                                     # , Single-valued answer to the question
        self.group_question_options = group_question_options                                     # , Valueset containing the possible options
        self.group_question_data = group_question_data                                     # , Structured answer
        self.group_question_remarks = group_question_remarks                                     # , Remarks about the answer given
        
        if group_group is None:
            self.group_group = []                                     # , { attb['short_desc'] }}
        if group_question is None:
            self.group_question = []                                     # , { attb['short_desc'] }}
        

class RelatedPerson(Resource):
    """
    Short Description: An person that is related to a patient, but who is not a direct target of care

    Formal Description: Information about a person that is involved in the care for a patient, but who is not the target of healthcare, nor has a formal responsibility in the care process.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param patient: The patient this person is related to.
    :param relationship: The nature of the relationship between a patient and the related person.
    :param name: A name associated with the person.
    :param gender: Administrative Gender - the gender that the person is considered to have for administration and record keeping purposes.
    :param address: Address where the related person can be contacted or visited.
    
    :param telecom: A contact detail for the person, e.g. a telephone number or an email address.
    :param photo: Image of the person.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="RelatedPerson",
                 text=None,
                 patient=None,
                 relationship=None,
                 name=None,
                 gender=None,
                 address=None,
                 telecom=None,
                 photo=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.patient = patient                                     # , The patient this person is related to
        self.relationship = relationship                                     # , The nature of the relationship
        self.name = name                                     # , A name associated with the person
        self.gender = gender                                     # , Gender for administrative purposes
        self.address = address                                     # , Address where the related person can be contacted or visited
        
        if telecom is None:
            self.telecom = []                                     # , { attb['short_desc'] }}
        if photo is None:
            self.photo = []                                     # , { attb['short_desc'] }}
        

class SecurityEvent(Resource):
    """
    Short Description: Event record kept for security purposes

    Formal Description: A record of an event made for purposes of maintaining a security log. Typical uses include detection of intrusion attempts and monitoring for inappropriate usage.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param event: Identifies the name, action type, time, and disposition of the audited event.
    :param event_type: Identifier for a family of the event.
    :param event_action: Indicator for type of action performed during the event that generated the audit.
    :param event_dateTime: The time when the event occurred on the source.
    :param event_outcome: Indicates whether the event succeeded or failed.
    :param event_outcomeDesc: A free text description of the outcome of the event.
    :param participant_reference: Direct reference to a resource that identifies the participant.
    :param participant_userId: Unique identifier for the user actively participating in the event.
    :param participant_altId: Alternative Participant Identifier. For a human, this should be a user identifier text string from authentication system. This identifier would be one known to a common authentication system (e.g., single sign-on), if available.
    :param participant_name: Human-meaningful name for the user.
    :param participant_requestor: Indicator that the user is or is not the requestor, or initiator, for the event being audited.
    :param participant_media: Type of media involved. Used when the event is about exporting/importing onto media.
    :param participant_network: Logical network location for application activity, if the activity has a network location.
    :param participant_network_type: An identifier for the type of network access point that originated the audit event.
    :param source: Application systems and processes.
    :param source_site: Logical source location within the healthcare enterprise network.
    :param object_reference: Identifies a specific instance of the participant object. The reference should always be version specific.
    :param object_type: Object type being audited.
    :param object_role: Code representing the functional application role of Participant Object being audited.
    :param object_lifecycle: Identifier for the data life-cycle stage for the participant object.
    :param object_sensitivity: Denotes policy-defined sensitivity for the Participant Object ID such as VIP, HIV status, mental health status or similar topics.
    :param object_name: An instance-specific descriptor of the Participant Object ID audited, such as a person's name.
    :param object_description: Text that describes the object in more detail.
    :param object_query: The actual query for a query-type participant object.
    :param object_detail_type: Name of the property.
    :param object_detail_value: Property value.
    
    :param event_subtype: Identifier for the category of event.
    :param participant: A person, a hardware device or software process.
    :param participant_role: Specification of the role(s) the user plays when performing the event. Usually the codes used in this element are local codes defined by the role-based access control security system used in the local context.
    :param source_type: Code specifying the type of source where event originated.
    :param object: Specific instances of data or objects that have been accessed.
    :param object_detail: Additional Information about the Object.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="SecurityEvent",
                 text=None,
                 event=None,
                 event_type=None,
                 event_action=None,
                 event_dateTime=None,
                 event_outcome=None,
                 event_outcomeDesc=None,
                 participant_reference=None,
                 participant_userId=None,
                 participant_altId=None,
                 participant_name=None,
                 participant_requestor=None,
                 participant_media=None,
                 participant_network=None,
                 participant_network_type=None,
                 source=None,
                 source_site=None,
                 object_reference=None,
                 object_type=None,
                 object_role=None,
                 object_lifecycle=None,
                 object_sensitivity=None,
                 object_name=None,
                 object_description=None,
                 object_query=None,
                 object_detail_type=None,
                 object_detail_value=None,
                 event_subtype=None,
                 participant=None,
                 participant_role=None,
                 source_type=None,
                 object=None,
                 object_detail=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.event = event                                     # , What was done
        self.event_type = event_type                                     # , Type/identifier of event
        self.event_action = event_action                                     # , Type of action performed during the event
        self.event_dateTime = event_dateTime                                     # , Time when the event occurred on source
        self.event_outcome = event_outcome                                     # , Whether the event succeeded or failed
        self.event_outcomeDesc = event_outcomeDesc                                     # , Description of the event outcome
        self.participant_reference = participant_reference                                     # , Direct reference to resource
        self.participant_userId = participant_userId                                     # , Unique identifier for the user
        self.participant_altId = participant_altId                                     # , Alternative User id e.g. authentication
        self.participant_name = participant_name                                     # , Human-meaningful name for the user
        self.participant_requestor = participant_requestor                                     # , Whether user is initiator
        self.participant_media = participant_media                                     # , Type of media
        self.participant_network = participant_network                                     # , Logical network location for application activity
        self.participant_network_type = participant_network_type                                     # , The type of network access point
        self.source = source                                     # , Application systems and processes
        self.source_site = source_site                                     # , Logical source location within the enterprise
        self.object_reference = object_reference                                     # , Specific instance of resource (e.g. versioned)
        self.object_type = object_type                                     # , Object type being audited
        self.object_role = object_role                                     # , Functional application role of Object
        self.object_lifecycle = object_lifecycle                                     # , Life-cycle stage for the object
        self.object_sensitivity = object_sensitivity                                     # , Policy-defined sensitivity for the object
        self.object_name = object_name                                     # , Instance-specific descriptor for Object
        self.object_description = object_description                                     # , Descriptive text
        self.object_query = object_query                                     # , Actual query for object
        self.object_detail_type = object_detail_type                                     # , Name of the property
        self.object_detail_value = object_detail_value                                     # , Property value
        
        if event_subtype is None:
            self.event_subtype = []                                     # , { attb['short_desc'] }}
        if participant is None:
            self.participant = []                                     # , { attb['short_desc'] }}
        if participant_role is None:
            self.participant_role = []                                     # , { attb['short_desc'] }}
        if source_type is None:
            self.source_type = []                                     # , { attb['short_desc'] }}
        if object is None:
            self.object = []                                     # , { attb['short_desc'] }}
        if object_detail is None:
            self.object_detail = []                                     # , { attb['short_desc'] }}
        

class Specimen(Resource):
    """
    Short Description: Sample for analysis

    Formal Description: Sample for analysis.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param type: Kind of material that forms the specimen.
    :param source_relationship: Whether this relationship is to a parent or to a child.
    :param subject: Where the specimen came from. This may be the patient(s) or from the environment or  a device.
    :param accessionIdentifier: The identifier assigned by the lab when accessioning specimen(s). This is not necessarily the same as the specimen identifier, depending on local lab procedures.
    :param receivedTime: Time when specimen was received for processing or testing.
    :param collection: Details concerning the specimen collection.
    :param collection_collector: Person who collected the specimen.
    :param collection_collected: Time when specimen was collected from subject - the physiologically relevant time.
    :param collection_quantity: The quantity of specimen collected; for instance the volume of a blood sample, or the physical measurement of an anatomic pathology sample.
    :param collection_method: A coded value specifying the technique that is used to perform the procedure.
    :param collection_sourceSite: Anatomical location from which the specimen should be collected (if subject is a patient). This element is not used for environmental specimens.
    :param treatment_description: Textual description of procedure.
    :param treatment_procedure: A coded value specifying the procedure used to process the specimen.
    :param container_description: Textual description of the container.
    :param container_type: The type of container associated with the specimen (e.g. slide, aliquot, etc).
    :param container_capacity: The capacity (volume or other measure) the container may contain.
    :param container_specimenQuantity: The quantity of specimen in the container; may be volume, dimensions, or other appropriate measurements, depending on the specimen type.
    :param container_additive: Additive associated with the container.
    
    :param source: Parent specimen from which the focal specimen was a component.
    :param source_target: The specimen resource that is the target of this relationship.
    :param collection_comment: To communicate any details or issues encountered during the specimen collection procedure.
    :param treatment: Details concerning treatment and processing steps for the specimen.
    :param treatment_additive: Material used in the processing step.
    :param container: The container holding the specimen.  The recursive nature of containers; i.e. blood in tube in tray in rack is not addressed here.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Specimen",
                 text=None,
                 type=None,
                 source_relationship=None,
                 subject=None,
                 accessionIdentifier=None,
                 receivedTime=None,
                 collection=None,
                 collection_collector=None,
                 collection_collected=None,
                 collection_quantity=None,
                 collection_method=None,
                 collection_sourceSite=None,
                 treatment_description=None,
                 treatment_procedure=None,
                 container_description=None,
                 container_type=None,
                 container_capacity=None,
                 container_specimenQuantity=None,
                 container_additive=None,
                 source=None,
                 source_target=None,
                 collection_comment=None,
                 treatment=None,
                 treatment_additive=None,
                 container=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.type = type                                     # , Kind of material that forms the specimen
        self.source_relationship = source_relationship                                     # , parent | child
        self.subject = subject                                     # , Where the specimen came from. This may be the patient(s) or from the environment or  a device
        self.accessionIdentifier = accessionIdentifier                                     # , Identifier assigned by the lab
        self.receivedTime = receivedTime                                     # , The time when specimen was received for processing
        self.collection = collection                                     # , Collection details
        self.collection_collector = collection_collector                                     # , Who collected the specimen
        self.collection_collected = collection_collected                                     # , Collection time
        self.collection_quantity = collection_quantity                                     # , The quantity of specimen collected
        self.collection_method = collection_method                                     # , Technique used to perform collection
        self.collection_sourceSite = collection_sourceSite                                     # , Anatomical collection site
        self.treatment_description = treatment_description                                     # , Textual description of procedure
        self.treatment_procedure = treatment_procedure                                     # , Indicates the treatment or processing step  applied to the specimen
        self.container_description = container_description                                     # , Textual description of the container
        self.container_type = container_type                                     # , Kind of container directly associated with specimen
        self.container_capacity = container_capacity                                     # , Container volume or size
        self.container_specimenQuantity = container_specimenQuantity                                     # , Quantity of specimen within container
        self.container_additive = container_additive                                     # , Additive associated with container
        
        if source is None:
            self.source = []                                     # , { attb['short_desc'] }}
        if source_target is None:
            self.source_target = []                                     # , { attb['short_desc'] }}
        if collection_comment is None:
            self.collection_comment = []                                     # , { attb['short_desc'] }}
        if treatment is None:
            self.treatment = []                                     # , { attb['short_desc'] }}
        if treatment_additive is None:
            self.treatment_additive = []                                     # , { attb['short_desc'] }}
        if container is None:
            self.container = []                                     # , { attb['short_desc'] }}
        

class Substance(Resource):
    """
    Short Description: A homogeneous material with a definite composition

    Formal Description: A homogeneous material with a definite composition.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param type: A code (or set of codes) that identify this substance.
    :param description: A description of the substance - its appearance, handling requirements, and other usage notes.
    :param instance: Substance may be used to describe a kind of substance, or a specific package/container of the substance: an instance.
    :param instance_expiry: When the substance is no longer valid to use. For some substances, a single arbitrary date is used for expiry.
    :param instance_quantity: The amount of the substance.
    :param ingredient_quantity: The amount of the ingredient in the substance - a concentration ratio.
    :param ingredient_substance: Another substance that is a component of this substance.
    
    :param ingredient: A substance can be composed of other substances.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Substance",
                 text=None,
                 type=None,
                 description=None,
                 instance=None,
                 instance_expiry=None,
                 instance_quantity=None,
                 ingredient_quantity=None,
                 ingredient_substance=None,
                 ingredient=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.type = type                                     # , What kind of substance this is
        self.description = description                                     # , Textual description of the substance, comments
        self.instance = instance                                     # , If this describes a specific package/container of the substance
        self.instance_expiry = instance_expiry                                     # , When no longer valid to use
        self.instance_quantity = instance_quantity                                     # , Amount of substance in the package
        self.ingredient_quantity = ingredient_quantity                                     # , Optional amount (concentration)
        self.ingredient_substance = ingredient_substance                                     # , A component of the substance
        
        if ingredient is None:
            self.ingredient = []                                     # , { attb['short_desc'] }}
        

class Supply(Resource):
    """
    Short Description: A supply -  request and provision

    Formal Description: A supply - a  request for something, and provision of what is supplied.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param kind: Category of supply, e.g.  central, non-stock, etc. This is used to support work flows associated with the supply process.
    :param status: Status of the supply request.
    :param orderedItem: The item that is requested to be supplied.
    :param patient: A link to a resource representing the person whom the ordered item is for.
    :param dispense_status: A code specifying the state of the dispense event.
    :param dispense_type: Indicates the type of dispensing event that is performed. Examples include: Trial Fill, Completion of Trial, Partial Fill, Emergency Fill, Samples, etc.
    :param dispense_quantity: The amount of supply that has been dispensed. Includes unit of measure.
    :param dispense_suppliedItem: Identifies the medication or substance being dispensed. This is either a link to a resource representing the details of the medication or substance or a simple attribute carrying a code that identifies the medication from a known list of medications.
    :param dispense_supplier: The individual responsible for dispensing the medication.
    :param dispense_whenPrepared: The time the dispense event occurred.
    :param dispense_whenHandedOver: The time the dispensed item was sent or handed to the patient (or agent).
    :param dispense_destination: Identification of the facility/location where the Supply was shipped to, as part of the dispense event.
    
    :param dispense: Indicates the details of the dispense event such as the days supply and quantity of a supply dispensed.
    :param dispense_receiver: Identifies the person who picked up the Supply.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="Supply",
                 text=None,
                 kind=None,
                 status=None,
                 orderedItem=None,
                 patient=None,
                 dispense_status=None,
                 dispense_type=None,
                 dispense_quantity=None,
                 dispense_suppliedItem=None,
                 dispense_supplier=None,
                 dispense_whenPrepared=None,
                 dispense_whenHandedOver=None,
                 dispense_destination=None,
                 dispense=None,
                 dispense_receiver=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.kind = kind                                     # , The kind of supply (central, non-stock, etc)
        self.status = status                                     # , requested | dispensed | received | failed | cancelled
        self.orderedItem = orderedItem                                     # , Medication, Substance, or Device requested to be supplied
        self.patient = patient                                     # , Patient for whom the item is supplied
        self.dispense_status = dispense_status                                     # , in progress | dispensed | abandoned
        self.dispense_type = dispense_type                                     # , Category of dispense event
        self.dispense_quantity = dispense_quantity                                     # , Amount dispensed
        self.dispense_suppliedItem = dispense_suppliedItem                                     # , Medication, Substance, or Device supplied
        self.dispense_supplier = dispense_supplier                                     # , Dispenser
        self.dispense_whenPrepared = dispense_whenPrepared                                     # , Dispensing time
        self.dispense_whenHandedOver = dispense_whenHandedOver                                     # , Handover time
        self.dispense_destination = dispense_destination                                     # , Where the Supply was sent
        
        if dispense is None:
            self.dispense = []                                     # , { attb['short_desc'] }}
        if dispense_receiver is None:
            self.dispense_receiver = []                                     # , { attb['short_desc'] }}
        

class ValueSet(Resource):
    """
    Short Description: A set of codes drawn from one or more code systems

    Formal Description: A value set specifies a set of codes drawn from one or more code systems.

    :param text: A human-readable narrative that contains a summary of the resource, and may be used to represent the content of the resource to a human. The narrative need not encode all the structured data, but is required to contain sufficient detail to make it "clinically safe" for a human to just read the narrative. Resource definitions may define what content should be represented in the narrative to ensure clinical safety.
    :param version: The identifier that is used to identify this version of the value set when it is referenced in a specification, model, design or instance. This is an arbitrary value managed by the profile author manually and the value should be a timestamp.
    :param name: A free text natural language name describing the value set.
    :param publisher: The name of the individual or organization that published the value set.
    :param description: A free text natural language description of the use of the value set - reason for definition, conditions of use, etc.
    :param copyright: A copyright statement relating to the value set and/or its contents.
    :param status: The status of the value set.
    :param experimental: This valueset was authored for testing purposes (or education/evaluation/marketing), and is not intended to be used for genuine usage.
    :param extensible: Whether this is intended to be used with an extensible binding or not.
    :param date: The date that the value set status was last changed.
    :param define: When value set defines its own codes.
    :param define_system: URI to identify the code system.
    :param define_version: The version of this code system that defines the codes. Note that the version is optional because a well maintained code system does not suffer from versioning, and therefore the version does not need to be maintained. However many code systems are not well maintained, and the version needs to be defined and tracked.
    :param define_caseSensitive: If code comparison is case sensitive when codes within this system are compared to each other.
    :param define_concept_code: Code that identifies concept.
    :param define_concept_abstract: If this code is not for use as a real concept.
    :param define_concept_display: Text to Display to the user.
    :param define_concept_definition: The formal definition of the concept. Formal definitions are not required, because of the prevalence of legacy systems without them, but they are highly recommended, as without them there is no formal meaning associated with the concept.
    :param compose: When value set includes codes from elsewhere.
    :param compose_include_system: The code system from which the selected codes come from.
    :param compose_include_version: The version of the code system that the codes are selected from.
    :param expansion: When value set is an expansion.
    :param expansion_timestamp: Time valueset expansion happened.
    :param expansion_contains_system: System value for the code.
    :param expansion_contains_code: Code - if blank, this is not a choosable code.
    :param expansion_contains_display: User display for the concept.
    
    :param telecom: Contacts of the publisher to assist a user in finding and communicating with the publisher.
    :param define_concept: Concepts in the code system.
    :param compose_import: Includes the contents of the referenced value set as a part of the contents of this value set.
    :param compose_include: Include one or more codes from a code system.
    :param compose_exclude: Exclude one or more codes from the value set.
    :param expansion_contains: Codes in the value set.
    
    """
    def __init__(self,
                 customer_id=None,
                 name_space=None,
                 id=None,
                 identifier=None,
                 versionId=None,
                 resourceType="ValueSet",
                 text=None,
                 version=None,
                 name=None,
                 publisher=None,
                 description=None,
                 copyright=None,
                 status=None,
                 experimental=None,
                 extensible=None,
                 date=None,
                 define=None,
                 define_system=None,
                 define_version=None,
                 define_caseSensitive=None,
                 define_concept_code=None,
                 define_concept_abstract=None,
                 define_concept_display=None,
                 define_concept_definition=None,
                 compose=None,
                 compose_include_system=None,
                 compose_include_version=None,
                 expansion=None,
                 expansion_timestamp=None,
                 expansion_contains_system=None,
                 expansion_contains_code=None,
                 expansion_contains_display=None,
                 telecom=None,
                 define_concept=None,
                 compose_import=None,
                 compose_include=None,
                 compose_exclude=None,
                 expansion_contains=None,
                 ):
        Resource.__init__(self,
                          customer_id=customer_id,
                          name_space=name_space,
                          identifier=identifier,
                          id=id,
                          versionId=versionId,
                          resourceType=resourceType)
        self.text = text                                     # , Text summary of the resource, for human interpretation
        self.version = version                                     # , Logical id for this version of the value set
        self.name = name                                     # , Informal name for this value set
        self.publisher = publisher                                     # , Name of the publisher (Organization or individual)
        self.description = description                                     # , Human language description of the value set
        self.copyright = copyright                                     # , About the value set or its content
        self.status = status                                     # , draft | active | retired
        self.experimental = experimental                                     # , If for testing purposes, not real usage
        self.extensible = extensible                                     # , Whether this is intended to be used with an extensible binding
        self.date = date                                     # , Date for given status
        self.define = define                                     # , When value set defines its own codes
        self.define_system = define_system                                     # , URI to identify the code system
        self.define_version = define_version                                     # , Version of this system
        self.define_caseSensitive = define_caseSensitive                                     # , If code comparison is case sensitive
        self.define_concept_code = define_concept_code                                     # , Code that identifies concept
        self.define_concept_abstract = define_concept_abstract                                     # , If this code is not for use as a real concept
        self.define_concept_display = define_concept_display                                     # , Text to Display to the user
        self.define_concept_definition = define_concept_definition                                     # , Formal Definition
        self.compose = compose                                     # , When value set includes codes from elsewhere
        self.compose_include_system = compose_include_system                                     # , The system the codes come from
        self.compose_include_version = compose_include_version                                     # , Specific version of the code system referred to
        self.expansion = expansion                                     # , When value set is an expansion
        self.expansion_timestamp = expansion_timestamp                                     # , Time valueset expansion happened
        self.expansion_contains_system = expansion_contains_system                                     # , System value for the code
        self.expansion_contains_code = expansion_contains_code                                     # , Code - if blank, this is not a choosable code
        self.expansion_contains_display = expansion_contains_display                                     # , User display for the concept
        
        if telecom is None:
            self.telecom = []                                     # , { attb['short_desc'] }}
        if define_concept is None:
            self.define_concept = []                                     # , { attb['short_desc'] }}
        if compose_import is None:
            self.compose_import = []                                     # , { attb['short_desc'] }}
        if compose_include is None:
            self.compose_include = []                                     # , { attb['short_desc'] }}
        if compose_exclude is None:
            self.compose_exclude = []                                     # , { attb['short_desc'] }}
        if expansion_contains is None:
            self.expansion_contains = []                                     # , { attb['short_desc'] }}
        
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
