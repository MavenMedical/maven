import unittest
import timeit
import asyncio
import maven_config as MC
import utils.api.pyfhir.pyfhir_generated as FHIR_API
import maven_logging as ML
import utils.streaming.stream_processor as SP
import datetime
import utils.web_client.allscripts_http_client as AHC
from clientApp.webservice.composition_builder import CompositionBuilder
import utils.web_client.http_client as http
from utils.enums import CONFIG_PARAMS
import pickle
import unittest

import redis
import fuzzywuzzy
from utils.database.database import AsyncConnectionPool
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from pickle import load, dumps


def async_test(f):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper


class TestRedisTerminologyServer(unittest.TestCase):
    def setUp(self):
        MavenConfig = {
            CONFIG_PARAMS.PERSISTENCE_SVC.value: {
            "database": CONFIG_PARAMS.DATABASE_SVC.value, },
            CONFIG_PARAMS.DATABASE_SVC.value:
            {
                AsyncConnectionPool.CONFIG_CONNECTION_STRING: MC.dbconnection,
                AsyncConnectionPool.CONFIG_MIN_CONNECTIONS: 4,
                AsyncConnectionPool.CONFIG_MAX_CONNECTIONS: 16
            },
        }

        MC.MavenConfig.update(MavenConfig)
        self.loop = asyncio.get_event_loop()
        self.db = AsyncConnectionPool(CONFIG_PARAMS.DATABASE_SVC.value)
        self.db.schedule(self.loop)
        self.REDIS_CACHE = redis.StrictRedis(host='localhost', port=6379, db=0)

    @async_test
    def test_connection(self):
        cur = yield from self.db.execute_single("SELECT * FROM customer;")
        if cur:
            customers = [res[0] for res in cur]
        else:
            return False
        print(customers)

    @async_test
    def test_load_SNOMED_Descriptions_into_redis(self, number=10000000):
        tick = datetime.datetime.now()
        cur = yield from self.db.execute_single("SELECT d.term, d.id FROM terminology.descriptions d LIMIT %s", extra=[number])
        one_thousand_snomeds = [(res[1], res[0]) for res in cur]
        tock = datetime.datetime.now()
        print("Loading {} descriptions from database: {} seconds".format(len(one_thousand_snomeds), (tock - tick).seconds))

    @async_test
    def test_read_SNOMED_Descriptions_into_redis(self, number=10000000):
        #descriptions_list = [bytes.decode(desc) for desc in self.REDIS_CACHE.keys()]
        cur = yield from self.db.execute_single("SELECT d.term, d.id FROM terminology.descriptions d LIMIT %s", extra=[number])
        descriptions_list = [res[0] for res in cur]
        tick = datetime.datetime.now()
        for desc in descriptions_list:
            if fuzz.token_sort_ratio("prostate cancer", desc) > 80:
                print(desc)
        tock = datetime.datetime.now()
        print("Analyzing {} descriptions from REDIS: {} seconds".format(len(descriptions_list), (tock - tick).seconds))

    @async_test
    def test_shutdown(self):
        self.REDIS_CACHE.flushdb()






