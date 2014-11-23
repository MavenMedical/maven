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
import utils.api.pyfhir.pyfhir_generated as FHIR_API
import urllib.parse
import maven_logging as ML
import utils.streaming.stream_processor as SP
import datetime
import utils.web_client.allscripts_http_client as AHC
from clientApp.webservice.composition_builder import CompositionBuilder
import utils.web_client.http_client as http
from utils.enums import CONFIG_PARAMS, ALERT_TYPES
from uuid import uuid1 as UUID


ML.get_logger(ML.set_debug())
global customer_id
global sandboxURL
global provider_username
global patient_id


def async_test(f):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper


class RabbitReaderWriter(SP.StreamProcessor):

    def __init__(self, configname, updater_fn):
        SP.StreamProcessor.__init__(self, configname)
        self.master_list = ['', '', '', '', '']
        self.object_manager = []
        self.evaled_composition_updater_fn = updater_fn

    @asyncio.coroutine
    def read_object(self, obj, key2):
        newest_composition = obj
        yield from self.evaled_composition_updater_fn(newest_composition)


def update_globals(customer_id1, provider_username1, patient_id1, sandboxURL1, loop1):
    global customer_id
    customer_id = customer_id1
    global sandboxURL
    sandboxURL = sandboxURL1
    global provider_username
    provider_username = provider_username1
    global patient_id
    patient_id = patient_id1
    global loop
    loop =loop1


class TestCompositionEvaluator(unittest.TestCase):

    def setUp(self):
        global customer_id
        global sandboxURL
        global provider_username
        global patient_id
        self.customer_id = customer_id
        self.provider_username = provider_username
        self.patient_id = patient_id
        self.sandboxURL = sandboxURL

        MavenConfig = {
            CONFIG_PARAMS.EHR_API_BASE_URL.value: self.sandboxURL,
            http.CONFIG_OTHERHEADERS: {
                'Content-Type': 'application/json'
            },
            CONFIG_PARAMS.EHR_API_APPNAME.value: 'MavenPathways.TestApp',
            CONFIG_PARAMS.EHR_API_SVC_USER.value: 'MavenPathways',
            CONFIG_PARAMS.EHR_API_PASSWORD.value: 'MavenPathways123!!',

            "rabbit reader writer":
            {
                SP.CONFIG_READERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
                SP.CONFIG_READERNAME: "rabbit reader writer" + ".Reader",
                SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
                SP.CONFIG_WRITERNAME: "rabbit reader writer" + ".Writer",
                SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_UNPICKLEPARSER,
            },
            "rabbit reader writer" + ".Reader":
            {
                SP.CONFIG_HOST: 'localhost',
                SP.CONFIG_QUEUE: 'aggregator_work_queue',
                SP.CONFIG_EXCHANGE: 'maven_exchange',
                SP.CONFIG_KEY: 'aggregate',
            },

            "rabbit reader writer" + ".Writer":
            {
                SP.CONFIG_HOST: 'localhost',
                SP.CONFIG_QUEUE: 'incoming_cost_evaluator_work_queue',
                SP.CONFIG_EXCHANGE: 'maven_exchange',
                SP.CONFIG_KEY: 'incomingcosteval',
                SP.CONFIG_WRITERKEY: 'CostEval'
            },
        }
        MC.MavenConfig.update(MavenConfig)

        self.loop = loop
        self.ALLSCRIPTS_API = AHC.allscripts_api(MC.MavenConfig)
        self.COMP_BUILDER = CompositionBuilder(self.customer_id, self.ALLSCRIPTS_API)
        self.RABBIT_MSG = RabbitReaderWriter("rabbit reader writer", self.update_evaled_composition)
        self.RABBIT_MSG.schedule(self.loop)
        self.loop.run_until_complete(self.COMP_BUILDER.build_providers())

    @asyncio.coroutine
    def update_evaled_composition(self, composition):
        global evaled_composition
        evaled_composition = composition

    @async_test
    def test_build_composition(self):
        global unevaled_composition
        unevaled_composition = yield from self.COMP_BUILDER.build_composition(self.provider_username, self.patient_id, str(UUID()), datetime.datetime.now(), [])
        self.assertTrue(isinstance(unevaled_composition, FHIR_API.Composition))
        self.assertTrue(len(unevaled_composition.section) == 1)
        self.RABBIT_MSG.write_object(unevaled_composition, writer_key="CostEval")

    @async_test
    def test_check_alerts(self):
        global evaled_composition
        self.assertTrue(isinstance(evaled_composition, FHIR_API.Composition))
        self.assertTrue(len(evaled_composition.section) > 1)
        pathway_alerts = evaled_composition.get_alerts_by_type(type=ALERT_TYPES.PATHWAY)
        yield from self.print_alerts(pathway_alerts)

    @asyncio.coroutine
    def print_alerts(self, pathway_alerts):

        if len(pathway_alerts) == 0:
            print("****NO ALERTS GENERATED!!!****")
            return
        else:
            print("****{} ALERT(s) GENERATED****".format(len(pathway_alerts)))
            for alert in pathway_alerts:
                l = ["====GENERATED ALERT====",
                     "Customer ID: {}".format(evaled_composition.customer_id),
                     "Provider Username: {}".format(evaled_composition.author.get_provider_username()),
                     "Provider ID: {}".format(evaled_composition.author.get_provider_id()),
                     "Patient Name: {}".format(evaled_composition.subject.get_name()),
                     "Patient ID: {}".format(evaled_composition.subject.get_pat_id()),
                     "Encounter ID: {}".format(urllib.parse.quote(evaled_composition.encounter.get_csn())),
                     "--",
                     "Pathway ID: {}".format(alert.CDS_rule),
                     "Encounter Dx: {}".format([coding.code for condition in evaled_composition.get_encounter_conditions() for coding in condition.code.coding if coding.system in ["ICD-9", "ICD9"] and condition.category == "Encounter"]),
                     "Problem List Dx: {}".format([coding.code for condition in evaled_composition.get_encounter_conditions() for coding in condition.code.coding if coding.system in ["ICD-9", "ICD9"] and condition.category == "Problem List"]),
                     "History Dx: {}".format([coding.code for condition in evaled_composition.get_encounter_conditions() for coding in condition.code.coding if coding.system in ["ICD-9", "ICD9"] and condition.category == "History"]),
                     "====END GENERATED ALERT===="]
                print("\n".join(l))

    def tearDown(self):
        self.RABBIT_MSG.close()