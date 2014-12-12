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
import maven_logging as ML
import utils.streaming.stream_processor as SP
import utils.web_client.allscripts_http_client as AHC
import utils.web_client.http_client as http
from utils.enums import CONFIG_PARAMS

from clientApp.allscripts.allscripts_scheduler import scheduler as ALLSCRIPTS_SCHEDULER


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


class FakeAllscriptsClientInterface():
    def __init__(self):
        pass

    def evaluate_composition(self, composition):
        print(composition)


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


class TestAllscriptsTriggerScheduler(unittest.TestCase):

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
        self.client_app_scheduler = ALLSCRIPTS_SCHEDULER(FakeAllscriptsClientInterface(), self.customer_id, self.ALLSCRIPTS_API, 10, False)
        #self.COMP_BUILDER = CompositionBuilder(self.customer_id, self.ALLSCRIPTS_API)
        #@self.loop.run_until_complete(self.COMP_BUILDER.build_providers())

        #self.RABBIT_MSG = RabbitReaderWriter("rabbit reader writer", self.update_evaled_composition)
        #self.RABBIT_MSG.schedule(self.loop)

    @async_test
    def test_run_scheduler(self):
        self.client_app_scheduler.active_providers = {(3, '10053'): {"provider_id": "10053",
                                                                     "user_name": "MAVEN1"}}
        yield from self.client_app_scheduler.run()

    def tearDown(self):
        pass


