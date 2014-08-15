# *************************************************************************
# Copyright (c) 2014 - Maven Medical
# ************************
# AUTHOR:
__author__ = 'Tom DuBois'
# ************************
# DESCRIPTION:
#
#
#
#
# ************************
# ASSUMES:
# ************************
# SIDE EFFECTS:
# ************************
# LAST MODIFIED FOR JIRA ISSUE: MAV-289
# *************************************************************************
import asyncio
from enum import Enum
from datetime import date, datetime, timedelta
import re
from dateutil.parser import parse
from collections import defaultdict
import utils.web_client.allscripts_http_client as AHC
import clientApp.module_webservice.notification_service as NS
from maven_config import MavenConfig
import pickle
from clientApp.module_webservice.composition_builder import CompositionBuilder
from utils.streaming import stream_processor as SP
import maven_logging as ML

icd9_match = re.compile('\(V?[0-9]+(?:\.[0-9]+)?\)')

CONFIG_API = 'api'

ML.get_logger()


class Types(Enum):
    StaticTest1 = 1
    StaticTest2 = 2
    Unused1 = 3


class scheduler(SP.StreamProcessor):

    def __init__(self, configname, messenger):
        SP.StreamProcessor.__init__(self, MavenConfig[configname]['SP'])
        self.config = MavenConfig[configname]
        self.apiname = self.config[CONFIG_API]
        self.allscripts_api = AHC.allscripts_api(self.apiname)
        self.processed = set()
        self.lastday = None
        self.messenger = messenger
        self.comp_builder = CompositionBuilder(configname)
        self.wk = 2

    @asyncio.coroutine
    def get_updated_schedule(self):
        first = True
        while True:
            try:
                today = date.today()
                if today != self.lastday:
                    self.lastday = today
                    self.processed = set()
                    sched = []
                try:
                    sched = yield from self.allscripts_api.GetSchedule('CliffHux', today)
                except AHC.AllscriptsError as e:
                    ML.EXCEPTION(e)
                # print([(sch['patientID'], sch['ApptTime2'], sch['ProviderID']) for sch in sched])
                tasks = set()
                for appointment in sched:
                    patient = appointment['patientID']
                    provider = appointment['ProviderID']
                    if (patient, provider, today) not in self.processed:
                        tasks.add((patient, provider, today, first))
                for task in tasks:
                    asyncio.Task(self.evaluate(*task))
            except Exception as e:
                ML.EXCEPTION(e)
            yield from asyncio.sleep(30)
            first = False

    @asyncio.coroutine
    def evaluate(self, patient, provider, today, first):
        try:
            # print('evaluating %s for %s' % (patient, provider))
            now = datetime.now()
            prior = now - timedelta(seconds=12000)
        except:
            import traceback
            traceback.print_exc()
        try:
            documents = yield from self.allscripts_api.GetDocuments('CliffHux', patient,
                                                                    prior, now)
            # print('got %d documents' % len(documents))
            if documents:
                # print('\n'.join([str((doc['DocumentID'], doc['SortDate'], doc['keywords'])) for doc in documents]))
                for doc in documents:
                    keywords = doc.get('keywords', '')
                    match = icd9_match.search(keywords)
                    doctime = doc.get('SortDate', None)
                    newdoc = doctime and parse(doctime) >= prior

                    if match and newdoc:
                        # self.processed.add((patient, provider, today))
                        if not first:
                            start, stop = match.span()
                            composition = yield from self.comp_builder.build_composition("CLIFFHUX", patient)
                            self.write_object(pickle.dumps([composition, "CLIFFHUX"]), self.wk)
                            self.messenger(patient, provider, keywords[start:stop])
                            break
                # processed.update({doc['DocumentID'] for doc in documents})
        except AHC.AllscriptsError as e:
            ML.EXCEPTION(e)
        except:
            ML.EXCEPTION(e)

if __name__ == '__main__':
    MavenConfig['allscripts_old_demo'] = {
        AHC.http.CONFIG_BASEURL: 'http://aws-eehr-11.4.1.unitysandbox.com/Unity/UnityService.svc',
        AHC.http.CONFIG_OTHERHEADERS: {
            'Content-Type': 'application/json'
        },
        AHC.CONFIG_APPNAME: 'web20',
        AHC.CONFIG_APPUSERNAME: 'webtwozero',
        AHC.CONFIG_APPPASSWORD: 'www!web20!',
    }

    MavenConfig['allscripts_demo'] = {
        AHC.http.CONFIG_BASEURL: 'http://pro14ga.unitysandbox.com/Unity/UnityService.svc',
        AHC.http.CONFIG_OTHERHEADERS: {
            'Content-Type': 'application/json'
        },
        AHC.CONFIG_APPNAME: 'MavenPathways.TestApp',
        AHC.CONFIG_APPUSERNAME: 'MavenPathways',
        AHC.CONFIG_APPPASSWORD: 'MavenPathways123!!',
    }

    MavenConfig['notificationserver'] = {
        NS.SP.CONFIG_HOST: 'localhost',
        NS.SP.CONFIG_PORT: 8092,
        NS.SP.CONFIG_PARSERTIMEOUT: 120,
        NS.CONFIG_QUEUEDELAY: 30,
    }

    MavenConfig['scheduler'] = {CONFIG_API: 'allscripts_demo'}

    ns = NS.NotificationService('notificationserver')

    def translate(patient, provider, icd9):
        ML.DEBUG(provider)
        ns.send_messages(provider,
                         ["patient %s is set with icd9 %s" % (patient, icd9)])
    sched = scheduler('scheduler', translate)

    loop = asyncio.get_event_loop()
    ns.schedule(loop)
    print(loop.run_until_complete(sched.get_updated_schedule()))
