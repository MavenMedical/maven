# *************************************************************************
# Copyright (c) 2014 - Maven Medical
# ************************
# AUTHOR:
__author__ = 'Yuki Uchino'
# ************************
# DESCRIPTION:   This user_sync_service.py contains the code required to manage user deactivations coming
#                coming from Allscripts, as well as updating the notification_service.py of users activated/deactivated
#                from Maven.
#
#
# ************************
# ASSUMES:
# ************************
# SIDE EFFECTS:
# ************************
# LAST MODIFIED FOR JIRA ISSUE: MAV-303
# *************************************************************************
import ast
import utils.web_client.http_client as http
import asyncio
from collections import Counter
import maven_config as MC
import maven_logging as ML
import utils.web_client.allscripts_http_client as AHC

CONFIG_USERSYNCSERVICE = 'sync user service'
CONFIG_SYNCDELAY = 'sync delay'
CONFIG_API = 'api'
logger = ML.get_logger()
ML.set_debug()


class UserSyncService(http.http_api):
    def __init__(self, configname, loop=None):
        self.config = MC.MavenConfig[configname]
        self.customer_id = self.config['customer_id']
        self.sync_delay = self.config.get(CONFIG_SYNCDELAY, 60 * 60)
        self.api_name = self.config[CONFIG_API]
        self.ehr_api = AHC.allscripts_api(self.api_name)
        super(UserSyncService, self).__init__(CONFIG_USERSYNCSERVICE)
        self.postprocess = (lambda x: list(x[0].values())[0])
        self.loop = loop or asyncio.get_event_loop()
        self.ehr_providers = []
        self.maven_providers = []
        self.active_providers = []

    @ML.coroutine_trace(logger.debug)
    def synchronize_users(self):
        while True:
            yield from self.evaluate_users()
            yield from asyncio.sleep(self.sync_delay)

    @ML.coroutine_trace(logger.debug)
    def evaluate_users(self):
        try:
            try:
                ehr_providers = yield from self.ehr_api.GetProviders(username=MC.MavenConfig[self.api_name][AHC.CONFIG_APPUSERNAME])

                for provider in ehr_providers:
                    fhir_provider = self.ehr_api.build_partial_practitioner(provider)
                    self.ehr_providers.append(fhir_provider)
            except AHC.AllscriptsError as e:
                logger.exception(e)

            try:
                ret = yield from self.get('/syncusers', rawdata=False, params={"roles[]": "maventask",
                                                                               "customer_id": self.customer_id})
                self.maven_providers = ast.literal_eval(ret)

                for prov in self.maven_providers:
                    if prov['state'] == "active":
                        prov['active'] = True
                    else:
                        prov['active'] = False
            except Exception as e:
                logger.exception(e)

            self.diff_users()

        except Exception as e:
                logger.exception(e)

    def diff_users(self):
        # create 2 new lists of tuples containing (provider_id, active state)
        ehr_prov_list = Counter([(prov.get_provider_id(), prov.ehr_active) for prov in self.ehr_providers])
        maven_prov_list = Counter([(prov['prov_id'], prov['active']) for prov in self.maven_providers])

        print(list((ehr_prov_list - maven_prov_list).elements()))
        print(list((maven_prov_list - ehr_prov_list).elements()))

    @ML.coroutine_trace(logger.debug)
    def update_maven_users(self):
        raise NotImplementedError


def run():
    import asyncio

    MC.MavenConfig['allscripts_demo'] = {
        AHC.http.CONFIG_BASEURL: 'http://pro14ga.unitysandbox.com/Unity/UnityService.svc',
        AHC.http.CONFIG_OTHERHEADERS: {
            'Content-Type': 'application/json'
        },
        AHC.CONFIG_APPNAME: 'MavenPathways.TestApp',
        AHC.CONFIG_APPUSERNAME: 'MavenPathways',
        AHC.CONFIG_APPPASSWORD: 'MavenPathways123!!',
    }
    MC.MavenConfig[CONFIG_USERSYNCSERVICE] = {
        http.CONFIG_BASEURL: 'http://localhost/services',
        http.CONFIG_OTHERHEADERS: {'Content-Type': 'application/json'},
    }
    MC.MavenConfig['maven user sync'] = {
        CONFIG_USERSYNCSERVICE: CONFIG_USERSYNCSERVICE,
        'customer_id': 5,
        CONFIG_SYNCDELAY: 60 * 6,
        CONFIG_API: 'allscripts_demo'
    }

    sync_scvs = UserSyncService('maven user sync')
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(sync_scvs.synchronize_users())

if __name__ == '__main__':
    run()
