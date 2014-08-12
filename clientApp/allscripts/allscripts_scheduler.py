import utils.web_client.allscripts_http_client as AHC
from maven_config import MavenConfig
import asyncio
from enum import Enum
from utils.web_client.builder import builder
from datetime import date, timedelta

CONFIG_API = 'api'


class Types(Enum):
    StaticTest1 = 1
    StaticTest2 = 2
    Unused1 = 3


class scheduler(builder):

    def __init__(self, configname):
        builder.__init__(self)
        self.config = MavenConfig[configname]
        self.apiname = self.config[CONFIG_API]
        self.allscripts_api = AHC.allscripts_api(self.apiname)
        self.processed = set()
        self.lastday = None

    @asyncio.coroutine
    def get_updated_schedule(self):
        while True:
            try:
                today = date.today() - timedelta(days=1)
                if today != self.lastday:
                    self.lastday = today
                    self.processed = set()
                    sched = []
                try:
                    sched = yield from self.allscripts_api.GetSchedule('CliffHux', today)
                except AHC.AllscriptsError as e:
                    print(e)
                print([(sch['patientID'], sch['ApptTime2'], sch['ProviderID']) for sch in sched])
                for appointment in sched:
                    patient = appointment['patientID']
                    provider = appointment['ProviderID']
                    if (patient, provider) not in self.processed:
                        asyncio.Task(self.evaluate(patient, provider))
            except Exception as e:
                print(e)
            yield from asyncio.sleep(10)

    @asyncio.coroutine
    def evaluate(self, patient, provider):
        print('evaluating %s for %s' % (patient, provider))
        today = date.today()
        prior = today - timedelta(days=2000)
        try:
            documents = yield from self.allscripts_api.GetDocuments('CliffHux', patient,
                                                                    prior, today)
            if documents:
                print(documents)
        except AHC.AllscriptsError as e:
            print(e)
            pass

if __name__ == '__main__':
    MavenConfig['allscripts_old_demo'] = {
        AHC.http.CONFIG_BASEURL: 'http://aws-eehr-11.4.1.unitysandbox.com/Unity/UnityService.svc/json',
        AHC.http.CONFIG_OTHERHEADERS: {
            'Content-Type': 'application/json'
        },
        AHC.CONFIG_APPNAME: 'web20',
        AHC.CONFIG_APPUSERNAME: 'webtwozero',
        AHC.CONFIG_APPPASSWORD: 'www!web20!',
    }

    MavenConfig['allscripts_demo'] = {
        AHC.http.CONFIG_BASEURL: 'http://pro14ga.unitysandbox.com/Unity/UnityService.svc/json',
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
