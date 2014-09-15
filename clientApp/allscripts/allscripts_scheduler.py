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
import utils.web_client.allscripts_http_client as AHC
import clientApp.webservice.notification_service as NS
import maven_config as MC
import pickle
from clientApp.webservice.composition_builder import CompositionBuilder
from utils.streaming import stream_processor as SP
import maven_logging as ML
from utils.enums import USER_STATE, NOTIFICATION_STATE

icd9_match = re.compile('\(V?[0-9]+(?:\.[0-9]+)?\)')
CONFIG_API = 'api'
CLIENT_SERVER_LOG = ML.get_logger('clientApp.webservice.allscripts_server')
CONFIG_SLEEPINTERVAL = 'sleep interval'
CONFIG_STREAMPROCESSOR = 'stream processor config'
CONFIG_COMPOSITIONBUILDER = 'composition builder config'
CONFIG_CLIENTEHR = 'client ehr'


class Types(Enum):
    StaticTest1 = 1
    StaticTest2 = 2
    Unused1 = 3


class scheduler(SP.StreamProcessor):

    def __init__(self, configname):
        self.config = MC.MavenConfig[configname]
        SP.StreamProcessor.__init__(self, self.config.get(CONFIG_STREAMPROCESSOR))
        self.allscripts_api = AHC.allscripts_api(self.config.get(CONFIG_API))
        self.processed = set()
        self.lastday = None
        self.comp_builder = CompositionBuilder(self.config.get(CONFIG_COMPOSITIONBUILDER))
        self.wk = 2
        self.sleep_interval = self.config.get(CONFIG_SLEEPINTERVAL, 60)
        self.active_providers = {}

    def update_active_providers(self, active_provider_list):
        self.active_providers = active_provider_list

    @asyncio.coroutine
    def get_updated_schedule(self):
        first = True
        yield from self.comp_builder.build_providers()
        while True:
            try:
                today = date.today()
                if today != self.lastday:
                    self.lastday = today
                    self.processed = set()
                    sched = []
                try:
                    for provider in self.active_providers:
                        if self.check_notification_policy(provider):
                            sched = yield from self.allscripts_api.GetSchedule(self.active_providers.get(provider)['user_name'], today)

                except AHC.AllscriptsError as e:
                    CLIENT_SERVER_LOG.exception(e)
                # print([(sch['patientID'], sch['ApptTime2'], sch['ProviderID']) for sch in sched])
                tasks = set()
                # CLIENT_SERVER_LOG.debug(sched)
                for appointment in sched:
                    patient = appointment['patientID']
                    provider = appointment['ProviderID']
                    tasks.add((patient, provider, today, first))
                for task in tasks:
                    asyncio.Task(self.evaluate(*task))
            except Exception as e:
                CLIENT_SERVER_LOG.exception(e)
            yield from asyncio.sleep(self.sleep_interval)
            first = False

    @asyncio.coroutine
    def evaluate(self, patient, provider, today, first):
        CLIENT_SERVER_LOG.debug('evaluating %s/%s' % (patient, provider))
        try:
            # print('evaluating %\s for %s' % (patient, provider))
            now = datetime.now()
            prior = now - timedelta(seconds=12000)
        except:
            import traceback
            traceback.print_exc()
        try:
            documents = yield from self.allscripts_api.GetDocuments('CliffHux', patient,
                                                                    prior, now)
            # print('got %d documents' % len(documents))
            # ML.DEBUG('documents: %d' % len(documents))
            if documents:
                # print('\n'.join([str((doc['DocumentID'], doc['SortDate'], doc['keywords'])) for doc in documents]))
                for doc in documents:
                    keywords = doc.get('keywords', '')
                    match = icd9_match.search(keywords)
                    docid = doc.get('DocumentID')
                    doctime = doc.get('SortDate', None)
                    todaydoc = doctime and datetime.date(parse(doctime)) == today
                    newdoc = True
                    if match and newdoc and todaydoc and (patient, provider, today, docid) not in self.processed:
                        ML.DEBUG('got doc, (match, newdoc, docid, first) = %s' % str((match, newdoc, docid, first)))
                        self.processed.add((patient, provider, today, docid))
                        if not first:
                            # start, stop = match.span()
                            CLIENT_SERVER_LOG.debug("About to send to Composition Builder...")
                            composition = yield from self.comp_builder.build_composition("CLIFFHUX", patient, docid)
                            CLIENT_SERVER_LOG.debug(("Built composition, about to send to Backend Data Router. Composition ID = %s" % composition.id))
                            self.write_object(pickle.dumps([composition, "CLIFFHUX"]), self.wk)
                            break
                # processed.update({doc['DocumentID'] for doc in documents})
        except AHC.AllscriptsError as e:
            CLIENT_SERVER_LOG.exception(e)
        except:
            CLIENT_SERVER_LOG.exception(e)

    def check_notification_policy(self, key):
        provider = self.active_providers.get(key)

        if provider.get('state') == USER_STATE.ACTIVE.value and provider.get('ehr_state') == USER_STATE.ACTIVE.value and provider.get('notification_state', None) is not None:
            return True
        elif provider.get('state') == USER_STATE.ACTIVE.value and provider.get('ehr_state') == USER_STATE.ACTIVE.value and provider.get('notification_state', None) == NOTIFICATION_STATE.MOBILE:
            return True
        else:
            return False


if __name__ == '__main__':
    MC.MavenConfig['allscripts_old_demo'] = {
        AHC.http.CONFIG_BASEURL: 'http://aws-eehr-11.4.1.unitysandbox.com/Unity/UnityService.svc',
        AHC.http.CONFIG_OTHERHEADERS: {
            'Content-Type': 'application/json'
        },
        AHC.CONFIG_APPNAME: 'web20',
        AHC.CONFIG_APPUSERNAME: 'webtwozero',
        AHC.CONFIG_APPPASSWORD: 'www!web20!',
    }

    MC.MavenConfig['allscripts_demo'] = {
        AHC.http.CONFIG_BASEURL: 'http://pro14ga.unitysandbox.com/Unity/UnityService.svc',
        AHC.http.CONFIG_OTHERHEADERS: {
            'Content-Type': 'application/json'
        },
        AHC.CONFIG_APPNAME: 'MavenPathways.TestApp',
        AHC.CONFIG_APPUSERNAME: 'MavenPathways',
        AHC.CONFIG_APPPASSWORD: 'MavenPathways123!!',
    }

    MC.MavenConfig['notificationserver'] = {
        NS.SP.CONFIG_HOST: 'localhost',
        NS.SP.CONFIG_PORT: 8092,
        NS.SP.CONFIG_PARSERTIMEOUT: 120,
        NS.CONFIG_QUEUEDELAY: 30,
    }

    MC.MavenConfig['scheduler'] = {CONFIG_API: 'allscripts_demo'}

    ns = NS.NotificationService('notificationserver')

    sched = scheduler('scheduler')

    loop = asyncio.get_event_loop()
    ns.schedule(loop)
    print(loop.run_until_complete(sched.get_updated_schedule()))
