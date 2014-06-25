#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:   This composition_evaluator.py contains the classes required to process a
#               FHIR Composition object through Maven Sleuth Rule Engine.
#
#
#
#************************
#ASSUMES:
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-123
#*************************************************************************
#      .---.        .-----------
#     /     \  __  /    ------
#    / /     \(  )/    -----
#   //////   ' \/ `   ---
#  //// / // :    : ---
# // /   /  /`    '--
#//          //..\\
#       ====UU====UU====
#           '//||\\`
#             ''``
#*************************************************************************
import pickle
import asyncio
import datetime
import json
import math
from collections import defaultdict
import maven_config as MC
from utils.database.database import AsyncConnectionPool, MappingUtilites
import utils.database.fhir_database as FHIR_DB
import utils.api.pyfhir.pyfhir_generated as FHIR_API
import utils.streaming.stream_processor as SP


class CompositionEvaluator(SP.StreamProcessor):

    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)
        self.conn = AsyncConnectionPool('EvaluatorConnectionPool')
        self.DBMapper = MappingUtilites()

    def schedule(self, loop):
        SP.StreamProcessor.schedule(self, loop)
        self.conn.schedule(loop)

    @asyncio.coroutine
    def read_object(self, obj, _):

        #Look up prices via costmap and create new "Encounter Cost Breakdown" section that is added to Composition
        composition = pickle.loads(obj)

        #Add the alerts section so that the components below can add their respective alerts
        self._add_alerts_section(composition)

        #Identify Encounter Orderables
        yield from self.identify_encounter_orderables(composition)

        #Maven Transparency
        yield from self.evaluate_encounter_cost(composition)

        #Maven Duplicate Orders (with related Clinical Observations) analysis
        yield from self.evaluate_duplicate_orders(composition)

        #Maven Alternative Meds
        yield from self.evaluate_alternative_meds(composition)

        #Use the FHIR Database API to look up each Condition's codes (ICD-9) and add Snomed CT concepts to the Condition
        yield from FHIR_DB.get_snomeds_and_append_to_encounter_dx(composition, self.conn)

        #Analyze Choosing Wisely/CDS Rules
        yield from self.evaluate_CDS_rules(composition)

        #Write everything to persistent DB storage
        yield from FHIR_DB.write_composition_to_db(composition, self.conn)

        #Send message back to data_router (or aggregate)
        self.write_object(composition, writer_key='aggregate')

        #Debug Message
        comp_json = json.dumps(composition, default=FHIR_API.jdefault, indent=4)
        print(json.dumps(FHIR_API.remove_none(json.loads(comp_json)), default=FHIR_API.jdefault, indent=4))

    def _add_alerts_section(self, composition):
        composition.section.append(FHIR_API.Section(title="Maven Alerts", code=FHIR_API.CodeableConcept(text="Maven Alerts", coding=[FHIR_API.Coding(system="maven",
                                                                                                                                                     code="alerts")])))
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    #####
    ##### IDENTIFY INCOMING ENCOUNTER ORDERABLES
    #####
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    @asyncio.coroutine
    def identify_encounter_orderables(self, composition):

        for order in composition.get_encounter_orders():

            detail_orders = yield from [(yield from FHIR_DB.identify_encounter_orderable(item, order, composition, self.conn)) for item in order.detail]

            #TODO - Check to make sure duplicate codes that reference the same orderable don't result in duplicate FHIR Procedures/Medications

            #Remove the placeholder(s) CodeableConcept/FHIR Procedure/FHIR Medication from the order.detail list
            del order.detail[:]

            #Add the fully-matched FHIR Procedure/Medication(s) to the Composition Order
            order.detail.extend(detail_orders)

    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    #####
    ##### EVALUATE ENCOUNTER COST
    #####
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    @asyncio.coroutine
    def evaluate_encounter_cost(self, composition):
        """
        :param composition: FHIR Composition object with fully identified FHIR Order objects (i.e. already run through order identifier
        """

        encounter_cost_breakdown = []
        encounter_total_cost = 0
        for order in composition.get_encounter_orders():
            order_total_cost = 0
            for order_detail in order.detail:
                order_total_cost += order_detail.base_cost
                if isinstance(order_detail, FHIR_API.Procedure):
                    codeable_concept = order_detail.type
                elif isinstance(order_detail, FHIR_API.Medication):
                    codeable_concept = order_detail.code
                coding = composition.get_coding_from_codeable_concept(codeable_concept=codeable_concept, system=["clientEMR", "CPT", "rxnorm"])
                encounter_cost_breakdown.append({"order_name": coding.display,
                                                 "order_cost": order_detail.base_cost,
                                                 "order_type": order_detail.resourceType})
            encounter_total_cost += order_total_cost

        if encounter_cost_breakdown is not None and len(encounter_cost_breakdown) > 0:
            alert_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            short_title = ("Encounter Cost: %s" % encounter_total_cost)

            #Create a storeable text description of the cost breakdown details list
            long_description = ""
            for cost_element in encounter_cost_breakdown:
                long_description += ("%s: $%s\n" % (cost_element['order_name'], cost_element['order_cost']))


            FHIR_alert = FHIR_API.Alert(customer_id=composition.customer_id, subject=composition.subject.get_pat_id(),
                                        provider_id=composition.get_author_id(), encounter_id=composition.encounter.get_csn(),
                                        alert_datetime=alert_datetime, short_title=short_title, cost_breakdown=encounter_cost_breakdown, long_description=long_description)

            cost_alert = {"alert_type": "cost",
                          "alert_time" : alert_datetime,
                          "total_cost": encounter_total_cost,
                          "cost_details": encounter_cost_breakdown,
                          "alert_list": [FHIR_alert]}

            alerts_section = composition.get_section_by_coding(code_system="maven", code_value="alerts")
            alerts_section.content.append(cost_alert)

    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    #####
    ##### EVALUATE DUPLICATE ORDERS
    #####
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    @asyncio.coroutine
    def evaluate_duplicate_orders(self, composition):

        #Check to see if there are exact duplicate orders (order code AND order code type)from within the last year
        duplicate_orders = yield from FHIR_DB.get_duplicate_orders(composition, self.conn)

        if duplicate_orders is not None and len(duplicate_orders) > 0:
            #Check to see if there are relevant lab components to be displayed
            duplicate_orders_with_observations = yield from FHIR_DB.get_observations_from_duplicate_orders(duplicate_orders, composition, self.conn)

            if duplicate_orders_with_observations is not None and len(duplicate_orders_with_observations) > 0:
                self._generate_duplicate_order_alerts(composition, duplicate_orders_with_observations)

    def _generate_duplicate_order_alerts(self, composition, dup_ords_with_obs):
        customer_id = composition.customer_id
        patient_id = composition.subject.get_pat_id()
        alert_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        duplicate_order_alerts = {"alert_type": "dup_order",
                                  "alert_time": alert_datetime,
                                  "alert_list": []}

        for ord in list(dup_ords_with_obs):
            order_code = ord[0]
            order_code_system = ord[1]
            order_id = dup_ords_with_obs[ord]["order_id"]
            ord_detail = composition.get_encounter_order_detail_by_coding(code=order_code, code_system="clientEMR")

            #Create a storeable text description of the related clinical observations list
            long_description = ""
            for observation in dup_ords_with_obs[ord]['related_observations']:
                ord_detail.relatedItem.append(observation)
                long_description += ("%s: %s %s (%s)" % (observation.name,
                                                         observation.valueQuantity.value,
                                                         observation.valueQuantity.units,
                                                         observation.appliesdateTime))

            FHIR_alert = FHIR_API.Alert(customer_id=customer_id, subject=patient_id, provider_id=composition.get_author_id(), encounter_id=composition.encounter.get_csn(),
                                        code_trigger=order_code, code_trigger_type=order_code_system, alert_datetime=composition.lastModifiedDate,
                                        short_title=("Duplicate Order: %s" % ord_detail.text), short_description="Clinical observations are available for a duplicate order recently placed.", long_description=long_description,
                                        saving=16.14,
                                        related_observations=dup_ords_with_obs[ord]['related_observations'],
                                        category="dup_order")
            duplicate_order_alerts['alert_list'].append(FHIR_alert)


        alerts_section = composition.get_section_by_coding(code_system="maven", code_value="alerts")
        alerts_section.content.append(duplicate_order_alerts)

    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    #####
    ##### EVALUATE ALTERNATIVE MEDICATIONS
    #####
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    @asyncio.coroutine
    def evaluate_alternative_meds(self, composition):
        pass

    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    #####
    ##### EVALUATE CHOOSING WISELY RULES
    #####
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    @asyncio.coroutine
    def evaluate_CDS_rules(self, composition):
        """

        """
        CDS_rules = yield from FHIR_DB.get_matching_CDS_rules(composition, self.conn)

        cds_alerts = []
        if CDS_rules is not None and len(CDS_rules) > 0:
            for rule in CDS_rules:
                rule_result = yield from self._evaluate_CDS_rule_details(composition, rule)
                if rule_result:
                    cds_alert = yield from self.generate_cds_alert(composition, rule)
                    cds_alerts.append(cds_alert)

        if cds_alerts is not None and len(cds_alerts) > 0:
            alerts_section = composition.get_section_by_coding(code_system="maven", code_value="alerts")
            alerts_section.content.append({"alert_type": "cds",
                                           "alert_time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                                           "alert_list": cds_alerts})

    @asyncio.coroutine
    def _evaluate_CDS_rule_details(self, composition, rule):
        additional_dx_details_result = yield from self._evaluate_additional_dx_rule_details(composition, rule.encounter_dx_rules)
        lab_rule_details_result = yield from self._evaluate_lab_rule_details(composition, rule.lab_rules)
        med_rule_details_result = yield from self._evaluate_medication_rule_details(composition, None)

        if additional_dx_details_result and lab_rule_details_result and med_rule_details_result:
            return True
        else:
            return False

    @asyncio.coroutine
    def _evaluate_additional_dx_rule_details(self, composition, dx_rule_details):
        return True

    @asyncio.coroutine
    def _evaluate_lab_rule_details(self, composition, lab_rule_details):
        return True

    @asyncio.coroutine
    def _evaluate_medication_rule_details(self, composition, med_rule_details):
        return True

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
        short_title = rule.name
        long_title = rule.name
        short_description = rule.name
        long_description = rule.name
        override_indications = ['Select one of these override indications boink']
        saving = 807.12
        category = "cds"

        FHIR_alert = FHIR_API.Alert(customer_id=customer_id, subject=pat_id, provider_id=provider_id, encounter_id=encounter_id,
                                    code_trigger=code_trigger, CDS_rule=CDS_rule, alert_datetime=alert_datetime,
                                    short_title=short_title, long_title=long_title, short_description=short_description, long_description=long_description,
                                    override_indications=override_indications, saving=saving, category=category)

        return FHIR_alert

    @asyncio.coroutine
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

    @asyncio.coroutine
    def get_override_indications(self, rule, customer_id):
        override_indications = []
        column_map = ["override_indication.name",
                      "override_indication.description"]

        columns = self.DBMapper.select_rows_from_map(column_map)

        cur = yield from self.conn.execute_single("select " + columns + " from override_indication where sleuth_rule=%s and customer_id=%s", extra=[rule.CDS_rule_id, customer_id])
        for result in cur:
            override_indications.append(result)

        return override_indications


def run_composition_evaluator():

    rabbithandler = 'rabbitmessagehandler'
    MavenConfig = {
        rabbithandler:
        {
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
            SP.CONFIG_READERNAME: rabbithandler+".Reader",
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
            SP.CONFIG_WRITERNAME: [rabbithandler+".Writer", rabbithandler+".Writer2"],
            SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_IDENTITYPARSER,

        },
        rabbithandler+".Reader":
        {
            SP.CONFIG_HOST:'localhost',
            SP.CONFIG_QUEUE:'incoming_cost_evaluator_work_queue',
            SP.CONFIG_EXCHANGE:'maven_exchange',
            SP.CONFIG_KEY:'incomingcosteval'
        },

        rabbithandler+".Writer":
        {
            SP.CONFIG_HOST:'localhost',
            SP.CONFIG_QUEUE:'aggregator_work_queue',
            SP.CONFIG_EXCHANGE:'maven_exchange',
            SP.CONFIG_KEY:'aggregate',
            SP.CONFIG_WRITERKEY:'aggregate',
        },

        rabbithandler+".Writer2":
        {
            SP.CONFIG_HOST:'localhost',
            SP.CONFIG_QUEUE:'logger_work_queue',
            SP.CONFIG_EXCHANGE:'maven_exchange',
            SP.CONFIG_KEY:'logging',
            SP.CONFIG_WRITERKEY:'logging',
        },
        'EvaluatorConnectionPool': {
            AsyncConnectionPool.CONFIG_CONNECTION_STRING: MC.dbconnection,
            AsyncConnectionPool.CONFIG_MIN_CONNECTIONS: 2,
            AsyncConnectionPool.CONFIG_MAX_CONNECTIONS: 4
        },
    }

    MC.MavenConfig = MavenConfig

    loop = asyncio.get_event_loop()
    sp_message_handler = CompositionEvaluator(rabbithandler)
    sp_message_handler.schedule(loop)

    try:
        loop.run_forever()

    except KeyboardInterrupt:
        sp_message_handler.close()
        loop.close()

if __name__ == '__main__':
    run_composition_evaluator()
