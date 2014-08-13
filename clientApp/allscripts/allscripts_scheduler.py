import utils.web_client.allscripts_http_client as AHC
from maven_config import MavenConfig
import asyncio
from enum import Enum
from datetime import date, datetime, timedelta
import re
from dateutil.parser import parse

icd9_match = re.compile('\(V?[0-9]+(?:\.[0-9]+)?\)')

CONFIG_API = 'api'


class Types(Enum):
    StaticTest1 = 1
    StaticTest2 = 2
    Unused1 = 3


class scheduler():

    def __init__(self, configname):
        self.config = MavenConfig[configname]
        self.apiname = self.config[CONFIG_API]
        self.allscripts_api = AHC.allscripts_api(self.apiname)
        self.processed = set()
        self.lastday = None

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
                    print(e)
                # print([(sch['patientID'], sch['ApptTime2'], sch['ProviderID']) for sch in sched])
                for appointment in sched:
                    patient = appointment['patientID']
                    provider = appointment['ProviderID']
                    if (patient, provider, today) not in self.processed:
                        asyncio.Task(self.evaluate(patient, provider, today, first))
            except Exception as e:
                print(e)
            yield from asyncio.sleep(5)
            first = False

    @asyncio.coroutine
    def evaluate(self, patient, provider, today, first):
        try:
            # print('evaluating %s for %s' % (patient, provider))
            now = datetime.now()
            prior = now - timedelta(seconds=1200)
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
                        self.processed.add((patient, provider, today))
                        if not first:
                            start, stop = match.span()
                            print((start, stop))
                            print('firing ' + str((patient, provider, keywords[start:stop])))
                            break
                # processed.update({doc['DocumentID'] for doc in documents})
        except AHC.AllscriptsError as e:
            print(e)
        except:
            import traceback
            traceback.print_exc()

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

    MavenConfig['scheduler'] = {CONFIG_API: 'allscripts_demo'}

    sched = scheduler('scheduler')
    loop = asyncio.get_event_loop()
    print(loop.run_until_complete(sched.get_updated_schedule()))
