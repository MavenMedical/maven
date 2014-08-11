import utils.web_client.allscripts_http_client as AHC
from maven_config import MavenConfig
import asyncio
from enum import Enum
from collections import defaultdict
from utils.web_client.builder import builder

CONFIG_API = 'api'


class Types(Enum):
    StaticTest1 = 1
    StaticTest2 = 2
    Unused1 = 3

build = builder()


class scheduler():

    def __init__(self, configname):
        self.config = MavenConfig[configname]
        apiname = self.config[CONFIG_API]
        self.allscripts_api = AHC.allscripts_api(apiname)

    @build.build(lambda: {})
    def build_composition(self, obj, username, patient):
        return obj

    @build.provide(Types.StaticTest1)
    def _StaticTest1(self, username, patient):
        ret = yield from self.allscripts_api.GetPatient(username, patient)
        return ret

    @build.provide(Types.StaticTest2)
    def _StaticTest2(self, username, patient):
        return {patient: username}

    @build.provide(Types.Unused1)
    def _Unused1(self, username, patient):
        print('running unused dependency')
        return {patient: username}

    @build.require(Types.StaticTest1, Types.StaticTest2)
    def _build_sample(self, obj, demographics, procedures):
        obj['demographics'] = demographics
        obj['procedures'] = procedures


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
    print(loop.run_until_complete(sched.build_composition("terry", "-22")))
