# *************************************************************************
# Copyright (c) 2014 - Maven Medical
# ************************
# AUTHOR:
__author__ = 'Yuki Uchino'
# ************************
# DESCRIPTION:   This fhir_database.py module contains the classes required to update the
#                SQL database from FHIR objects, as well as convert database records into
#                FHIR objects.
#
#
# ************************
# ASSUMES:       The database connection argument for each of the methods is of type AsynchronousConnectionPool
# ************************
# SIDE EFFECTS:
# ************************
# LAST MODIFIED FOR JIRA ISSUE: MAV-600 something by Yuki for conversion to Remote Procedure Calling
# *************************************************************************
import json
import datetime
import asyncio
from dateutil.relativedelta import relativedelta
import utils.api.pyfhir.pyfhir_generated as FHIR_API
from utils.database.database import AsyncConnectionPool, MappingUtilites
from utils.enums import ORDER_SOURCE, PROCEDURE_ORDER_TYPES, MEDICATION_ORDER_TYPES, ALERT_TYPES, ALERT_VALIDATION_STATUS
import maven_logging as ML
import maven_config as MC
from utils.database.remote_database_connector import RemoteDatabaseConnector


DBMapper = MappingUtilites()
FHIR_DB_LOG = ML.get_logger()
CONFIG_DATABASE = 'database'

##########################################################################################
##########################################################################################
##########################################################################################
#####
# WRITE FHIR OBJECTS TO DATABASE
#####
##########################################################################################
##########################################################################################
##########################################################################################


def FHIRPersistence(configname):
    server = RemoteDatabaseConnector(MC.MavenConfig[configname][CONFIG_DATABASE])
    fhir_client = server.create_client(FHIRPersistanceBase)
    fhir_client.schedule = lambda *args: None
    return fhir_client


class FHIRPersistanceBase():
    def __init__(self, configname):
        self.db = AsyncConnectionPool(MC.MavenConfig[configname][CONFIG_DATABASE])
        self.DBMapper = MappingUtilites()
        self.scheduled = False

    def schedule(self, loop=asyncio.get_event_loop()):
        if not self.scheduled:
            self.db.schedule(loop)
        self.scheduled = True

    @asyncio.coroutine
    def test(self):
        cur = yield from self.db.execute_single("SELECT * FROM customer;")
        for result in cur:
            print(result)

    @asyncio.coroutine
    def last_node_clicked(self, customer, protocol, patient):
        try:
            cur = yield from self.db.execute_single("SELECT node_id FROM trees.activity WHERE customer_id=%s AND patient_id=%s AND canonical_id=(SELECT canonical_id FROM trees.protocol WHERE protocol_id=%s) ORDER BY datetime DESC LIMIT 1", extra=[customer, patient, protocol])
            return cur.fetchone()[0]
        except:
            return None

    @ML.coroutine_trace(timing=True, write=FHIR_DB_LOG.debug)
    def write_composition_to_db(self, composition):
        yield from self.write_composition_patient(composition)
        yield from self.write_composition_encounter(composition)
        yield from self.write_composition_json(composition)
        yield from self.write_composition_conditions(composition)
        yield from self.write_composition_encounter_orders(composition)
        yield from self.write_composition_alerts(composition)

    @ML.coroutine_trace(timing=True, write=FHIR_DB_LOG.debug)
    def write_composition_patient(self, composition):
        try:
            patient_id = composition.subject.get_pat_id()
            customer_id = composition.customer_id
            birth_month = composition.subject.get_birth_month()
            birth_date = str(composition.subject.birthDate)
            sex = composition.subject.gender
            mrn = composition.subject.get_mrn()
            patname = composition.subject.get_name()
            cur_pcp_prov_id = composition.subject.get_current_pcp()

            cur = yield from self.db.execute_single("SELECT upsert_patient(%s, %s, %s, %s, %s, %s, %s, %s)",
                                                    extra=[patient_id, customer_id, birth_month, sex, mrn, patname, cur_pcp_prov_id, birth_date])
            cur.close()
        except:
            raise Exception("Error inserting patient data into database")

    @ML.coroutine_trace(timing=True, write=FHIR_DB_LOG.debug)
    def write_composition_encounter(self, composition):
        try:
            encounter_id = composition.encounter.get_csn()
            patient_id = composition.subject.get_pat_id()
            if composition.encounter.fhir_class is not None:
                encounter_type = composition.encounter.fhir_class.code
            else:
                encounter_type = None
            if composition.encounter.period is not None:
                encounter_date = composition.encounter.period.start.date().isoformat()
            else:
                encounter_date = None
            provider_id = composition.get_author_id()
            bill_prov_id = composition.get_author_id()
            encounter_dep = None
            encounter_admit_time = encounter_date
            encounter_disch_time = None
            customer_id = composition.customer_id
            last_modified = datetime.datetime.now()

            cur = yield from self.db.execute_single("SELECT upsert_encounter(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                                    extra=[encounter_id, patient_id, encounter_type, encounter_date, provider_id, bill_prov_id, encounter_dep, encounter_admit_time, encounter_disch_time, customer_id, last_modified])
            cur.close()

        except:
            raise Exception("Error inserting encounter data into database")

    @ML.coroutine_trace(timing=True, write=FHIR_DB_LOG.debug)
    def write_composition_json(self, composition):
        try:
            patient_id = composition.subject.get_pat_id()
            customer_id = composition.customer_id
            encID = composition.encounter.get_csn()
            json_composition = json.dumps(composition, default=FHIR_API.jdefault)
            datetime_insertion = datetime.datetime.now()
            cur = yield from self.db.execute_single("INSERT INTO composition (patient_id, encounter_id, customer_id, comp_body, datetime_inserted) VALUES (%s, %s, %s, %s, %s)", extra=[patient_id, encID, customer_id, json_composition, datetime_insertion])
            cur.close()

        except:
            raise Exception("Error inserting JSON composition into database")

    @ML.coroutine_trace(timing=True, write=FHIR_DB_LOG.debug)
    def write_composition_conditions(self, composition):
        try:
            patient_id = composition.subject.get_pat_id()
            customer_id = composition.customer_id
            encounter_id = composition.encounter.get_csn()
            condition_list = composition.get_encounter_conditions()

            for condition in condition_list:
                snomed_id = condition.get_snomed_id()
                dx_coding = condition.get_ICD9_id()

                if dx_coding:
                    dx_code_id = dx_coding.code
                    dx_code_system = dx_coding.system
                else:
                    dx_code_id = None
                    dx_code_system = None

                columns = [patient_id,
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
                # dx_ID = condition.get_problem_ID().value
                cur = yield from self.db.execute_single("SELECT upsert_condition(%s, %s, %s, %s, %s, %s, %s, %s::bigint, %s, %s, %s, %s, %s, %s)", extra=columns)
                cur.close()

        except:
            raise Exception("Error inserting encounter problem list into database")

    @ML.coroutine_trace(timing=True, write=FHIR_DB_LOG.debug)
    def write_composition_encounter_orders(self, composition):
        try:
            # Write encounter orders
            if composition.get_encounter_orders() is not None:
                for order in [(order) for order in composition.get_encounter_orders() if isinstance(order.detail[0], (FHIR_API.Medication, FHIR_API.Procedure))]:
                    yield from self.write_composition_encounter_order(order, composition)

            # Write procedure history orders
            if composition.get_procedure_history() is not None:
                for order in [(order) for order in composition.get_procedure_history() if isinstance(order.detail[0], (FHIR_API.Medication, FHIR_API.Procedure))]:
                    yield from self.write_composition_proc_history_order(order, composition)

        except:
            raise Exception("Error inserting composition encounter orders into database")

    @ML.coroutine_trace(timing=True, write=FHIR_DB_LOG.debug)
    def write_composition_encounter_order(self, order, composition):
        try:
            if isinstance(order.detail[0], FHIR_API.Procedure):
                code_id = order.detail[0].type.coding[0].code
                order_type = order.detail[0].type.text
            elif isinstance(order.detail[0], FHIR_API.Medication):
                code_id = order.detail[0].code.coding[0].code
                order_type = order.detail[0].code.text
            cmdargs = [composition.customer_id,
                       order.identifier[0].value,
                       composition.subject.get_pat_id(),
                       composition.encounter.get_csn(),
                       composition.get_author_id(),
                       composition.get_author_id(),
                       order.get_orderable_ID(),
                       order.status,
                       ORDER_SOURCE.WEBSERVICE.name,
                       code_id,
                       "clientEMR",
                       order.detail[0].text,
                       order_type,
                       order.detail[0].cost,
                       order.date]

            cur = yield from self.db.execute_single("SELECT upsert_enc_order(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", extra=cmdargs)
            cur.close()
        except:
            raise Exception("Error inserting encounter order into database")

    @ML.coroutine_trace(timing=True, write=FHIR_DB_LOG.debug)
    def write_composition_proc_history_order(self, order, composition):
        try:
            if isinstance(order.detail[0], FHIR_API.Procedure):
                code_id = order.detail[0].type.coding[0].code
                code_system = order.detail[0].type.coding[0].system
                order_type = order.detail[0].type.text
            elif isinstance(order.detail[0], FHIR_API.Medication):
                code_id = order.detail[0].code.coding[0].code
                order_type = order.detail[0].code.text
            cmdargs = [composition.customer_id,
                       '',
                       composition.subject.get_pat_id(),
                       composition.encounter.get_csn(),
                       composition.get_author_id(),
                       composition.get_author_id(),
                       order.get_orderable_ID(),
                       order.status,
                       ORDER_SOURCE.WEBSERVICE.name,
                       code_id,
                       code_system,
                       order.text,
                       order_type,
                       None,
                       order.detail[0].date]

            cur = yield from self.db.execute_single("SELECT upsert_historic_order(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", extra=cmdargs)
            cur.close()
        except:
            raise Exception("Error inserting encounter order into database")

    @ML.coroutine_trace(timing=True, write=FHIR_DB_LOG.debug)
    def write_composition_alerts(self, composition):

        customer_id = composition.customer_id
        patient_id = composition.subject.get_pat_id()
        provider_id = composition.get_author_id()
        encounter_id = composition.encounter.get_csn()

        for alert in composition.get_section_by_coding(code_system="maven", code_value="alerts").content:
            try:
                if alert.category in [ALERT_TYPES.CDS, ALERT_TYPES.REC_RESULT, ALERT_TYPES.ALT_MED]:
                    is_alert_with_triggering_order = True
                else:
                    is_alert_with_triggering_order = False

                column_map = ["customer_id",
                              "patient_id",
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
                              "status",
                              "validation_status",
                              "alert_uuid"]
                cmdargs = [customer_id,
                           patient_id,
                           provider_id,
                           encounter_id,
                           alert.CDS_rule,
                           alert.category.name,
                           alert.code_trigger,
                           alert.code_trigger_type,
                           alert.alert_datetime,
                           alert.short_title,
                           alert.long_title,
                           alert.short_description,
                           alert.long_description,
                           alert.status,
                           alert.validation_status,
                           str(alert.id)]

                if is_alert_with_triggering_order:
                    column_map.append("saving")
                    cmdargs.append(alert.saving)

                    column_map.append("order_id")
                    cmdargs.append(alert.triggering_order.get_clientEMR_uuid())

                columns = DBMapper.select_rows_from_map(column_map)

                cmd = []
                cmd.append("INSERT INTO alert")
                cmd.append("(" + columns + ")")

                if is_alert_with_triggering_order:
                    cmd.append("VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                else:
                    cmd.append("VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

                yield from self.db.execute_and_close_single(' '.join(cmd) + ';', cmdargs)
                yield from self.db.execute_and_close_single("INSERT INTO trees.activity "
                                                            "(customer_id, user_id, patient_id, protocol_id, datetime, action, canonical_id) "
                                                            "VALUES (%s, "
                                                            "(SELECT user_id FROM users WHERE customer_id=%s AND prov_id=%s),"
                                                            "%s, %s, now(), 'alert generated', "
                                                            "(SELECT canonical_id FROM trees.protocol WHERE customer_id=%s AND protocol_id = %s));",
                                                            (customer_id, customer_id, provider_id, patient_id, alert.CDS_rule, customer_id, alert.CDS_rule))
            except:
                raise Exception("Error inserting Alerts into the database")

    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    #####
    # CONSTRUCT FHIR OBJECTS FROM DATABASE
    #####
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    @ML.coroutine_trace(timing=True, write=FHIR_DB_LOG.debug)
    def construct_encounter_orders_from_db(self, composition):
        rtn_encounter_orders = []

        try:
            column_map = ["oo.customer_id",          # 0
                          "oo.order_id",
                          "oo.patient_id",
                          "oo.encounter_id",         # 3
                          "oo.ordering_provider_id",
                          "oo.auth_provider_id",
                          "oo.orderable_id",         # 6
                          "oo.status",
                          "oo.source",
                          "oo.code_id",              # 9
                          "oo.code_system",
                          "oo.order_name",
                          "oo.order_type",           # 12
                          "oo.order_cost",
                          "oo.order_cost_type",
                          "oo.order_datetime",       # 15
                          "od.cpt_code",
                          "od.cpt_version",
                          "od.rx_rxnorm_id"]         # 18
            columns = DBMapper.select_rows_from_map(column_map)

            cmd = []
            cmd.append("SELECT " + columns)
            cmd.append("FROM order_ord oo")
            cmd.append("JOIN orderable od ON oo.customer_id=od.customer_id and oo.orderable_id=od.orderable_id")
            cmd.append("WHERE oo.encounter_id=%s")
            cmd.append("AND oo.customer_id=%s")

            cmdargs = [composition.encounter.get_csn(), composition.customer_id]

            cur = yield from self.db.execute_single(' '.join(cmd), cmdargs)

            for result in cur:
                order_type = result[12]

                if order_type.lower() in PROCEDURE_ORDER_TYPES.__members__:
                    FHIR_procedure = FHIR_API.Procedure(text=result[11],
                                                        name=result[11],
                                                        type=FHIR_API.CodeableConcept(coding=[FHIR_API.Coding(system=result[17],
                                                                                                              code=result[16]),
                                                                                              FHIR_API.Coding(system="clientEMR",
                                                                                                              code=result[6])],
                                                                                      text="Procedure"))
                    rtn_encounter_orders.append(FHIR_API.Order(identifier=[FHIR_API.Identifier(system="clientEMR",
                                                                                               value=result[1],
                                                                                               label="Internal")],
                                                               date=result[15],
                                                               detail=[FHIR_procedure],
                                                               status=result[7]))

                elif order_type.lower() in MEDICATION_ORDER_TYPES.__members__:
                    FHIR_medication = FHIR_API.Medication(text=result[11],
                                                          name=result[1],
                                                          code=FHIR_API.CodeableConcept(coding=[FHIR_API.Coding(system="rxnorm",
                                                                                                                code=result[18]),
                                                                                                FHIR_API.Coding(system="clientEMR",
                                                                                                                code=result[6])],
                                                                                        text="Medication"))
                    rtn_encounter_orders.append(FHIR_API.Order(detail=[FHIR_medication],
                                                               date=result[15],
                                                               identifier=[FHIR_API.Identifier(system="clientEMR",
                                                                                               value=result[1],
                                                                                               label="Internal")],
                                                               status=result[7]))
            return rtn_encounter_orders

        except:
            raise Exception("Error constructing encounter order list from database")

    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    #####
    # COMPOSITION EVALUATOR(S) HELPER FUNCTIONS
    #####
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    @ML.coroutine_trace(timing=True, write=FHIR_DB_LOG.debug)
    def identify_encounter_orderable(self, item=None, order=None, composition=None):
        try:
            column_map = ["orderable_id",
                          "system",
                          "name",
                          "description",
                          "ord_type"]

            if isinstance(item, FHIR_API.CodeableConcept):
                column_map.extend(["cpt_code", "cpt_version", "rx_rxnorm_id", "rx_generic_name"])
                columns = DBMapper.select_rows_from_map(column_map)
                cmdargs = [tuple([(coding.code) for coding in item.coding]), composition.customer_id]
                cmd = []
                cmd.append("SELECT " + columns)
                cmd.append("FROM orderable")
                cmd.append("WHERE orderable_id IN %s AND (customer_id=%s OR customer_id=-1)")
                cmd.append("ORDER BY customer_id DESC")
                cmd.append("LIMIT 1;")

                try:
                    cur = yield from self.db.execute_single(' '.join(cmd), cmdargs)
                    result = cur.fetchone()

                    # Return the codeable concept so that downstream processes know that that a proper FHIR Med/Proc was never
                    #     identified for this codeable concept
                    if result is None:
                        return item

                    FHIR_DB_LOG.debug("Result from DB query (identify_encounter_orderable): %s" % [(result[x]) for x in range(len(result))])
                    orderable_id, system, name, description, order_type = self._get_base_order_elements_from_DB_cursor_result(result)

                    if order_type in ["Med", "Medication"]:
                        original_coding = FHIR_API.Coding(code=orderable_id, system=system, display=name)
                        rxnorm_coding = FHIR_API.Coding(code=result[7], system="rxnorm", display=name)
                        rtn_FHIR_medication = FHIR_API.Medication(text=name,
                                                                  identifier=order.identifier,
                                                                  name=name,
                                                                  code=FHIR_API.CodeableConcept(coding=[original_coding, rxnorm_coding],
                                                                                                text=order_type))
                        return rtn_FHIR_medication

                    elif order_type in ["Procedure", "Lab", "Imaging", "Proc"]:
                        original_coding = FHIR_API.Coding(code=orderable_id, system=system, display=name)
                        procedure_coding = FHIR_API.Coding(code=result[5], system=result[6], display=name)
                        rtn_FHIR_procedure = FHIR_API.Procedure(text=name,
                                                                identifier=order.identifier,
                                                                name=name,
                                                                type=FHIR_API.CodeableConcept(coding=[original_coding, procedure_coding],
                                                                                              text=order_type))
                        return rtn_FHIR_procedure
                except:
                    raise Exception("Error generating FHIR Medication/Procedure from Orderable table")

            elif isinstance(item, FHIR_API.Procedure):
                column_map.extend(["cpt_code", "cpt_version"])
                columns = DBMapper.select_rows_from_map(column_map)
                cmdargs = [tuple([(coding.code) for coding in item.type.coding]), composition.customer_id]
                cmd = []
                cmd.append("SELECT " + columns)
                cmd.append("FROM orderable")
                cmd.append("WHERE cpt_code IN %s AND (customer_id=%s OR customer_id=-1)")
                cmd.append("ORDER BY customer_id DESC")
                cmd.append("LIMIT 1;")

                cur = yield from self.db.execute_single(' '.join(cmd), cmdargs)
                result = cur.fetchone()

                if result is None:
                    return item.type

                FHIR_DB_LOG.debug("Result from DB query (identify_encounter_orderable): %s" % [(result[x]) for x in range(len(result))])
                orderable_id, system, name, description, order_type = self._get_base_order_elements_from_DB_cursor_result(result)
                del item.type.coding[:]
                item.type.coding.append(FHIR_API.Coding(code=result[5], system=result[6], display=name))
                item.type.coding.append(FHIR_API.Coding(code=orderable_id, system=system, display=name))
                item.identifier = order.identifier
                item.type.text = order_type
                item.name = name

                return item

            elif isinstance(item, FHIR_API.Medication):
                column_map.extend(["rx_rxnorm_id", "rx_generic_name"])
                columns = DBMapper.select_rows_from_map(column_map)
                cmdargs = [tuple([(coding.code) for coding in item.code.coding]), composition.customer_id]
                cmd = []
                cmd.append("SELECT " + columns)
                cmd.append("FROM orderable")
                cmd.append("WHERE cpt_code IN %s AND (customer_id=%s OR customer_id=-1)")
                cmd.append("ORDER BY customer_id DESC")
                cmd.append("LIMIT 1;")

                cur = yield from self.db.execute_single(' '.join(cmd), cmdargs)
                result = cur.fetchone()

                if result is None:
                    return item.code

                FHIR_DB_LOG.debug("Result from DB query (identify_encounter_orderable): %s" % [(result[x]) for x in range(len(result))])
                orderable_id, system, name, description, order_type = self._get_base_order_elements_from_DB_cursor_result(result)
                del item.code.coding[:]
                item.code.coding.append(FHIR_API.Coding(code=result[5], system=result[6], display=name))
                item.code.coding.append(FHIR_API.Coding(code=orderable_id, system=system, display=name))
                item.code.text = order_type
                item.identifier = order.identifier
                item.name = name

                return item
        except:
            raise Exception("Error identifying orderables")

    def _get_base_order_elements_from_DB_cursor_result(self, result):
        try:
            orderable_id = result[0]
            system = result[1]
            name = result[2]
            description = result[3]
            order_type = result[4]

            return orderable_id, system, name, description, order_type
        except:
            raise Exception("Error extracting base order elements from orderable table query")

    @ML.coroutine_trace(timing=True, write=FHIR_DB_LOG.debug)
    def get_order_detail_cost(self, order_detail, composition):
        try:
            column_map = ["cost",
                          "cost_type",
                          "customer_id",
                          "department",
                          "code",
                          "code_type",
                          "orderable_id"]
            columns = DBMapper.select_rows_from_map(column_map)

            cmd = []
            cmd.append("SELECT " + columns)
            cmd.append("FROM transparent.costmap")
            cmd.append("WHERE code=%s")
            cmd.append("AND code_type=%s")
            cmd.append("AND (customer_id=%s or customer_id=-1)")
            cmd.append("AND (department=%s or department='-1')")
            cmd.append("ORDER BY (customer_id, department, cost_type) DESC")
            cmd.append("LIMIT 1;")

            if len(composition.encounter.location) > 0:
                department = composition.encounter.location[0].identifier[0].value
            else:
                department = ""

            if isinstance(order_detail, FHIR_API.Procedure):
                proc_coding = order_detail.type.get_coding_by_system(["HCPCS", "CPT", "maven"])
                cmdargs = [proc_coding.code,
                           proc_coding.system,
                           composition.customer_id,
                           department]

            elif isinstance(order_detail, FHIR_API.Medication):
                med_coding = order_detail.code.get_coding_by_system(["rxnorm", "maven"])
                cmdargs = [med_coding.code,
                           med_coding.system,
                           composition.customer_id,
                           department]

            cur = yield from self.db.execute_single(' '.join(cmd), cmdargs)

            result = cur.fetchone()
            if not result:
                return None, None
            else:
                FHIR_DB_LOG.debug("Result from DB query (get_order_detail_cost): %s" % [(result[x]) for x in range(len(result))])
                return FHIR_API.round_up_five(result[0]), result[1]
        except:
            raise Exception("Error querying the transparent.costmap table")

    @ML.coroutine_trace(timing=True, write=FHIR_DB_LOG.debug)
    def get_snomeds_and_append_to_encounter_dx(self, composition):
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
                for coding in [c for c in condition.code.coding if c.code is not None]:
                    column_map = ["snomedid"]
                    columns = DBMapper.select_rows_from_map(column_map)
                    cur = yield from self.db.execute_single("select " + columns + " from terminology.codemap where code=%s and codetype=%s", extra=[coding.code, coding.system])
                    for result in cur:
                        FHIR_DB_LOG.info("Result from Database: %s, %s -> %s" % (coding.code, coding.system, result))
                        if result[0]:
                            snomed_ids.append(int(result[0]))
                    cur.close()

                for snomed_id in snomed_ids:
                    condition.code.coding.append(FHIR_API.Coding(system="SNOMED CT", code=snomed_id))
            return composition
        except:
            raise Exception("Error gathering SNOMED CT codes for Encounter Diagnoses")

    @ML.coroutine_trace(timing=True, write=FHIR_DB_LOG.debug)
    def get_recently_resulted_orders(self, composition):
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
            for order in [(order) for order in composition.get_encounter_orders() if isinstance(order.detail[0], (FHIR_API.Medication, FHIR_API.Procedure))]:
                if order.get_orderable_ID():
                    orderable_IDs_list.extend(order.get_orderable_ID())

            # for order in enc_ord_summary_section.content:
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
            cmd.append("WHERE order_ord.customer_id=%s AND order_ord.patient_id=%s AND order_ord.orderable_id IN %s AND order_ord.order_datetime > %s AND order_ord.order_datetime <= %s")

            cur = yield from self.db.execute_single(' '.join(cmd), cmdargs)

            for result in cur:
                FHIR_DB_LOG.debug("Result from DB query (get_recently_resulted_orders): %s" % [(result[x]) for x in range(len(result))])
                rtn_duplicate_orders[(result[0], result[1])] = {"order_id": result[2],
                                                                "encounter_id": result[3],
                                                                "order_name": result[4],
                                                                "date_time": result[5],
                                                                "order_type": result[6]}

            return rtn_duplicate_orders
        except:
            raise Exception("Error finding previous duplicate orders for this patient")

    @ML.coroutine_trace(timing=True, write=FHIR_DB_LOG.debug)
    def get_observations_from_duplicate_orders(self, duplicate_orders, composition):
        """

        """
        try:
            customer_id = composition.customer_id
            patient_id = composition.subject.get_pat_id()

            for ord in list(duplicate_orders):
                observations = []
                # order_code = ord[0]
                # order_code_system = ord[1]
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
                cur = yield from self.db.execute_single("select " + columns + " from observation where customer_id=%s and patient_id=%s and order_id=%s", extra=cmdargs)

                for result in cur:
                    FHIR_DB_LOG.debug("Result from DB query (get_observations_from_duplicate_orders): %s" % [(result[x]) for x in range(len(result))])
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

    @ML.coroutine_trace(timing=True, write=FHIR_DB_LOG.debug)
    def get_matching_CDS_rules(self, composition):
        try:
            # Pull a list of all the SNOMED CT codes from all of the conditions in the composition
            # It's important the the list/array of problem list/encounter DXs is an empty list as opposed to being null
            encounter_snomedIDs = composition.get_encounter_dx_snomeds()
            problem_list_snomedIDs = composition.get_problem_list_dx_snomeds()
            patient_age = composition.get_patient_age()

            # TODO - Need to replace this placeholder list of meds with the real meds
            patient_meds = []

            rtn_matched_rules = []
            for enc_ord in [(order) for order in composition.get_encounter_orders() if isinstance(order.detail[0], (FHIR_API.Medication, FHIR_API.Procedure))]:
                trigger_code = enc_ord.get_proc_med_terminology_coding()
                args = [trigger_code.code,
                        trigger_code.system,
                        patient_age,
                        composition.subject.gender,
                        encounter_snomedIDs,
                        problem_list_snomedIDs,
                        composition.subject.get_pat_id(),
                        composition.customer_id,
                        patient_meds]

                cur = yield from self.db.execute_single("SELECT * FROM choosewisely.evalrules(%s,%s,%s,%s,%s,%s,%s,%s,%s)", extra=args)

                for result in cur:
                    FHIR_DB_LOG.debug("Result from DB query (get_matching_CDS_rules): %s" % [(result[x]) for x in range(len(result))])
                    full_spec = json.loads(result[4])
                    rtn_matched_rules.append(FHIR_API.Rule(rule_details=result[2],
                                                           CDS_rule_id=result[0],
                                                           CDS_rule_status=result[3],
                                                           code_trigger=trigger_code.code,
                                                           code_trigger_type=trigger_code.system,
                                                           name=result[1],
                                                           short_title=full_spec['evidence']['short-title'],
                                                           short_description=full_spec['evidence']['short-description'],
                                                           long_title=full_spec['evidence']['long-title'],
                                                           long_description=full_spec['evidence']['long-description'],
                                                           triggering_order=enc_ord))
            return rtn_matched_rules
        except:
            raise Exception("Error extracting CDS rules from database")

    @ML.coroutine_trace(timing=True, write=FHIR_DB_LOG.debug)
    def get_matching_pathways(self, composition):
        try:
            # Pull a list of all the SNOMED CT codes from all of the conditions in the composition
            # It's important the the list/array of problem list/encounter DXs is an empty list as opposed to being null
            encounter_snomedIDs = composition.get_encounter_dx_snomeds()
            problem_list_snomedIDs = composition.get_problem_list_dx_snomeds()
            history_snomedIDs = composition.get_history_dx_snomeds()
            patient_age = composition.get_patient_age()
            provider_id = composition.author.get_provider_id()
            encounter_id = composition.encounter.get_csn()

            historic_procs = []
            if composition.get_procedure_history() is not None:
                for enc_ord in [(order) for order in composition.get_procedure_history() if isinstance(order.detail[0], FHIR_API.Procedure)]:
                    terminology_code = enc_ord.get_proc_med_terminology_coding()
                    historic_procs.append(terminology_code.code)

            # TODO - Need to replace this placeholder list of meds with the real meds
            patient_meds = []
            args = [1,
                    patient_age,
                    composition.subject.gender,
                    encounter_snomedIDs,
                    problem_list_snomedIDs,
                    history_snomedIDs,
                    composition.subject.get_pat_id(),
                    composition.customer_id,
                    patient_meds,
                    provider_id,
                    encounter_id,
                    historic_procs]
            cur = yield from self.db.execute_single("SELECT * FROM trees.evalnode(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", extra=args)

            code_list_items = []
            for result in cur:
                code_list_group_record = {
                    "protocol_id": result[0],
                    "protocol_name": result[1],
                    "protocol_desc": result[2],
                    "protocol_full_spec": json.loads(result[3]),
                    "protocol_priority": result[4],
                    "codelist_type": result[5],
                    "node_id": result[6],
                    "disjunctive_groupid": result[7],
                    "should_intersect": result[8],
                    "int_list": result[9],
                    "str_list": result[10],
                    "int_intersects": result[11],
                    "str_intersects": result[12],
                }
                code_list_items.append(code_list_group_record)
                # FHIR_DB_LOG.debug("Result from DB query (get_matching_pathways): %s" % [(result[x]) for x in range(len(result))])

            rtn_matched_rules = self._pathways_additional_selection_logic(code_list_items)
            return rtn_matched_rules
        except:
            raise Exception("Error matching pathways from database")

    def _pathways_additional_selection_logic(self, codelists):
        if not codelists:
            return []
        rtn_matched_rules = []
        cur_id = 0
        cur_id_processed = False
        cur_groupid = 0
        last_codelist_eval = True
        last_codelist = None
        for cl in codelists:

            # Don't process unnecessarily, continue with loop
            if cl.get('protocol_id') == cur_id and cur_id_processed:
                last_codelist = cl
                continue

            # No need evaluating the next codelist in the same protocol/group if the last codelist failed
            if cl.get('protocol_id', None) == cur_id and cl.get('disjunctive_groupid') == cur_groupid and not last_codelist_eval:
                last_codelist = cl
                continue

            # If the group changes and the last codelist passed, we assume the previous group evaluated to true
            if cl.get('protocol_id', None) == cur_id and cl.get('disjunctive_groupid') != cur_groupid and last_codelist_eval and cl.get('protocol_full_spec', None) is not None:
                rtn_matched_rules.append(FHIR_API.Rule(protocol_details=cl.get('protocol_full_spec'),
                                                       CDS_rule_id=cl.get('protocol_id'),
                                                       name=cl.get('protocol_name'),
                                                       short_description=cl.get('protocol_desc'),
                                                       priority=cl.get('protocol_priority')))
                cur_id_processed = True
                last_codelist = cl
                continue

            # If the id changes, and last codelist passed, we assume the group evaluated to true from the previous codelist
            if cl.get('protocol_id', None) != cur_id and last_codelist_eval and last_codelist is not None and last_codelist.get('protocol_full_spec', None) is not None:
                rtn_matched_rules.append(FHIR_API.Rule(protocol_details=last_codelist.get('protocol_full_spec'),
                                                       CDS_rule_id=last_codelist.get('protocol_id'),
                                                       name=last_codelist.get('protocol_name'),
                                                       short_description=last_codelist.get('protocol_desc'),
                                                       priority=last_codelist.get('protocol_priority')))

            if cl.get('protocol_id') != cur_id:
                cur_id = cl.get('protocol_id')
                cur_id_processed = False

            if cl.get('disjunctive_groupid') != cur_groupid:
                cur_groupid = cl.get('disjunctive_groupid')

            if cl.get('int_list', None) is not None:
                last_codelist_eval = True if cl.get('should_intersect') == cl.get('int_intersects') else False

            elif cl.get('str_list', None) is not None:
                last_codelist_eval = True if cl.get('should_intersect') == cl.get('str_intersects') else False

            last_codelist = cl

        # If last_codelist_eval is True at the end, we assume the group/codelist passed, so we add the last_codelist
        if last_codelist_eval and last_codelist and last_codelist.get('protocol_full_spec', None) is not None:
            rtn_matched_rules.append(FHIR_API.Rule(protocol_details=last_codelist.get('protocol_full_spec'),
                                                   CDS_rule_id=last_codelist.get('protocol_id'),
                                                   name=last_codelist.get('protocol_name'),
                                                   short_description=last_codelist.get('protocol_desc'),
                                                   priority=last_codelist.get('protocol_priority')))

        return rtn_matched_rules

    @ML.coroutine_trace(timing=True, write=FHIR_DB_LOG.debug)
    def get_user_group_membership(self, provider_username, customer_id):
        column_map = ["group_id"]
        columns = DBMapper.select_rows_from_map(column_map)

        cmd = []
        cmd.append("SELECT " + columns)
        cmd.append("FROM user_membership")
        cmd.append("WHERE customer_id=%s")
        cmd.append("AND user_name=%s")
        cmdargs = [customer_id, provider_username]

        rtn = []
        cur = None
        try:
            cur = yield from self.db.execute_single(' '.join(cmd), cmdargs)
            for result in cur:
                rtn.append(result[0])
        except Exception as e:
            rtn = e
        finally:
            if cur:
                cur.close()
            return rtn

    @ML.coroutine_trace(timing=True, write=FHIR_DB_LOG.debug)
    def get_alternative_meds(self, order, composition):
        return []

    @ML.coroutine_trace(timing=True, write=FHIR_DB_LOG.debug)
    def get_alert_configuration(self, ALERT_TYPE, composition):
        try:
            if len(composition.encounter.location) > 0:
                department = composition.encounter.location[0].identifier[0].value
            else:
                department = -1

            customer_id = composition.customer_id

            column_map = ["validation_status",
                          "department",
                          "category",
                          "rule_id",
                          "provide_optouts"]
            columns = DBMapper.select_rows_from_map(column_map)

            cmd = []
            cmd.append("SELECT " + columns)
            cmd.append("FROM alert_config")
            cmd.append("WHERE (customer_id=%s or customer_id=-1)")
            cmd.append("AND category=%s")
            cmd.append("AND (department=%s or department='-1')")
            cmd.append("ORDER BY customer_id DESC, department DESC")
            cmd.append("LIMIT 1;")
            cmdargs = [customer_id, ALERT_TYPE.name, department]

            cur = yield from self.db.execute_single(' '.join(cmd), cmdargs)

            rtn_alert_validation_status = cur.fetchone()

            if rtn_alert_validation_status is None:
                FHIR_DB_LOG.debug("No alert_config record for Alert Type: %s" % ALERT_TYPE.name)
                return ALERT_VALIDATION_STATUS.SUPPRESS.value

            else:
                FHIR_DB_LOG.debug("Result from DB query (get_alert_configuration): %s" %
                                  [(rtn_alert_validation_status[x]) for x in range(len(rtn_alert_validation_status))])
                return rtn_alert_validation_status[0]
        except:
            raise Exception("Error retrieving COST alert configuration from database")
