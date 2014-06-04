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
from utils.database.database import AsyncConnectionPool, MappingUtilites
import utils.database.fhir_database as FHIR_DB
import utils.api.pyfhir.pyfhir_generated as FHIR_API
import utils.streaming.stream_processor as SP
import maven_config as MC
import datetime
from collections import defaultdict


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
        yield from self.evaluate_encounter_cost(composition)
        yield from self.evaluate_duplicate_orders(composition)

        #TODO Logic to check if recently alerted (will involved look-up in DB.This type of caching would be nice via REDIS)

        rules = yield from self.get_matching_sleuth_rules(composition)
        yield from self.evaluate_sleuth_rules(composition, rules)
        yield from FHIR_DB.write_composition_to_db(composition, self.conn)
        self.write_object(composition, writer_key='aggregate')

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
        Takes a FHIR Composition object, iterates through the Orders found in the "Encounter Orders"
        Composition.section object, checks the costmap table for the cost-look-up, and then adds a
        NEW section to Composition.section labeled "Encounter Cost Breakdown," which is a list of
        {"order name": 807.13} tuples with order name and the price.

        :param composition: FHIR Composition object created using Maven's FHIR API
        """

        orders = composition.get_encounter_orders()
        encounter_orders_code_summary = []

        # This block is the original code Yuki wrote.  It makes potentially many calls to the database.
        # I (Tom) re-wrote this to make a single sql query, but be functionally equivalent.  
        # Yuki's code is easier to follow, so I'm leaving it here
        #orders = composition.get_encounter_orders()
        #for order in orders:
        #    order.totalCost = 0.00
        #    order_details = composition.get_proc_supply_details(order)
        #
        #    for detail in order_details:
        #        cur = yield from self.conn.execute_single("select cost_amt from costmap where billing_code=%s", extra=[detail[0]])
        #        for result in cur:
        #            order.totalCost += float(result[0])
        #            encounter_cost_breakdown.append([detail[1], float(result[0])])
        #        cur.close()

        # build the query and maps
        ordersdict = defaultdict(lambda: [])
        detailsdict = defaultdict(lambda: [])

        for order in orders:
            order.totalCost = 0.00
            order_details = composition.get_proc_supply_details(order)
            for detail in order_details:
                encounter_orders_code_summary.append((detail[0], detail[1]))
                ordersdict[detail[0]].append(order)
                detailsdict[detail[0]].append(detail)

        encounter_cost_breakdown = yield from FHIR_DB.gather_encounter_order_cost_info(ordersdict, detailsdict, self.conn)

        composition.section.append(FHIR_API.Section(title="Encounter Orders Code Summary", content=encounter_orders_code_summary,
                                                    code=FHIR_API.CodeableConcept(coding=[FHIR_API.Coding(code="enc_ord_sum", system="maven")])))

        composition.section.append(FHIR_API.Section(title="Encounter Cost Breakdown", content=encounter_cost_breakdown))

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
        #Check to see if there are exact duplicate orders from within the last year
        enc_ord_summary_section = composition.get_section_by_coding("maven", "enc_ord_sum")
        duplicate_orders = yield from FHIR_DB.gather_duplicate_orders(enc_ord_summary_section, composition, self.conn)

        #Check to see if there are relevant lab components to be displayed
        yield from FHIR_DB.gather_observations_from_duplicate_orders(duplicate_orders, composition, self.conn)

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
        raise NotImplementedError


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
    def get_matching_sleuth_rules(self, composition):
        """
        This method returns a list of matching rules, and each returned rule is an array with the columns described below.
        It selects from the sleuth_rule table using the CPT code and Customer_ID

         :param composition: The FHIR composition that needs to contain a FHIR Section containing the Encounter Orders
        """
        orders = composition.get_encounter_orders()
        customer_id = composition.customer_id
        applicable_sleuth_rules = []

        for order in orders:
            order_details = composition.get_proc_supply_details(order)

            for detail in order_details:
                column_map = ["sleuth_rule.rule_details",
                              "sleuth_rule.rule_id",
                              "sleuth_rule.code_trigger",
                              "sleuth_rule.code_trigger_type",
                              "sleuth_rule.name",
                              "sleuth_rule.description",
                              "sleuth_rule.tag_line"]
                columns = self.DBMapper.select_rows_from_map(column_map)

                cur = yield from self.conn.execute_single("select " + columns + " from sleuth_rule where code_trigger=%s and customer_id=%s", extra=[detail[0], customer_id])

                for result in cur:
                    FHIR_rule = FHIR_API.Rule(rule_details=result[0],
                                              rule_id=result[1],
                                              code_trigger=result[2],
                                              code_trigger_type=result[3],
                                              name=result[4],
                                              description=result[5],
                                              tag_line=result[6])

                    applicable_sleuth_rules.append(FHIR_rule)
        return applicable_sleuth_rules

    @asyncio.coroutine
    def evaluate_sleuth_rules(self, composition, rules):
        """
        PAY ATTENTION RULE ENGINE(TECHNO)LOGIC BELOW
        Evaluates, one by one, each of the rules that was found to be applicable from the method get_matching_sleuth_rules()

        :param composition: The FHIR composition object that is to be evaluated
        :param rules: The list of rules (each rule a tuple returned from the DB) returned by the get_matching_sleuth_rules() method
        """
        #We use customer_id A LOT, as it's pretty much needed for every DB call
        customer_id = composition.customer_id

        #empty list to store any potential Alerts that get triggered
        alert_bundle = []

        #Use the FHIR Database API to look up each Condition's codes (ICD-9) and add Snomed CT concepts to the Condition
        yield from FHIR_DB.gather_related_snomeds(composition, self.conn)

        #Pull a list of all the SNOMED CT codes from all of the conditions in the composition
        encounter_snomedIDs = composition.get_encounter_dx_snomeds()

        for rule in rules:
            #retrieve and evaluate the encounter_dx related rules from the rule FHIR object
            encounter_dx_rules = rule.encounter_dx_rules
            enc_dx_results = yield from self.evaluate_encounter_dx(encounter_snomedIDs, encounter_dx_rules)

            #retrieve and evaluate the lab related rules from the rule FHIR objec
            lab_rules = rule.lab_rules
            lab_results = yield from self.evaluate_encounter_labs()

            #evaluate the med rules
            med_results = yield from self.evaluate_encounter_meds()

            #If the encounter, lab, med rules, evaluate to true, gather evidence and override indications and create the alert
            if enc_dx_results and lab_results and med_results:
                evidence = yield from self.gather_evidence(rule, customer_id)
                override_indications = yield from self.get_override_indications(rule, customer_id)
                alert = yield from self.generate_alert(composition, rule, evidence, alert_bundle, override_indications=override_indications)
                alert_bundle.append(alert)

        #If the alert_bundle has anything in it, append it, as a "bundle o' alerts", to the composition's "Maven Alerts" FHIR Section
        if alert_bundle is not None and len(alert_bundle) > 0:
            composition_alerts_section = composition.get_alerts_section()
            alert_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            composition_alerts_section.content.append({alert_datetime: alert_bundle})
            yield from FHIR_DB.write_composition_alerts(alert_datetime, alert_bundle, self.conn)

        else:
            return


    @asyncio.coroutine
    def evaluate_encounter_dx(self, encounter_snomedIDs, dx_rules):
        dx_rules_results = []
        for dx_rule in dx_rules:
            dx_rule_eval = False

            if dx_rule['exists'] == True:
                for enc_dx in encounter_snomedIDs:
                    dx_pass = False
                    cur = yield from self.conn.execute_single("select issnomedchild(%s,%s)", extra=[dx_rule['snomed'], enc_dx])
                    dx_pass = cur.fetchone()[0]
                    if dx_pass == True:
                        dx_rule_eval = True
                        break

            elif dx_rule['exists'] == False:
                for enc_dx in encounter_snomedIDs:
                    if enc_dx == dx_rule['snomed']:
                        dx_rule_eval = False
                        break
                    else:
                        dx_rule_eval = True

            dx_rules_results.append(dx_rule_eval)

        if False in dx_rules_results:
            return False
        else:
            return True

    @asyncio.coroutine
    def evaluate_encounter_labs(self):
        return True

    @asyncio.coroutine
    def evaluate_encounter_meds(self):
        return True

    @asyncio.coroutine
    def gather_evidence(self, rule, customer_id):
        evidence = []
        column_map = ["sleuth_evidence.name",
                      "sleuth_evidence.description",
                      "sleuth_evidence.source",
                      "sleuth_evidence.source_url"]
        columns = self.DBMapper.select_rows_from_map(column_map)
        cur = yield from self.conn.execute_single("select " + columns + " from sleuth_evidence where sleuth_rule=%s and customer_id=%s", extra=[rule.sleuth_rule_id, customer_id])
        for result in cur:
            evidence.append(result)

        return evidence

    @asyncio.coroutine
    def get_override_indications(self, rule, customer_id):
        override_indications = []
        column_map = ["override_indication.name",
                      "override_indication.description"]

        columns = self.DBMapper.select_rows_from_map(column_map)

        cur = yield from self.conn.execute_single("select " + columns + " from override_indication where sleuth_rule=%s and customer_id=%s", extra=[rule.sleuth_rule_id, customer_id])
        for result in cur:
            override_indications.append(result)

        return override_indications


    @asyncio.coroutine
    def generate_alert(self, composition, rule, evidence, alert_group, override_indications=None):
        """
        Generates an alert from the rule that evaluated to true, along with the evidence that supports that rule (from a clinical perspective)

        :param composition: The composition that is being analyzed. This method attaches a new FHIR SECTION to the composition
        :param rule: The sleuth_rule that evaluated to truec
        :param evidence: A LIST of evidence that supports the rule.
        """

        customer_id = composition.customer_id
        pat_id = composition.subject.get_pat_id()
        provider_id = composition.encounter.get_prov_id()
        encounter_id = composition.encounter.get_csn()
        code_trigger = rule.code_trigger
        sleuth_rule = rule.sleuth_rule_id
        alert_datetime = datetime.datetime.now()
        short_title = rule.name
        tag_line = rule.tag_line
        description = rule.description
        override_indications = ['Select one of these override indications boink']
        saving = 807.12

        FHIR_alert = FHIR_API.Alert(customer_id=customer_id, subject=pat_id, provider_id=provider_id, encounter_id=encounter_id,
                                    code_trigger=code_trigger, sleuth_rule=sleuth_rule, alert_datetime=alert_datetime,
                                    short_title=short_title, tag_line=tag_line, description=description,
                                    override_indications=override_indications, saving=saving)

        return FHIR_alert

    @asyncio.coroutine
    def get_encounter_dx_rules(self, rule_details):
        """
        Extracts the encounter_dx-related rules from the whole set of rule_details

        :param rule_details: The JSON-formatted rule details associated with each top-level rule
        """
        dx_rules = []
        for rule_detail in rule_details:
            if rule_detail['type'] == "encounter_dx":
                dx_rules.append(rule_detail)
        return dx_rules

    def evaluator_response(self, obj, response):
        raise NotImplementedError


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
