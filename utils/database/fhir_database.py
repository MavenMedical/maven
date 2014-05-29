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
import utils.api.pyfhir.pyfhir as api
from utils.database.database import MappingUtilites

DBMapper = MappingUtilites()

@asyncio.coroutine
def write_composition_to_db(composition, conn):
    yield from write_composition_patient(composition, conn)
    yield from write_composition_encounter(composition, conn)
    yield from write_composition_json(composition, conn)
    yield from write_composition_conditions(composition, conn)
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


        cur = yield from conn.execute_single("SELECT upsert_patient(%s, %s, %s, %s, %s, %s, %s, %s)",
                                            extra=[pat_id, customer_id, birth_month, sex, mrn, patname, cur_pcp_prov_id, birth_date])
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
        #provider_id = composition.encounter.get_prov_id()
        provider_id = composition.get_author_id()
        bill_prov_id = "32209837"
        encounter_dep = 1235234
        encounter_admit_time = "2014-03-24T08:45:23"
        encounter_disch_time = None
        customer_id = composition.customer_id

        cur = yield from conn.execute_single("SELECT upsert_encounter(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                            extra=[encounter_id, pat_id, encounter_type, encounter_date, provider_id, bill_prov_id, encounter_dep, encounter_admit_time, encounter_disch_time, customer_id])
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
        cur = yield from conn.execute_single("INSERT INTO composition (patient_id, encounter_id, customer_id, comp_body) VALUES (%s, %s, %s, %s)", extra=[pat_id, encID, customer_id, json_composition])
        cur.close()

    except:
        raise Exception("Error inserting JSON composition into database")

@asyncio.coroutine
def write_composition_conditions(composition, conn):
    try:
        pat_id = composition.subject.get_pat_id()
        customer_id = composition.customer_id
        encounter_id = composition.encounter.get_csn()
        condition_list = composition.get_encounter_conditions()
        for condition in condition_list:
            snomed_id = condition.get_snomed_id()
            dx_code_id = condition.get_ICD9_id()
            if dx_code_id is not None:
                dx_code_system = "ICD-9"
            else:
                dx_code_system = None

            columns = [pat_id,
                       customer_id,
                       encounter_id,
                       condition.category,
                       condition.status,
                       condition.dateAsserted,
                       condition.abatementDate,
                       snomed_id,
                       dx_code_id,
                       dx_code_system,
                       condition.text,
                       condition.isPrincipal,
                       condition.abatementBoolean,
                       condition.presentOnArrival]
            #dx_ID = condition.get_problem_ID().value
            cur = yield from conn.execute_single("SELECT upsert_condition(%s, %s, %s, %s, %s, %s, %s, %s::bigint, %s, %s, %s, %s, %s, %s)", extra=columns)
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
            order_name = order.detail[0].text
            order_type = order.detail[0].resourceType
            order_code = order.detail[0].type.coding[0].code
            order_code_type = order.detail[0].type.coding[0].system
            order_cost = float(order.totalCost)
            active = True

            cur = yield from conn.execute_single("SELECT upsert_enc_order(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                                extra=[pat_id, customer_id, encID, order_name, order_type, order_code, order_code_type, order_cost, order_datetime, active])

    except:
        raise Exception("Error inserting encounter orders into database")

@asyncio.coroutine
def write_composition_alerts(alert_datetime, alert_bundle, conn):

    for alert in alert_bundle:

        column_map = ["customer_id",
                      "pat_id",
                      "provider_id",
                      "encounter_id",
                      "code_trigger",
                      "sleuth_rule",
                      "alert_datetime",
                      "short_title",
                      "long_title",
                      "description",
                      "saving"]

        columns = DBMapper.select_rows_from_map(column_map)

        cur = yield from conn.execute_single("INSERT INTO alert(" + columns + ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                            extra=[alert.customer_id, alert.subject, alert.provider_id, alert.encounter_id,
                                             alert.code_trigger, alert.sleuth_rule, alert_datetime, alert.short_title, alert.tag_line,
                                             alert.description, alert.saving])