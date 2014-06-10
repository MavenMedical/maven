#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:
#
#
#
#
#************************
#ASSUMES:
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE:
#*************************************************************************
import unittest
import asyncio
import maven_config as MC
import utils.streaming.stream_processor as SP
from utils.database.database import AsyncConnectionPool
from emr_parser import VistaParser
import app.backend.evaluators.composition_evaluator as CE


class TestCompositionEvaluator(unittest.TestCase):

    def setUp(self):
        with open("/home/devel/maven/clientApp/module_webservice/test_message_from_ehr") as f:
            r = f.readlines()
            self.composition = VistaParser().create_composition(r[11])
        self.composition_evaluator = CE.CompositionEvaluator(testhandler)
        self.loop = asyncio.get_event_loop()
        self.composition_evaluator.schedule(self.loop)

    def test_cost_evaluator(self):
        @asyncio.coroutine
        def go():
            yield from self.composition_evaluator.evaluate_encounter_cost(composition=self.composition)
        self.loop.run_until_complete(go())

        enc_ord_summary_section = self.composition.get_section_by_coding("maven", "enc_ord_sum")
        self.assertEqual(enc_ord_summary_section.content, [('76370', 'CPT4'), ('2', 'maven'), ('3', 'maven')])

        enc_ord_details_section = self.composition.get_section_by_coding("maven", "enc_cost_details")
        self.assertEqual(enc_ord_details_section.content, [['IMMUNOGLOBULINS', 16.14], ['CEFIXIME TAB ', 519.14], ['CT SINUS COMPLETE W/O CONTRAST', 807.0]])

    def test_duplicate_order(self):
        @asyncio.coroutine
        def go():
            #TODO - the duplicate orders functionality relies on a section that is added during cost evaluation
            #TODO - which we need to decouple (thats why the evaluate_encounter_cost method is run before below)
            yield from self.composition_evaluator.evaluate_encounter_cost(composition=self.composition)
            yield from self.composition_evaluator.evaluate_duplicate_orders(composition=self.composition)
        self.loop.run_until_complete(go())

        ord_detail = self.composition.get_encounter_order_detail_by_coding(code="3", code_system="maven")
        check_observation = (ord_detail.relatedItem[0].name, ord_detail.relatedItem[0].valueQuantity.value, ord_detail.relatedItem[0].valueQuantity.units)
        self.assertEqual(check_observation, ('Hemoglobin A1c', 7.4, '%'))

    def test_alternative_meds(self):
        pass

    def test_rule_engine(self):
        pass

testhandler = 'testmsghandler'
MavenConfig = {
    testhandler:
    {
        SP.CONFIG_READERTYPE: SP.CONFIGVALUE_EXPLICIT,
        SP.CONFIG_READERNAME: testhandler+".Reader",
        SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_EXPLICIT,
        SP.CONFIG_WRITERNAME: [testhandler+".Writer", testhandler+".Writer2"],
        SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_IDENTITYPARSER,

    },
    testhandler+".Reader":
    {
        SP.CONFIG_HOST:'localhost',
        SP.CONFIG_QUEUE:'aggregator_work_queue',
        SP.CONFIG_EXCHANGE:'maven_exchange',
        SP.CONFIG_KEY:'aggregate',
    },

    testhandler+".Writer":
    {
        SP.CONFIG_HOST:'localhost',
        SP.CONFIG_QUEUE:'aggregator_work_queue',
        SP.CONFIG_EXCHANGE:'maven_exchange',
        SP.CONFIG_KEY:'aggregate',
        SP.CONFIG_WRITERKEY:'aggregate',
    },

    testhandler+".Writer2":
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

if __name__ == '__main__':
    TestCompositionEvaluator()