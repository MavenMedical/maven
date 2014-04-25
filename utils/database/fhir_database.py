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
#ASSUMES:       The database connection argument for each of the methods is of type AsynchronousConnectionPool
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-96
#*************************************************************************
import json
import datetime
import asyncio
import utils.api.api as api



@asyncio.coroutine
def write_composition_to_db(composition, conn):
    yield from write_composition_patient(composition, conn)
    yield from write_composition_encounter(composition, conn)
    yield from write_composition_json(composition, conn)
    yield from write_composition_encounterdx(composition, conn)
    yield from write_composition_encounter_orders(composition, conn)

@asyncio.coroutine
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


        cur = yield from conn.execute_single("SELECT upsert_patient('%s', %s, '%s', '%s', '%s', '%s', '%s', '%s')" %
                                            (pat_id, customer_id, birth_month, sex, mrn, patname, cur_pcp_prov_id, birth_date))
        cur.close()
    except:
        raise Exception("Error inserting patient data into database")

@asyncio.coroutine
def write_composition_encounter(composition, conn):
    try:
        encounter_id = composition.encounter.get_csn()
        pat_id = composition.subject.get_pat_id()
        encounter_type = "Emergency"
        encounter_date = "2014-03-24"
        provider_id = composition.encounter.get_prov_id()
        bill_prov_id = "32209837"
        encounter_dep = 1235234
        encounter_admit_time = "2014-03-24T08:45:23"
        encounter_disch_time = "NULL"
        customer_id = composition.customer_id

        cur = yield from conn.execute_single("SELECT upsert_encounter('%s', '%s', '%s', '%s', '%s', '%s', %s, '%s', %s, '%s')" %
                                            (encounter_id, pat_id, encounter_type, encounter_date, provider_id, bill_prov_id, encounter_dep, encounter_admit_time, encounter_disch_time, customer_id))
        cur.close()

    except:
        raise Exception("Error inserting encounter data into database")

@asyncio.coroutine
def write_composition_json(composition, conn):
    try:
        pat_id = composition.subject.get_pat_id()
        customer_id = composition.customer_id
        encID = composition.encounter.get_csn()
        json_composition = json.dumps(composition, default=api.jdefault)
        cur = yield from conn.execute_single("INSERT INTO composition (patient_id, encounter_id, customer_id, comp_body) VALUES ('%s', '%s', %s, ('%s'))" % (pat_id, encID, customer_id, json_composition))
        cur.close()

    except:
        raise Exception("Error inserting JSON composition into database")

@asyncio.coroutine
def write_composition_encounterdx(composition, conn):
    try:
        pat_id = composition.subject.get_pat_id()
        customer_id = composition.customer_id
        encID = composition.encounter.get_csn()
        problem_list = composition.get_encounter_problem_list()
        for problem in problem_list:
            dx_ID = problem.get_problem_ID().value
            cur = conn.execute_single("SELECT upsert_encounterdx('%s', '%s', '%s', NULL, NULL, NULL, %s)" % (pat_id, encID, dx_ID, customer_id))
            cur.close()

    except:
        raise Exception("Error inserting encounter problem list into database")

@asyncio.coroutine
def write_composition_encounter_orders(composition, conn):
    try:
        pat_id = composition.subject.get_pat_id()
        customer_id = composition.customer_id
        encID = composition.encounter.get_csn()
        order_datetime = datetime.datetime.now()
        orders = composition.get_encounter_orders()
        for order in orders:
            order_name = order.detail[0].name
            order_type = order.detail[0].type
            order_code = order.detail[0].identifier[0].value
            order_code_type = "maven"
            order_cost = float(order.totalCost)
            active = True

            cur = yield from conn.execute_single("SELECT upsert_enc_order('%s', %s, '%s', '%s', '%s', '%s', '%s', %s, '%s', '%s')" %
                                                (pat_id, customer_id, encID, order_name, order_type, order_code, order_code_type, order_cost, order_datetime, active))

    except:
        raise Exception("Error inserting encounter orders into database")