#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:   This file builds the Python classes based on the json examples provided by FHIR
#
#
#
#
#************************
#ASSUMES:
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-160ish (Rebuilding FHIR spec after discussion with ONC/Dr. Fridsma and
#                                          being introduced to the Health e-Decisions working group
#*************************************************************************
import os
import json
import jinja2
import keyword


class FHIR_PythonObjectGenerator():

    def __init__(self):
        self.directory = '/home/devel/maven/utils/api/pyfhir/examples/'
        self.FHIR_FILE_LIST = get_file_list_from_directory(self.directory)

        self.templateLoader = jinja2.FileSystemLoader('/home/devel/maven/utils/api/pyfhir/templates/')
        self.templateEnv = jinja2.Environment(loader=self.templateLoader)

        self.data_types_lib_template = self.templateEnv.get_template("pyfhir_datatypes_lib_template.jinja2")
        self.complex_datatype_template = self.templateEnv.get_template("data_type_template.jinja2")

        self.pyfhir_lib_template = self.templateEnv.get_template("pyfhir_lib_template.jinja2")
        self.pyfhir_resource_template = self.templateEnv.get_template("pyfhir_resource_template.jinja2")
        self.compositionResourceCustomMethods = compositionResourceCustomMethods
        self.patientResourceCustomMethods = patientResourceCustomMethods
        self.encounterResourceCustomMethods = encounterResourceCustomMethods
        self.conditionResourceCustomMethods = conditionResourceCustomMethods
        self.sleuthruleResourceClass = sleuthruleResourceClass

    def generate_python_objects(self):
        #self.build_FHIR_datatypes()
        self.build_FHIR_resources()

    def build_FHIR_datatypes(self):
        try:
            lib_file = open('/home/devel/maven/utils/api/pyfhir/pyfhir_datatypes_generated.py', 'w+')
            lib_file.write(self.data_types_lib_template.render())
            datatypes = _get_list_FHIR_data_types(self.directory)
            complex_datatypes = [(file) for dt in datatypes for file in self.FHIR_FILE_LIST if ("%s.profile" % dt) in file]
            self._build_complex_types(complex_datatypes, lib_file)
            lib_file.close()
        except IOError:
            pass

    def build_FHIR_resources(self):
        try:
            lib_file = open('/home/devel/maven/utils/api/pyfhir/pyfhir_generated.py', 'w+')
            lib_file.write(self.pyfhir_lib_template.render())
            fhir_resource_list = _get_list_FHIR_resources(self.directory)
            fhir_resource_files = [(file) for rsc in fhir_resource_list for file in self.FHIR_FILE_LIST if ("%s.profile" % rsc.lower()) in file]
            self._build_resources(fhir_resource_files, lib_file)
            lib_file.write(self.sleuthruleResourceClass)
            lib_file.close()
        except IOError:
            pass

    def _build_complex_types(self, complex_dts, lib_file):
        for cplx_dt in complex_dts:
            cplx_dt_json = _create_json_dict_from_file(cplx_dt)
            class_definition = ""
            attributes_list = []
            list_attributes_list = []
            for i in cplx_dt_json['structure'][0]['element']:

                if "." in i['path'] and "extension" not in i['path'] and "modifierExtension" not in i['path']:
                    if "type" in i['definition'].keys() and i['definition']['max'] == "*":
                        print(i['definition']['type'])
                        list_attributes_list.append({"name" : i['path'].split(".")[1], "short_desc" : i['definition']['short'], "formal_desc" : i['definition']['formal']})

                    elif len(i['path'].split(".")) == 2 and "[x]" not in i['path']:
                        attributes_list.append({"name" : i['path'].split(".")[1], "short_desc" : i['definition']['short'], "formal_desc" : i['definition']['formal']})
                    elif len(i['path'].split(".")) == 3:
                        attributes_list.append({"name" : i['path'].split(".")[2], "short_desc" : i['definition']['short'], "formal_desc" : i['definition']['formal']})
                else:
                    class_definition = i['definition']

            if "name" in cplx_dt_json['structure'][0].keys():
                class_name = cplx_dt_json['structure'][0]['name']
            elif "type" in cplx_dt_json['structure'][0].keys():
                class_name = cplx_dt_json['structure'][0]['type']

            templateVars = {"class_name" : class_name,
                            "attributes" : attributes_list,
                            "list_attributes" : list_attributes_list,
                            "class_definition_short" : class_definition['short'],
                            "class_definition_long" : class_definition['formal'],
                            }

            lib_file.write(self.complex_datatype_template.render(templateVars))
            
    def _build_resources(self, resources, lib_file):
        for rsc in resources:
            rsc_json = _create_json_dict_from_file(rsc)
            class_definition = ""
            attributes_list = []
            list_attributes_list = []
            class_name = rsc_json['structure'][0]['type']

            #TODO if the attribute is a complex attribute (e.g. in Observation "referenceRange"), build a python obj
            #o = type('referenceRange', (object,), {"low": None, "high": None, "meaning": None})

            if class_name != "DocumentReference":
                if class_name == "Composition":
                    pass
            
                for attb in rsc_json['structure'][0]['element']:
                    nested_attb = attb['path'].split(".")
                    nested_attb_length = len(nested_attb)
                    attb_full_path = attb['path']

                    if nested_attb_length == 1:
                        class_definition = attb['definition']

                    if nested_attb_length > 1 and "extension" not in attb_full_path and "modifierExtension" not in attb_full_path and "contained" not in attb_full_path and "identifier" not in attb_full_path:
                        attb_keys = attb['definition'].keys()

                        if (attb['definition']['max'] == "*"):
                            attb_IS_LIST = True
                        else:
                            attb_IS_LIST = False

                        if attb_IS_LIST:
                            if nested_attb_length == 2:
                                attb_name = nested_attb[1].strip("[x]")
                                if keyword.iskeyword(attb_name):
                                    attb_name = ("fhir_%s" % attb_name)
                                list_attributes_list.append({"name" : attb_name,
                                                             "short_desc" : attb['definition']['short'],
                                                             "formal_desc" : attb['definition']['formal']})

                            elif nested_attb_length == 3:
                                list_attributes_list.append({"name" : (attb['path'].split(".")[1].strip("[x]")+ "_" + attb['path'].split(".")[2].strip("[x]")),
                                                             "short_desc" : attb['definition']['short'],
                                                             "formal_desc" : attb['definition']['formal']})

                        elif nested_attb_length == 2:

                            attb_name = attb['path'].split(".")[1]
                            if keyword.iskeyword(attb_name):
                                attb_name = ("fhir_%s" % attb_name)

                            if "[x]" in attb_name:
                                for codetype in attb['definition']['type']:
                                    attributes_list.append({"name" : (attb_name.strip("[x]") + codetype['code']),
                                                    "short_desc" : attb['definition']['short'],
                                                    "formal_desc" : attb['definition']['formal'],
                                                    "object_type" : codetype['code']})


                            attributes_list.append({"name" : attb_name.strip("[x]"),
                                                    "short_desc" : attb['definition']['short'],
                                                    "formal_desc" : attb['definition']['formal']})

                        elif nested_attb_length == 3:
                            attributes_list.append({"name" : (attb['path'].split(".")[1].strip("[x]")+ "_" + attb['path'].split(".")[2].strip("[x]")),
                                                    "short_desc" : attb['definition']['short'],
                                                    "formal_desc" : attb['definition']['formal']})

                        elif nested_attb_length == 4:
                            attributes_list.append({"name" : (attb['path'].split(".")[1].strip("[x]")+ "_" + attb['path'].split(".")[2].strip("[x]")+ "_" + attb['path'].split(".")[3].strip("[x]")),
                                                    "short_desc" : attb['definition']['short'],
                                                    "formal_desc" : attb['definition']['formal']})



                templateVars = {"class_name" : class_name,
                                "attributes" : attributes_list,
                                "list_attributes" : list_attributes_list,
                                "class_definition_short" : class_definition['short'],
                                "class_definition_long" : class_definition['formal'],
                                }

                lib_file.write(self.pyfhir_resource_template.render(templateVars))
                if class_name == "Composition":
                    lib_file.write(self.compositionResourceCustomMethods)
                elif class_name == "Patient":
                    lib_file.write(self.patientResourceCustomMethods)
                elif class_name == "Encounter":
                    lib_file.write(self.encounterResourceCustomMethods)
                elif class_name == "Condition":
                    lib_file.write(self.conditionResourceCustomMethods)
                #print(self.pyfhir_resource_template.render(templateVars))


def _get_list_FHIR_data_types(file_path):
    data_types_json = _create_json_dict_from_file(file_path + "data-types.json")
    data_types_list = []
    for data_type in data_types_json['define']['concept']:
        data_types_list.append(data_type['code'])

    return data_types_list

def _get_list_FHIR_resources(file_path):
    data_types_json = _create_json_dict_from_file(file_path + "resource-types.json")
    data_types_list = []
    for data_type in data_types_json['define']['concept']:
        data_types_list.append(data_type['code'])

    return data_types_list


def _create_json_dict_from_file(file_path):
    try:
        f = open(file_path, 'r')
        rtn_json_object = json.loads(f.read())
        f.close()
        return rtn_json_object

    except IOError:
        pass


####
## Gets a listing of all the files in the examples directory
####
def get_file_list_from_directory(directory_path):
    file_list_generator = os.walk(directory_path)
    file_list = []
    for file in file_list_generator:
        for file_name in file[2]:
            file_list.append(file[0] + file_name)

    return file_list

compositionResourceCustomMethods = """
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
        problem_list = self.get_encounter_problem_list()
        problem_list_codes_IDs = []

        for problem in problem_list:
            for id in problem.identifier:
                problem_list_codes_IDs.append(id.value)

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
"""

patientResourceCustomMethods = """
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
"""

encounterResourceCustomMethods = """
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
"""

conditionResourceCustomMethods = """
    def get_problem_ID(self):
        for id in self.identifier:
            if id.label == "ICD":
                return id
"""

sleuthruleResourceClass = """
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
"""

if __name__ == '__main__':
    FHIR_Generator = FHIR_PythonObjectGenerator()
    FHIR_Generator.generate_python_objects()


