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
from collections import defaultdict
from dateutil.relativedelta import relativedelta
import utils.api.pyfhir.pyfhir_generated as FHIR_API
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
        json_composition = json.dumps(composition, default=FHIR_API.jdefault)
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
                                             alert.code_trigger, alert.CDS_rule, alert_datetime, alert.short_title, alert.tag_line,
                                             alert.description, alert.saving])

@asyncio.coroutine
def gather_encounter_order_cost_info(ordersdict, detailsdict, conn):

        rtn_encounter_cost_breakdown = []
        cur = yield from conn.execute_single("SELECT cost_amt, billing_code FROM costmap WHERE billing_code IN %s", extra=[tuple(ordersdict.keys())])

        # process the results
        for result in cur:
            cost = float(result[0])
            for order in ordersdict[result[1]]:
                order.totalCost += cost
            for detail in detailsdict[result[1]]:
                rtn_encounter_cost_breakdown.append([detail[2], cost])

        return rtn_encounter_cost_breakdown

@asyncio.coroutine
def gather_snomeds_append_to_encounter_dx(composition, conn):
    """
    Pseudo-code description:
    FOR EACH CONDITION,
    FOR EACH CODING-ID IN EACH CONDITION,
    LOOK-UP ANY AVAILABLE SNOMED CT CONCEPTS FROM DATABASE AND APPEND TO LIST
    CREATE A NEW CODING-ID AND APPEND TO CONDITION TO HOLD EACH SNOMED CT FROM LIST

    :param composition: FHIR Composition Object that MUST contain the "Encounter Diagnoses/Conditions" Composition Section
    :param conn: Asynchronous database connection
    """

    try:
        for condition in composition.get_encounter_conditions():
            snomed_ids = []
            for coding in condition.code.coding:
                column_map = ["snomedid"]
                columns = DBMapper.select_rows_from_map(column_map)
                cur = yield from conn.execute_single("select " + columns + " from terminology.codemap where code=%s and codetype=%s", extra=[coding.code, coding.system])
                for result in cur:
                    snomed_ids.append(int(result[0]))
                cur.close()

            for snomed_id in snomed_ids:
                condition.code.coding.append(FHIR_API.Coding(system="SNOMED CT", code=snomed_id))
    except:
        raise Exception("Error gathering SNOMED CT codes for Encounter Diagnoses")

@asyncio.coroutine
def gather_duplicate_orders(enc_ord_summary_section, composition, conn):
    """
    This function takes the "Maven Encounter Order Summary" Composition section (a list of tuples(code, code system)),
    runs a query against the database looking for orders up to a year ago, finds the intersection between the two,
    and returns a dictionary with KEY=tuple(code, code-system) VALUE=list(various data items that may wanted to be used)

    :param composition: A composition object that contains the Encounter Order Summary section (note this is different from
                        the full-fledged Encounter Orders section
    :param conn: An asynchronous database connection with which to perform the SQL queries
    """
    try:
        rtn_duplicate_orders = {}
        twelve_hours_ago = datetime.datetime.now() - relativedelta(hours=12)
        one_year_ago = datetime.datetime.now() - relativedelta(years=1)

        for order in enc_ord_summary_section.content:
            column_map = ["proc_code",
                          "code_type",
                          "orderid",
                          "encounter_id",
                          "order_name",
                          "datetime",
                          "order_type"]
            columns = DBMapper.select_rows_from_map(column_map)
            cur = yield from conn.execute_single("select " + columns + " from mavenorder where customer_id=%s and pat_id=%s and proc_code=%s and code_type=%s and datetime > %s AND datetime <= %s", extra=[composition.customer_id, composition.subject.get_pat_id(), order[0], order[1], one_year_ago, twelve_hours_ago])

            for result in cur:
                rtn_duplicate_orders[(result[0], result[1])] = {"order_id": result[2],
                                                                "encounter_id": result[3],
                                                                "order_name": result[4],
                                                                "date_time": result[5],
                                                                "order_type": result[6]}

        # DOH Moment Below...I don't need the intersection b/c the DB query is only selecting the ones that match anyway
        # for ord in set(enc_ord_summary_section.content).intersection(set(list(previous_orders))):
            #duplicate_orders[ord] = previous_orders[ord]

        return rtn_duplicate_orders
    except:
        raise Exception("Error finding previous duplicate orders for this patient")

@asyncio.coroutine
def gather_observations_from_duplicate_orders(duplicate_orders, composition, conn):
    """

    """
    try:
        customer_id = composition.customer_id
        patient_id = composition.subject.get_pat_id()

        for ord in list(duplicate_orders):
            order_code = ord[0]
            order_code_system = ord[1]
            ord_detail = composition.get_encounter_order_detail_by_coding(code=order_code, code_system=order_code_system)
            order_id = duplicate_orders[ord]["order_id"]
            column_map = ["status",
                          "result_time",
                          "numeric_result",
                          "units",
                          "reference_low",
                          "reference_high",
                          "loinc_code",
                          "name",
                          "external_name"]
            columns = DBMapper.select_rows_from_map(column_map)

            cur = yield from conn.execute_single("select " + columns + " from observation where customer_id=%s and pat_id=%s and order_id=%s", extra=[customer_id, patient_id, order_id])
            duplicate_orders[ord].update({"observations": []})
            for result in cur:
                duplicate_orders[ord]["observations"].append({"status": result[0],
                                                              "result_time": result[1],
                                                              "numeric_result": result[2],
                                                              "units": result[3],
                                                              "reference_low": result[4],
                                                              "reference_high": result[5],
                                                              "loinc_code": result[6],
                                                              "name": result[7],
                                                              "external_name": result[8]})

                ord_detail.relatedItem.append(FHIR_API.Observation(status=result[0],
                                                                   appliesdateTime=result[1],
                                                                   valueQuantity=FHIR_API.Quantity(value=result[2], units=result[3]),
                                                                   referenceRange_low=result[4],
                                                                   referenceRange_high=result[5],
                                                                   valueCodeableConcept=FHIR_API.CodeableConcept(coding=FHIR_API.Coding(system="http://loinc.org", code=result[6]),
                                                                                                                 text=result[7]),
                                                                   name=result[7]))

        print(duplicate_orders)
    except:
        raise Exception("Error extracting observations from duplicate lab orders")


@asyncio.coroutine
def get_matching_CDS_rules(composition, conn):

    #Pull a list of all the SNOMED CT codes from all of the conditions in the composition
    encounter_snomedIDs = composition.get_encounter_dx_snomeds()
    enc_ord_summary_section = composition.get_section_by_coding("maven", "enc_ord_sum")
    patient_age = composition.get_patient_age()

    matched_rules = []
    for enc_ord in enc_ord_summary_section.content:
        cur = yield from conn.execute_single("select rules.evalrules(%s,%s,%s,%s,%s,%s,%s,%s)", extra=[enc_ord[0], enc_ord[1], patient_age, composition.subject.gender, encounter_snomedIDs, encounter_snomedIDs, composition.subject.get_pat_id(), composition.customer_id])

        for result in cur:
            matched_rules.append(result)

    return matched_rules



























