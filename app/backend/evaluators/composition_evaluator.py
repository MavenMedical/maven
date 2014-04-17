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
#LAST MODIFIED FOR JIRA ISSUE: MAV-96
#*************************************************************************
import pickle

import asyncio
from utils.database.database import AsyncConnectionPool, MappingUtilites
import utils.streaming.stream_processor as SP
import maven_config as MC
import maven_logging as ML
import decimal


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
        composition = pickle.loads(obj)
        rules = yield from self.get_matching_sleuth_rules(composition)
        yield from self.evaluate_sleuth_rules(composition, rules)

    @asyncio.coroutine
    def get_matching_sleuth_rules(self, composition):
        orders = composition.get_encounter_orders()
        customer_id = composition.customer_id
        applicable_sleuth_rules = []

        for order in orders:
            order_details = composition.get_proc_supply_details(order)

            for detail in order_details:
                column_map = ["sleuth_rule.rule_details"]
                columns = self.DBMapper.select_rows_from_map(column_map)
                cur = yield from self.conn.execute_single("select %s from sleuth_rule where cpt_trigger='%s' and customer_id=%s" % (columns, detail[0], customer_id))
                for result in cur:
                    applicable_sleuth_rules.append(result)
        return applicable_sleuth_rules

    @asyncio.coroutine
    def evaluate_sleuth_rules(self, composition, rules):
        """
        Evaluates, one by one, each of the rules that was found to be applicable from the method get_matching_sleuth_rules()

        :param composition: The FHIR composition object that is to be evaluated
        :param rules: The list of rules returned by the get_matching_sleuth_rules() method
        """
        encounter_dx_codes = composition.get_encounter_dx_codes()
        encounter_snomedIDs = yield from self.get_snomedIDs(encounter_dx_codes)

        for rule in rules:
            rule_details = rule[0]['details']
            encounter_dx_rules = yield from self.get_encounter_dx_rules(rule_details)
            results = yield from self.evaluate_encounter_dx(encounter_snomedIDs, encounter_dx_rules)
            ML.PRINT(results)

    @asyncio.coroutine
    def evaluate_encounter_dx(self, encounter_snomedIDs, dx_rules):
        dx_rules_results = []
        for dx_rule in dx_rules:
            dx_rule_eval = False

            if dx_rule['exists'] == True:
                for enc_dx in encounter_snomedIDs:
                    dx_pass = False
                    cur = yield from self.conn.execute_single("select issnomedchild(%s,%s)" % (dx_rule['snomed'], enc_dx))
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

    @asyncio.coroutine
    def get_snomedIDs(self, encounter_dx_codes):
        """
        Looks up the snomed concept IDs for each of the ICD-9 codes in encounter_dx_codes

        :param encounter_dx_codes: A list of ICD-9 codes extracted from the FHIR composition's Problem List section
        """
        encounter_dx_snomeds = []

        for enc_dx in encounter_dx_codes:
            column_map = ["snomedid"]
            columns = self.DBMapper.select_rows_from_map(column_map)
            cur = yield from self.conn.execute_single("select %s from terminology.codemap where code='%s'" % (columns, enc_dx))
            for result in cur:
                encounter_dx_snomeds.append(int(result[0]))
            cur.close()
        return encounter_dx_snomeds


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
            AsyncConnectionPool.CONFIG_CONNECTION_STRING:
            ("dbname=%s user=%s password=%s host=%s port=%s" % ('maven', 'maven', 'temporary', 'localhost', '5432')),
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