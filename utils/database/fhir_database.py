#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:   This fhir_database.py module contains the classes required to update the
#               SQL database from FHIR objects, as well as convert database records into
#               FHIR objects.
#
#
#************************
#ASSUMES:
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-96
#*************************************************************************
import json
import datetime

import utils.api.api as api


class PostgresFHIR():

    @staticmethod
    def write_composition_to_db(composition, conn):
        write_composition_patient(composition, conn)
        write_composition_encounter(composition, conn)
        write_composition_json(composition, conn)
        write_composition_encounterdx(composition, conn)
        write_composition_encounter_orders(composition, conn)


def write_composition_patient(composition, conn):
    try:
        pat_id = composition.subject.get_pat_id()
        customer_id = composition.customer_id
        birth_month = composition.subject.get_birth_month()
        birth_date = str(composition.subject.birthDate)
        sex = composition.subject.gender
        mrn = composition.subject.get_mrn()
        patname = composition.subject.get_name()
        cur_pcp_prov_id = composition.subject.get_current_pcp()


        cur = conn.execute("SELECT upsert_patient('%s', %s, '%s', '%s', '%s', '%s', '%s', '%s')" %
                               (pat_id, customer_id, birth_month, sex, mrn, patname, cur_pcp_prov_id, birth_date))
        cur.close()
    except:
        raise Exception("Error inserting patient data into database")


def write_composition_encounter(composition, conn):
    try:
        pat_id = composition.subject.get_pat_id()
        customer_id = composition.customer_id
        encID = composition.encounter.get_csn()
        cur = conn.execute("SELECT upsert_encounter('%s', '%s', 'Emergency', '2014-03-24', 'JHU1093124', '32209837', 1235234, '2014-03-24T08:45:23', NULL, '%s')" % (encID, pat_id, customer_id))
        cur.close()

    except:
        raise Exception("Error parsing encounter data into database")


def write_composition_json(composition, conn):
    try:
        pat_id = composition.subject.get_pat_id()
        customer_id = composition.customer_id
        encID = composition.encounter.get_csn()
        json_composition = json.dumps(composition, default=api.jdefault)
        cur = conn.execute("INSERT INTO composition (patient_id, encounter_id, customer_id, comp_body) VALUES ('%s', '%s', %s, ('%s'))" % (pat_id, encID, customer_id, json_composition))
        cur.close()

    except:
        raise Exception("Error storing JSON composition")


def write_composition_encounterdx(composition, conn):
    try:
        pat_id = composition.subject.get_pat_id()
        customer_id = composition.customer_id
        encID = composition.encounter.get_csn()
        problem_list = composition.get_encounter_problem_list()
        for problem in problem_list:
            dx_ID = problem.get_problem_ID().value
            cur = conn.execute("SELECT upsert_encounterdx('%s', '%s', '%s', NULL, NULL, NULL, %s)" % (pat_id, encID, dx_ID, customer_id))

    except:
        raise Exception("Error parsing encounter problem list")


def write_composition_encounter_orders(composition, conn):
    try:
        pat_id = composition.subject.get_pat_id()
        customer_id = composition.customer_id
        encID = composition.encounter.get_csn()
        now = datetime.datetime.now()
        orders = composition.get_encounter_orders()
        for order in orders:
            cur = conn.execute("INSERT INTO mavenorder(pat_id, customer_id, encounter_id, order_name, order_type, proc_code, code_type, order_cost, datetime) VALUES('%s', %s,'%s','%s','%s', '%s', '%s', %s, '%s')" % (pat_id, composition.customer_id, encID, order.detail[0].name, order.detail[0].type, order.detail[0].identifier[0].value, "maven", float(order.totalCost), now))

    except:
        raise Exception("Error parsing encounter orders")