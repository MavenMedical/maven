# *************************************************************************
# Copyright (c) 2014 - Maven Medical
# ************************
# AUTHOR:
__author__ = 'Yuki Uchino'
# ************************
# DESCRIPTION:   This composition_evaluator.py contains the classes required to process a
#                FHIR Composition object through Maven Sleuth Rule Engine.
#
#
#
# ************************
# ASSUMES:
# ************************
# SIDE EFFECTS:
# ************************
# LAST MODIFIED FOR JIRA ISSUE: MAV-123
# *************************************************************************
#       .---.        .-----------
#      /     \  __  /    ------
#     / /     \(  )/    -----
#    //////   ' \/ `   ---
#   //// / // :    : ---
#  // /   /  /`    '--
# //          //..\\
#        ====UU====UU====
#            '//||\\`
#              ''``
# *************************************************************************
import pickle
import asyncio
import datetime
import maven_config as MC
import maven_logging as ML
import utils.database.fhir_database as FD
from utils.enums import ALERT_VALIDATION_STATUS, ORDER_STATUS, ALERT_TYPES, CONFIG_PARAMS
import utils.api.pyfhir.pyfhir_generated as FHIR_API
import utils.streaming.stream_processor as SP

COMP_EVAL_LOG = ML.get_logger()


class CompositionEvaluator(SP.StreamProcessor):

    def __init__(self, configname, fhir_persistence):
        SP.StreamProcessor.__init__(self, configname)
        self.fhir_persistence = fhir_persistence

    def schedule(self, loop):
        SP.StreamProcessor.schedule(self, loop)

    @asyncio.coroutine
    def read_object(self, obj, _):
        ML.INFO("comp_evaluator received a composition")

        # Load the FHIR Composition from the pickle
        composition = pickle.loads(obj)

        # Write the original composition that came across the wire for debugging purposes
        # Eventually we'll want the DB write method below to update the composition as opposed to writing it again
        yield from self.fhir_persistence.write_composition_json(composition)

        # Add the alerts section so that the components below can add their respective alerts
        self._add_alerts_section(composition)

        # Identify Encounter Orderables
        yield from self.identify_encounter_orderables(composition)

        # Send composition to fanout_evaluator RabbitMQ exchange
        # self.write_object(composition, writer_key='logging')

        # Detect deleted/removed/canceled orders from new set
        yield from self.detect_removed_orders(composition)

        # Maven Transparency
        yield from self.evaluate_encounter_cost(composition)

        # Maven Duplicate Orders (with related Clinical Observations) analysis
        yield from self.evaluate_recent_results(composition)

        # Maven Alternative Meds
        yield from self.evaluate_alternative_meds(composition)

        # Use the FHIR Database API to look up each Condition's codes (ICD-9) and add Snomed CT concepts to the Condition
        composition = yield from self.fhir_persistence.get_snomeds_and_append_to_encounter_dx(composition)

        # Analyze Choosing Wisely/CDS Rules
        yield from self.evaluate_CDS_rules(composition)

        # Maven Pathways
        yield from self.evaluate_clinical_pathways(composition)

        # Write everything to persistent DB storage
        yield from self.fhir_persistence.write_composition_to_db(composition)

        # Debug Message
        # COMP_EVAL_LOG.debug(json.dumps(FHIR_API.remove_none(json.loads(json.dumps(composition, default=FHIR_API.jdefault))), default=FHIR_API.jdefault, indent=4))

        # Send message back to data_router (or aggregate)
        self.write_object(composition, writer_key='aggregate')

    def _add_alerts_section(self, composition):
        composition.section.append(FHIR_API.Section(title="Maven Alerts", code=FHIR_API.CodeableConcept(text="Maven Alerts", coding=[FHIR_API.Coding(system="maven",
                                                                                                                                                     code="alerts")])))

    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    #####
    # IDENTIFY INCOMING ENCOUNTER ORDERABLES
    #####
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    @ML.coroutine_trace(write=COMP_EVAL_LOG.debug, timing=True)
    def identify_encounter_orderables(self, composition):

        try:
            if composition.get_encounter_orders() is None:
                return

            for order in composition.get_encounter_orders():

                # Loop through each order_detail in each order to identify
                detail_orders = yield from [(yield from self.fhir_persistence.identify_encounter_orderable(item, order, composition)) for item in order.detail]

                # TODO - Check to make sure duplicate codes that reference the same orderable don't result in duplicate FHIR Procedures/Medications

                # Remove the placeholder(s) CodeableConcept/FHIR Procedure/FHIR Medication from the order.detail list
                del order.detail[:]

                # Add the fully-matched FHIR Procedure/Medication(s) to the Composition Order
                order.detail.extend(detail_orders)
        except:
            raise Exception("Error extracting encounter orders from composition object")

    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    #####
    # DETECT ORDER EVENTS (REMOVED/CANCELED/COMPLETED/ETC)
    #####
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    @ML.coroutine_trace(write=COMP_EVAL_LOG.debug, timing=True)
    def detect_removed_orders(self, composition):

        try:
            if composition.get_encounter_orders() is None:
                return

            # Build a list of FHIR_API.Orders encounter orders in the database.order_ord
            orders_from_db = yield from self.fhir_persistence.construct_encounter_orders_from_db(composition)

            # Check the tuple of (internal ID, orderable_id) to see if there's overlap
            new_orders_clientEMR_IDs = [(order.get_clientEMR_uuid(), order.get_orderable_ID()) for order in composition.get_encounter_orders()]
            old_orders_clientEMR_IDs = [(order.get_clientEMR_uuid(), order.get_orderable_ID()) for order in orders_from_db]

            missing_orders = [old_order for old_order in old_orders_clientEMR_IDs if old_order not in new_orders_clientEMR_IDs]

            # Update FHIR_Order.status and write changes to DB for each of the orders found in missing_orders
            if missing_orders is not None and len(missing_orders) > 0:
                for order in [(db_order) for db_order in orders_from_db for order in missing_orders if order[0] == db_order.identifier[0].value]:

                    # Put the Order in a status of ON HOLD which means we need to figure out if it was Completed/Removed/Canceled
                    order.status = ORDER_STATUS.HD.name
                    yield from self.fhir_persistence.write_composition_encounter_order(order, composition)
        except:
            raise Exception("Error detecting removed orders")

    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    #####
    # EVALUATE ENCOUNTER COST
    #####
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    @ML.coroutine_trace(write=COMP_EVAL_LOG.debug, timing=True)
    def evaluate_encounter_cost(self, composition):
        """
        :param composition: FHIR Composition object with fully identified FHIR Order objects (i.e. already run through order identifier
        """
        # Check the alert configuration for cost and if it's suppress (-1) then return
        cost_alert_validation_status = yield from self.fhir_persistence.get_alert_configuration(ALERT_TYPES.COST, composition)
        if cost_alert_validation_status == ALERT_VALIDATION_STATUS.SUPPRESS.value:
            return

        encounter_cost_breakdown = {"total_cost": 0, "details": []}

        for order in [(order) for order in composition.get_encounter_orders() if isinstance(order.detail[0], (FHIR_API.Medication, FHIR_API.Procedure))]:
            order.totalCost = 0
            coding = order.get_proc_med_terminology_coding()
            for order_detail in order.detail:
                yield from self.fhir_persistence.get_order_detail_cost(order_detail, composition)
                order.totalCost += order_detail.cost

            encounter_cost_breakdown['details'].append({"order_name": coding.display,
                                                        "order_cost": order_detail.cost,
                                                        "order_type": order_detail.resourceType})
            encounter_cost_breakdown['total_cost'] += order.totalCost

        # Only generate the alert if there are costs to show
        if len(encounter_cost_breakdown['details']) > 0 and encounter_cost_breakdown['total_cost'] > 0:
            alert_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            short_title = ("Encounter Cost: %s" % encounter_cost_breakdown['total_cost'])

            # Create a storeable text description of the cost breakdown details list
            long_description = ""
            for cost_element in encounter_cost_breakdown['details']:
                long_description += ("%s: $%s\n" % (cost_element['order_name'], cost_element['order_cost']))

            FHIR_alert = FHIR_API.Alert(customer_id=composition.customer_id, subject=composition.subject.get_pat_id(),
                                        provider_id=composition.get_author_id(), encounter_id=composition.encounter.get_csn(),
                                        alert_datetime=alert_datetime, short_title=short_title, cost_breakdown=encounter_cost_breakdown,
                                        long_description=long_description, validation_status=cost_alert_validation_status,
                                        category=ALERT_TYPES.COST)

            alerts_section = composition.get_section_by_coding(code_system="maven", code_value="alerts")
            alerts_section.content.append(FHIR_alert)

    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    #####
    # EVALUATE DUPLICATE ORDERS
    #####
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    @ML.coroutine_trace(write=COMP_EVAL_LOG.debug, timing=True)
    def evaluate_recent_results(self, composition):
        # Check to see if recent results alert_config should event generate alerts
        recent_results_alert_validation_status = yield from self.fhir_persistence.get_alert_configuration(ALERT_TYPES.REC_RESULT, composition)
        if recent_results_alert_validation_status == ALERT_VALIDATION_STATUS.SUPPRESS.value:
            return

        # Check to see if there are exact duplicate orders (order code AND order code type)from within the last year
        duplicate_orders = yield from self.fhir_persistence.get_recently_resulted_orders(composition)

        if duplicate_orders is not None and len(duplicate_orders) > 0:
            # Check to see if there are relevant lab components to be displayed
            duplicate_orders_with_observations = yield from self.fhir_persistence.get_observations_from_duplicate_orders(duplicate_orders, composition)

            if duplicate_orders_with_observations is not None and len(duplicate_orders_with_observations) > 0:
                yield from self._generate_recent_results_alerts(composition, duplicate_orders_with_observations)

    @ML.coroutine_trace(write=COMP_EVAL_LOG.debug, timing=True)
    def _generate_recent_results_alerts(self, composition, dup_ords_with_obs):

        # Check to see if recent results alert_config should event generate alerts
        recent_results_alert_validation_status = yield from self.fhir_persistence.get_alert_configuration(ALERT_TYPES.REC_RESULT, composition)
        if recent_results_alert_validation_status == ALERT_VALIDATION_STATUS.SUPPRESS.value:
            return

        customer_id = composition.customer_id
        patient_id = composition.subject.get_pat_id()
        alert_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        for ord in list(dup_ords_with_obs):
            order_code = ord[0]
            order_code_system = ord[1]
            order = composition.get_encounter_order_by_clientEMR_uuid(dup_ords_with_obs[ord]["order_id"])
            ord_detail = composition.get_encounter_order_detail_by_coding(code=order_code, code_system="clientEMR")

            # Create a storeable text description of the related clinical observations list
            long_description = ""
            for observation in dup_ords_with_obs[ord]['related_observations']:
                ord_detail.relatedItem.append(observation)
                long_description += ("%s: %s %s (%s)" % (observation.name,
                                                         observation.valueQuantity.value,
                                                         observation.valueQuantity.units,
                                                         observation.appliesdateTime))

            FHIR_alert = FHIR_API.Alert(customer_id=customer_id,
                                        subject=patient_id,
                                        provider_id=composition.get_author_id(),
                                        encounter_id=composition.encounter.get_csn(),
                                        code_trigger=order_code,
                                        code_trigger_type=order_code_system,
                                        alert_datetime=alert_datetime,
                                        short_title=("Duplicate Order: %s" % ord_detail.text),
                                        short_description="Clinical observations are available for a duplicate order recently placed.",
                                        long_description=long_description,
                                        saving=order.totalCost,
                                        related_observations=dup_ords_with_obs[ord]['related_observations'],
                                        category=ALERT_TYPES.REC_RESULT,
                                        validation_status=recent_results_alert_validation_status,
                                        triggering_order=order)

            alerts_section = composition.get_section_by_coding(code_system="maven", code_value="alerts")
            alerts_section.content.append(FHIR_alert)

    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    #####
    # EVALUATE ALTERNATIVE MEDICATIONS
    #####
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    @ML.coroutine_trace(write=COMP_EVAL_LOG.debug, timing=True)
    def evaluate_alternative_meds(self, composition):
        # Check to see if recent results alert_config should event generate alerts
        alt_meds_alert_validation_status = yield from self.fhir_persistence.get_alert_configuration(ALERT_TYPES.ALT_MED, composition)
        if alt_meds_alert_validation_status == ALERT_VALIDATION_STATUS.SUPPRESS.value:
            return

        for order in composition.get_encounter_orders():
            if isinstance(order.detail[0], FHIR_API.Medication):
                alt_meds = yield from self.fhir_persistence.get_alternative_meds(order, composition)
                if alt_meds:
                    pass

    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    #####
    # EVALUATE CHOOSING WISELY RULES
    #####
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    @ML.coroutine_trace(write=COMP_EVAL_LOG.debug, timing=True)
    def evaluate_CDS_rules(self, composition):
        """

        """
        # Check to see if recent results alert_config should event generate alerts
        CDS_rules_alert_validation_status = yield from self.fhir_persistence.get_alert_configuration(ALERT_TYPES.CDS, composition)
        if CDS_rules_alert_validation_status == ALERT_VALIDATION_STATUS.SUPPRESS.value:
            return

        # Gather any matching CDS Rules that hit according to Dave's rules.evalrules PL/pgsql function
        CDS_rules = yield from self.fhir_persistence.get_matching_CDS_rules(composition)

        # If Dave's evalrules PL/pgsql function returns any rules, go through and evaluate the rule details
        cds_alerts = []
        if CDS_rules is not None and len(CDS_rules) > 0:
            for rule in CDS_rules:
                if (yield from self._evaluate_CDS_rule_details(composition, rule)):
                    cds_alert = yield from self.generate_cds_alert(composition, rule)
                    cds_alerts.append(cds_alert)

        # Add a CDS Alerts section to the FHIR Composition if any of the CDS rules pass all the rule details
        if cds_alerts is not None and len(cds_alerts) > 0:
            alerts_section = composition.get_section_by_coding(code_system="maven", code_value="alerts")
            alerts_section.content.extend(cds_alerts)

    @ML.coroutine_trace(write=COMP_EVAL_LOG.debug, timing=True)
    def _evaluate_CDS_rule_details(self, composition, rule):
        # Check to make sure that the FHIR_Rule.CDS_rule_status is not -1 (which is to suppress rule for internal/performance reasons)
        if rule.CDS_rule_status == ALERT_VALIDATION_STATUS.SUPPRESS.value:
            return False

        additional_dx_details_result = yield from self._evaluate_additional_dx_rule_details(composition, rule.encounter_dx_rules)
        lab_rule_details_result = yield from self._evaluate_lab_rule_details(composition, rule.lab_rules)
        med_rule_details_result = yield from self._evaluate_medication_rule_details(composition, None)

        if additional_dx_details_result and lab_rule_details_result and med_rule_details_result:
            return True
        else:
            return False

    # @ML.coroutine_trace(write=COMP_EVAL_LOG.debug, timing=True)
    @asyncio.coroutine
    def _evaluate_additional_dx_rule_details(self, composition, dx_rule_details):
        return True

    # @ML.coroutine_trace(write=COMP_EVAL_LOG.debug, timing=True)
    @asyncio.coroutine
    def _evaluate_lab_rule_details(self, composition, lab_rule_details):
        return True

    # @ML.coroutine_trace(write=COMP_EVAL_LOG.debug, timing=True)
    @asyncio.coroutine
    def _evaluate_medication_rule_details(self, composition, med_rule_details):
        return True

    # @ML.coroutine_trace(write=COMP_EVAL_LOG.debug, timing=True)
    @asyncio.coroutine
    def generate_cds_alert(self, composition, rule):
        """
        Generates an alert from the rule that evaluated to true, along with the evidence that supports that rule (from a clinical perspective)

        :param composition: The composition that is being analyzed. This method attaches a new FHIR SECTION to the composition
        :param rule: The sleuth_rule that evaluated to truec
        :param evidence: A LIST of evidence that supports the rule.
        """

        customer_id = composition.customer_id
        pat_id = composition.subject.get_pat_id()
        provider_id = composition.get_author_id()
        encounter_id = composition.encounter.get_csn()
        code_trigger = rule.code_trigger
        CDS_rule = rule.CDS_rule_id
        alert_datetime = datetime.datetime.now()
        short_title = rule.short_title
        long_title = rule.long_title
        short_description = rule.short_description
        long_description = rule.long_description
        override_indications = ['Select one of these override indications boink']
        saving = rule.triggering_order.totalCost
        category = ALERT_TYPES.CDS

        FHIR_alert = FHIR_API.Alert(customer_id=customer_id, subject=pat_id, provider_id=provider_id, encounter_id=encounter_id,
                                    code_trigger=code_trigger, code_trigger_type=rule.code_trigger_type, CDS_rule=CDS_rule, alert_datetime=alert_datetime,
                                    short_title=short_title, long_title=long_title, short_description=short_description, long_description=long_description,
                                    override_indications=override_indications, saving=saving, category=category, validation_status=rule.CDS_rule_status,
                                    triggering_order=rule.triggering_order)

        return FHIR_alert

    @ML.coroutine_trace(write=COMP_EVAL_LOG.debug, timing=True)
    def gather_evidence(self, rule, customer_id):
        evidence = []
        column_map = ["sleuth_evidence.name",
                      "sleuth_evidence.description",
                      "sleuth_evidence.source",
                      "sleuth_evidence.source_url"]
        columns = self.DBMapper.select_rows_from_map(column_map)
        cur = yield from self.conn.execute_single("select " + columns + " from sleuth_evidence where sleuth_rule=%s and customer_id=%s", extra=[rule.CDS_rule_id, customer_id])
        for result in cur:
            evidence.append(result)

        return evidence

    @ML.coroutine_trace(write=COMP_EVAL_LOG.debug, timing=True)
    def get_override_indications(self, rule, customer_id):
        override_indications = []
        column_map = ["override_indication.name",
                      "override_indication.description"]

        columns = self.DBMapper.select_rows_from_map(column_map)

        cur = yield from self.conn.execute_single("select " + columns + " from override_indication where sleuth_rule=%s and customer_id=%s", extra=[rule.CDS_rule_id, customer_id])
        for result in cur:
            override_indications.append(result)

        return override_indications

    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    #####
    # EVALUATE MAVEN PATHWAYS
    #####
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    @ML.coroutine_trace(write=COMP_EVAL_LOG.debug, timing=True)
    def evaluate_clinical_pathways(self, composition):
        pathways_alert_validation_status = yield from self.fhir_persistence.get_alert_configuration(ALERT_TYPES.PATHWAY, composition)
        if pathways_alert_validation_status == ALERT_VALIDATION_STATUS.SUPPRESS.value:
            return

        # The FHIR_database.py function here returns a list of FHIR.Rule objects that correspond to the Pathway
        matched_pathways = yield from self.fhir_persistence.get_matching_pathways(composition)

        if matched_pathways and len(matched_pathways) > 0:
            alerts_section = composition.get_section_by_coding(code_system="maven", code_value="alerts")

            # Discussion 2014-11-11 Yuki-Dave: we should just send the highest priority pathway if multiple are triggered
            matched_pathways.sort(key=lambda x: x.priority, reverse=True)
            for pathway in matched_pathways:
                FHIR_alert = FHIR_API.Alert(customer_id=composition.customer_id,
                                            category=ALERT_TYPES.PATHWAY,
                                            subject=composition.subject.get_pat_id(),
                                            CDS_rule=pathway.CDS_rule_id,
                                            priority=pathway.priority,
                                            provider_id=composition.get_author_id(),
                                            encounter_id=composition.encounter.get_csn(),
                                            alert_datetime=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                                            short_title=("Clinical Pathway Detected"),
                                            long_title=pathway.name,
                                            short_description=("Clinical Pathway recommendations are available"),
                                            long_description=("Clinical Pathway recommendations are available"))
                alerts_section.content.append(FHIR_alert)

            # Old logic for looping through multiple returned Pathway Rules. Instead, we're sorting based on priority
            # and creating an Alert for only the highest priority
            """
            for pathway in matched_pathways:
                FHIR_alert = FHIR_API.Alert(customer_id=composition.customer_id,
                                            category=ALERT_TYPES.PATHWAY,
                                            subject=composition.subject.get_pat_id(),
                                            CDS_rule=pathway.CDS_rule_id,
                                            priority=pathway.priority,
                                            provider_id=composition.get_author_id(),
                                            encounter_id=composition.encounter.get_csn(),
                                            alert_datetime=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                                            short_title=("Clinical Pathway Detected"),
                                            short_description=("Clinical Pathway recommendations are available"),
                                            long_description=("Clinical Pathway recommendations are available"))
                alerts_section.content.append(FHIR_alert)
            """

    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    #####
    # EVALUATE MAVEN TASKS FOR PROVIDER/PATIENT
    #####
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    """
    @ML.coroutine_trace(write=COMP_EVAL_LOG.debug, timing=True)
    def evaluate_tasks(self, composition):
        column_map = ["delivery_method",
                      "status",
                      "due",
                      "expire",
                      "msg_subject",
                      "msg_body"]
        columns = self.DBMapper.select_rows_from_map(column_map)
        cmd = ["SELECT (" + columns + ")",
               "FROM followuptask",
               "WHERE customer_id=%s AND user_name=%s AND "]
    """


def run_composition_evaluator():

    rabbithandler = 'rabbitmessagehandler'
    rpc_database_stream_processor = 'Client to Database RPC Stream Processor'

    MavenConfig = {
        rabbithandler:
        {
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
            SP.CONFIG_READERNAME: rabbithandler + ".Reader",
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
            SP.CONFIG_WRITERNAME: [rabbithandler + ".Writer", rabbithandler + ".Writer2"],
            SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_IDENTITYPARSER,

        },
        rabbithandler + ".Reader":
        {
            SP.CONFIG_HOST: 'localhost',
            SP.CONFIG_QUEUE: 'incoming_cost_evaluator_work_queue',
            SP.CONFIG_EXCHANGE: 'maven_exchange',
            SP.CONFIG_KEY: 'incomingcosteval'
        },

        rabbithandler + ".Writer":
        {
            SP.CONFIG_HOST: 'localhost',
            SP.CONFIG_QUEUE: 'aggregator_work_queue',
            SP.CONFIG_EXCHANGE: 'maven_exchange',
            SP.CONFIG_KEY: 'aggregate',
            SP.CONFIG_WRITERKEY: 'aggregate',
        },

        rabbithandler + ".Writer2":
        {
            SP.CONFIG_HOST: 'localhost',
            SP.CONFIG_QUEUE: 'logger_work_queue',
            SP.CONFIG_EXCHANGE: 'fanout_evaluator',
            SP.CONFIG_KEY: 'logging',
            SP.CONFIG_WRITERKEY: 'logging',
        },
        CONFIG_PARAMS.PERSISTENCE_SVC.value: {FD.CONFIG_DATABASE: rpc_database_stream_processor},
        rpc_database_stream_processor: {
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETREPLY,
            SP.CONFIG_WRITERNAME: rpc_database_stream_processor + '.Writer1',
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETQUERY,
            SP.CONFIG_READERNAME: rpc_database_stream_processor + '.Reader1',
            SP.CONFIG_WRITERDYNAMICKEY: 4,
            SP.CONFIG_DEFAULTWRITEKEY: 4,
        },
        rpc_database_stream_processor + ".Writer1": {
            SP.CONFIG_WRITERKEY: 4,
        },
        rpc_database_stream_processor + ".Reader1": {
            SP.CONFIG_HOST: MC.dbhost,
            SP.CONFIG_PORT: '54729',
        },
    }

    MC.MavenConfig.update(MavenConfig)

    fhir_persistence = FD.FHIRPersistence(CONFIG_PARAMS.PERSISTENCE_SVC.value)

    loop = asyncio.get_event_loop()
    sp_message_handler = CompositionEvaluator(rabbithandler, fhir_persistence)
    sp_message_handler.schedule(loop)

    try:
        loop.run_until_complete(asyncio.Task(fhir_persistence.test()))
        loop.run_forever()

    except KeyboardInterrupt:
        sp_message_handler.close()
        loop.close()

if __name__ == '__main__':
    run_composition_evaluator()
