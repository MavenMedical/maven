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
    yield from write_composition_alerts(composition, conn)

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
            dx_coding = condition.get_ICD9_id()
            dx_code_id = dx_coding.code
            dx_code_system = dx_coding.system

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
        for order in composition.get_encounter_orders():
            if isinstance(order.detail[0], FHIR_API.Procedure):
                code_id = order.detail[0].type.coding[0].code
            elif isinstance(order.detail[0], FHIR_API.Medication):
                code_id = order.detail[0].code.coding[0].code
            cmdargs = [composition.customer_id,
                       order.detail[0].identifier[0].value,
                       composition.subject.get_pat_id(),
                       composition.encounter.get_csn(),
                       composition.get_author_id(),
                       composition.get_author_id(),
                       order.get_orderable_ID()[0],
                       "created",
                       "webservice",
                       code_id,
                       "clientEMR",
                       order.detail[0].text,
                       order.detail[0].resourceType,
                       order.detail[0].base_cost,
                       composition.lastModifiedDate]

            cur = yield from conn.execute_single("SELECT upsert_enc_order(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", extra=cmdargs)

    except:
        raise Exception("Error inserting encounter orders into database")

@asyncio.coroutine
def write_composition_alerts(composition, conn):

    customer_id = composition.customer_id
    patient_id = composition.subject.get_pat_id()
    provider_id = composition.get_author_id()
    encounter_id = composition.encounter.get_csn()

    for alert_group_type in composition.get_section_by_coding(code_system="maven", code_value="alerts").content:

        alert_category = alert_group_type['alert_type']
        for alert in alert_group_type['alert_list']:
            try:
                column_map = ["customer_id",
                              "pat_id",
                              "provider_id",
                              "encounter_id",
                              "cds_rule",
                              "category",
                              "code_trigger",
                              "code_trigger_type",
                              "alert_datetime",
                              "short_title",
                              "long_title",
                              "short_description",
                              "long_description",
                              "saving"]
                columns = DBMapper.select_rows_from_map(column_map)

                cmdargs = [customer_id,
                           patient_id,
                           provider_id,
                           encounter_id,
                           alert.CDS_rule,
                           alert_category,
                           alert.code_trigger,
                           alert.code_trigger_type,
                           alert.alert_datetime,
                           alert.short_title,
                           alert.long_title,
                           alert.short_description,
                           alert.long_description,
                           alert.saving]

                cmd = []
                cmd.append("INSERT INTO alert")
                cmd.append("(" + columns + ")")
                cmd.append("VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

                cur = yield from conn.execute_single(' '.join(cmd)+';',cmdargs)

            except:
                raise Exception("Error inserting Alerts into the database")

@asyncio.coroutine
def identify_encounter_orderable(item=None, order=None, composition=None, conn=None):

    try:
        column_map = ["orderable_id",
                      "system",
                      "name",
                      "description",
                      "ord_type",
                      "base_cost"]

        if isinstance(item, FHIR_API.CodeableConcept):
            column_map.extend(["cpt_code", "cpt_version", "rx_rxnorm_id", "rx_generic_name"])
            columns = DBMapper.select_rows_from_map(column_map)
            cmdargs = [tuple([(coding.code) for coding in item.coding]), composition.customer_id]
            cmd = []
            cmd.append("SELECT " + columns)
            cmd.append("FROM orderable")
            cmd.append("WHERE orderable_id IN %s AND customer_id=%s")

            cur = yield from conn.execute_single(' '.join(cmd), cmdargs)

            for result in cur:
                orderable_id, system, name, description, order_type, base_cost = _get_base_order_elements_from_DB_cursor_result(result)

                if order_type == "Medication":
                    original_coding = FHIR_API.Coding(code=orderable_id, system=system, display=name)
                    rxnorm_coding = FHIR_API.Coding(code=result[8], system="rxnorm", display=name)
                    rtn_FHIR_medication = FHIR_API.Medication(text=name,
                                                       identifier=order.identifier,
                                                       name=name,
                                                       base_cost=base_cost,
                                                       code=FHIR_API.CodeableConcept(coding=[original_coding, rxnorm_coding],
                                                                                     text=order_type))
                    return rtn_FHIR_medication

                elif order_type in ["Procedure", "Lab"]:
                    original_coding = FHIR_API.Coding(code=orderable_id, system=system, display=name)
                    procedure_coding = FHIR_API.Coding(code=result[6], system=result[7], display=name)
                    rtn_FHIR_procedure = FHIR_API.Procedure(text=name,
                                                      identifier=order.identifier,
                                                      name=name,
                                                      base_cost=base_cost,
                                                      type=FHIR_API.CodeableConcept(coding=[original_coding, procedure_coding],
                                                                                    text=order_type))
                    return rtn_FHIR_procedure

        elif isinstance(item, FHIR_API.Procedure):
            column_map.extend(["cpt_code", "cpt_version"])
            columns = DBMapper.select_rows_from_map(column_map)
            cmdargs = [tuple([(coding.code) for coding in item.type.coding]), composition.customer_id]
            cmd = []
            cmd.append("SELECT " + columns)
            cmd.append("FROM orderable")
            cmd.append("WHERE cpt_code IN %s AND customer_id=%s")

            cur = yield from conn.execute_single(' '.join(cmd), cmdargs)

            for result in cur:
                orderable_id, system, name, description, order_type, base_cost = _get_base_order_elements_from_DB_cursor_result(result)
                del item.type.coding[:]
                item.type.coding.append(FHIR_API.Coding(code=result[6], system=result[7], display=name))
                item.type.coding.append(FHIR_API.Coding(code=orderable_id, system=system, display=name))
                item.identifier = order.identifier
                item.type.text = order_type
                item.base_cost = base_cost
                item.name = name

            return item

        elif isinstance(item, FHIR_API.Medication):
            column_map.extend(["rx_rxnorm_id", "rx_generic_name"])
            columns = DBMapper.select_rows_from_map(column_map)
            cmdargs = [tuple([(coding.code) for coding in item.code.coding]), composition.customer_id]
            cmd = []
            cmd.append("SELECT " + columns)
            cmd.append("FROM orderable")
            cmd.append("WHERE cpt_code IN %s AND customer_id=%s")

            cur = yield from conn.execute_single(' '.join(cmd), cmdargs)

            for result in cur:
                orderable_id, system, name, description, order_type, base_cost = _get_base_order_elements_from_DB_cursor_result(result)
                del item.code.coding[:]
                item.code.coding.append(FHIR_API.Coding(code=result[6], system=result[7], display=name))
                item.code.coding.append(FHIR_API.Coding(code=orderable_id, system=system, display=name))
                item.code.text = order_type
                item.identifier = order.identifier
                item.base_cost = base_cost
                item.name = name

            return item

    except:
        raise Exception("Error identifying orderables")

def _get_base_order_elements_from_DB_cursor_result(result):
    orderable_id = result[0]
    system = result[1]
    name = result[2]
    description = result[3]
    order_type = result[4]
    base_cost = FHIR_API.round_up_five(result[5])

    return orderable_id, system, name, description, order_type, base_cost



@asyncio.coroutine
def get_snomeds_and_append_to_encounter_dx(composition, conn):
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
def get_duplicate_orders(composition, conn):
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

        orderable_IDs_list = []
        for order in composition.get_encounter_orders():
            orderable_IDs_list.extend(order.get_orderable_ID())

        #for order in enc_ord_summary_section.content:
        column_map = ["order_ord.orderable_id",
                      "orderable.system",
                      "order_ord.order_id",
                      "order_ord.encounter_id",
                      "order_ord.order_name",
                      "order_ord.order_datetime",
                      "order_ord.order_type"]
        columns = DBMapper.select_rows_from_map(column_map)

        cmd = []
        cmdargs = [composition.customer_id,
                   composition.subject.get_pat_id(),
                   tuple(orderable_IDs_list),
                   one_year_ago,
                   twelve_hours_ago]
        cmd.append("SELECT " + columns)
        cmd.append("FROM order_ord")
        cmd.append("JOIN orderable on order_ord.orderable_id = orderable.orderable_id")
        cmd.append("WHERE order_ord.customer_id=%s AND order_ord.pat_id=%s AND order_ord.orderable_id IN %s AND order_ord.order_datetime > %s AND order_ord.order_datetime <= %s")


        cur = yield from conn.execute_single(' '.join(cmd), cmdargs)

        for result in cur:
            rtn_duplicate_orders[(result[0], result[1])] = {"order_id": result[2],
                                                            "encounter_id": result[3],
                                                            "order_name": result[4],
                                                            "date_time": result[5],
                                                            "order_type": result[6]}

        return rtn_duplicate_orders
    except:
        raise Exception("Error finding previous duplicate orders for this patient")

@asyncio.coroutine
def get_observations_from_duplicate_orders(duplicate_orders, composition, conn):
    """

    """
    try:
        customer_id = composition.customer_id
        patient_id = composition.subject.get_pat_id()

        for ord in list(duplicate_orders):
            observations = []
            order_code = ord[0]
            order_code_system = ord[1]
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
            cmdargs = [customer_id,
                       patient_id,
                       order_id]
            cur = yield from conn.execute_single("select " + columns + " from observation where customer_id=%s and pat_id=%s and order_id=%s", extra=cmdargs)

            for result in cur:
                duplicate_order_observation = FHIR_API.Observation(status=result[0],
                                                                   appliesdateTime=result[1],
                                                                   valueQuantity=FHIR_API.Quantity(value=result[2], units=result[3]),
                                                                   referenceRange_low=result[4],
                                                                   referenceRange_high=result[5],
                                                                   valueCodeableConcept=FHIR_API.CodeableConcept(coding=FHIR_API.Coding(system="http://loinc.org", code=result[6]),
                                                                                                                 text=result[7]),
                                                                   name=result[7])
                observations.append(duplicate_order_observation)

            if len(observations) > 0:
                duplicate_orders[ord]['related_observations'] = observations
            else:
                del duplicate_orders[ord]

        return duplicate_orders

    except:
        raise Exception("Error extracting observations from duplicate lab orders")


@asyncio.coroutine
def get_matching_CDS_rules(composition, conn):

    #Pull a list of all the SNOMED CT codes from all of the conditions in the composition
    encounter_snomedIDs = composition.get_encounter_dx_snomeds()

    #TODO
    patient_age = composition.get_patient_age()



    rtn_matched_rules = []
    for enc_ord in composition.get_encounter_orders():
        trigger_code = enc_ord.get_procedure_id_coding()
        args = [trigger_code.code,
                trigger_code.system,
                patient_age,
                composition.subject.gender,
                encounter_snomedIDs,
                encounter_snomedIDs,
                composition.subject.get_pat_id(),
                composition.customer_id]

        cur = yield from conn.execute_single("select * from rules.evalrules(%s,%s,%s,%s,%s,%s,%s,%s)", extra=args)

        for result in cur:
            rtn_matched_rules.append(FHIR_API.Rule(rule_details=result[2],
                                                   CDS_rule_id=result[0],
                                                   code_trigger=trigger_code.code,
                                                   code_trigger_type=trigger_code.system,
                                                   name=result[1]))
    return rtn_matched_rules



























