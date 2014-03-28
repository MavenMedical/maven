#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:   This python file acts to analyze the cost of orderables that were delivered via message
#               from an EMR.
#
#************************
#ASSUMES:       XML format that is described in the Unit Test for the clientApp api.
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-1
#*************************************************************************

import app.backend.module_rule_engine.base_evaluator as BE
#from xml.etree import ElementTree as ET
#from clientApp.api import cliPatient as PT
import app.utils.streaming.stream_processor as SP
from app.utils.database.database import AsyncConnectionPool,SingleThreadedConnection, MappingUtilites
import maven_config as MC
import asyncio
import json
import pickle
import clientApp.api.api as api
import maven_logging as ML
import datetime


class CostEvaluator(SP.StreamProcessor):

    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)
        self.conn = SingleThreadedConnection('CostEvalConnection')


    @asyncio.coroutine
    def read_object(self, obj, _):
        composition = pickle.loads(obj)
        self.evaluate_orders(composition)
        #ML.PRINT(json.dumps(composition, default=api.jdefault, indent=4))
        self.write_to_db(composition)
        self.write_object(composition, writer_key='aggregate')

    def evaluate_orders(self, composition):
        """

        """

        encounter_cost_breakdown = []
        total_cost = 0.00

        orders = composition.get_encounter_orders()
        for order in orders:
            order.totalCost = 0.00
            order_details = composition.get_proc_supply_details(order)

            for detail in order_details:
                cur = self.conn.execute("select cost_amt from costmap where billing_code='%s'" % detail[0])
                for result in cur:
                    #detail.append(float(result[0]))
                    order.totalCost += float(result[0])
                    encounter_cost_breakdown.append([detail[1], float(result[0])])

            total_cost += order.totalCost

        #encounter_cost_breakdown.append(["n/a", "Total Cost", total_cost])
        composition.section.append(api.Section(title="Encounter Cost Breakdown", content=encounter_cost_breakdown))

    def write_to_db(self, composition):

        try:
            pat_id = composition.subject.get_pat_id()
            customer_id = composition.customer_id
            birth_month = composition.subject.get_birth_month()
            birth_date = composition.subject.birthDate
            sex = composition.subject.gender
            mrn = composition.subject.get_mrn()
            patname = composition.subject.get_name()
            cur_pcp_prov_id = composition.subject.get_current_pcp()


            cur = self.conn.execute("SELECT upsert_patient('%s', %s, '%s', '%s', '%s', '%s', '%s')" %
                                   (pat_id, customer_id, birth_month, sex, mrn, patname, cur_pcp_prov_id))
        except:
            raise Exception("Error inserting patient data into database")

        try:
            encID = composition.encounter.get_csn()

            cur = self.conn.execute("SELECT upsert_encounter('%s', '%s', 'Emergency', '2014-03-24', '129850393', '32209837', 1235234, '2014-03-24T08:45:23', NULL, '%s')" % (encID, pat_id, customer_id))
            cur.close()

        except:
            raise Exception("Error parsing encounter data into database")

        try:
            json_composition = json.dumps(composition, default=api.jdefault)
            cur = self.conn.execute("INSERT INTO composition (patient_id, encounter_id, customer_id, comp_body) VALUES ('%s', '%s', %s, ('%s'))" % (pat_id, encID, customer_id, json_composition))
            cur.close()

        except:
            raise Exception("Error storing JSON composition")

        try:
            problem_list = composition.get_encounter_problem_list()
            for problem in problem_list:
                dx_ID = problem.get_problem_ID().value
                cur = self.conn.execute("SELECT upsert_encounterdx('%s', '%s', '%s', NULL, NULL, NULL, %s)" % (pat_id, encID, dx_ID, customer_id))

        except:
            raise Exception("Error parsing encounter problem list")

        try:
            now = datetime.datetime.now()
            orders = composition.get_encounter_orders()
            for order in orders:
                cur = self.conn.execute("INSERT INTO mavenorder(pat_id, customer_id, encounter_id, order_name, order_type, proc_code, code_type, order_cost, datetime) VALUES('%s', %s,'%s','%s','%s', '%s', '%s', %s, '%s')" % (pat_id, composition.customer_id, encID, order.detail[0].name, order.detail[0].type, order.detail[0].identifier[0].value, "maven", float(order.totalCost), now))

        except:
            raise Exception("Error parsing encounter orders")




def run_cost_evaluator():

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
        'CostEvalConnection': {
            SingleThreadedConnection.CONFIG_CONNECTION_STRING:
            ("dbname=%s user=%s password=%s host=%s port=%s" % ('maven', 'maven', 'temporary', 'localhost', '5432')),
            #AsyncConnectionPool.CONFIG_MIN_CONNECTIONS: 2,
            #AsyncConnectionPool.CONFIG_MAX_CONNECTIONS: 4
        },
    }

    MC.MavenConfig = MavenConfig

    loop = asyncio.get_event_loop()
    sp_message_handler = CostEvaluator(rabbithandler)
    sp_message_handler.schedule(loop)

    try:
        loop.run_forever()

    except KeyboardInterrupt:
        sp_message_handler.close()
        loop.close()

if __name__ == '__main__':
    run_cost_evaluator()