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
import json
import utils.web_client.http_client as http
import asyncio
from collections import Counter
import maven_config as MC
import maven_logging as ML
import utils.web_client.allscripts_http_client as AHC
from utils.enums import USER_STATE

CONFIG_USERSYNCSERVICE = 'sync user service'
CONFIG_SYNCDELAY = 'sync delay'
CONFIG_API = 'api'
logger = ML.get_logger()
ML.set_debug()


class UserSyncService(http.http_api):
    def __init__(self, configname, loop=None):
        self.config = MC.MavenConfig[configname]
        self.customer_id = MC.MavenConfig['customer_id']
        self.sync_delay = self.config.get(CONFIG_SYNCDELAY, 60 * 60)
        self.api_name = self.config[CONFIG_API]
        self.ehr_api = AHC.allscripts_api(self.api_name)
        super(UserSyncService, self).__init__(CONFIG_USERSYNCSERVICE)
        self.postprocess = (lambda x: list(x[0].values())[0])
        self.loop = loop or asyncio.get_event_loop()
        self.ehr_providers = {}
        self.maven_providers = []
        self.active_providers = {}
        self.provider_list_observers = []

    def subscribe(self, observer):
        self.provider_list_observers.append(observer)

    @ML.coroutine_trace(logger.debug)
    def synchronize_users(self):
        while True:
            yield from self.evaluate_users(self.customer_id)
            yield from asyncio.sleep(self.sync_delay)

    @ML.coroutine_trace(logger.debug)
    def evaluate_users(self, customer_id):
        try:
            try:
                ehr_providers = yield from self.ehr_api.GetProviders(username=MC.MavenConfig[self.api_name][AHC.CONFIG_APPUSERNAME])

                for provider in ehr_providers:
                    fhir_provider = self.ehr_api.build_partial_practitioner(provider)
                    self.ehr_providers[fhir_provider.get_provider_id()] = fhir_provider
            except AHC.AllscriptsError as e:
                logger.exception(e)

            try:
                ret = yield from self.get('/syncusers', rawdata=False, params={"roles[]": "maventask",
                                                                               "customer_id": customer_id})
                self.maven_providers = json.loads(ret)

            except Exception as e:
                logger.exception(e)

            # Go through the two sets of users (Maven, EHR's) and diff/update appropriately
            yield from self.diff_users(customer_id)

            # Add any new users to the in-memory list of active users
            for provider in self.maven_providers:
                self.active_providers[(provider['prov_id'], str(customer_id))] = provider

            # Share the in-memory list of active providers with the subscribers to this functionality
            # i.e. Notification Service, Allscripts_server, etc.
            self.update_provider_list_observers(self.active_providers)

        except Exception as e:
                logger.exception(e)

    def update_provider_list_observers(self, providers):
        for updateProviderList in self.provider_list_observers:
            updateProviderList(providers)

    @ML.coroutine_trace(logger.debug)
    def diff_users(self, customer_id):
        # create 2 lists containing provider_id to see if we need to CREATE new users
        ehr_prov_list = Counter([prov.get_provider_id() for prov in self.ehr_providers.values()])
        maven_prov_list = Counter([(prov['prov_id']) for prov in self.maven_providers])

        # Identify new EHR Providers that Maven is not aware of and write new users to Maven DB
        new_provider_list = list((ehr_prov_list - maven_prov_list).elements())
        if new_provider_list:
            for deactivated_provider in new_provider_list:
                yield from self.create_maven_user(self.ehr_providers[deactivated_provider], customer_id)

        # create 2 lists of tuples containing (provider_id, active state) to see if we need to UPDATE user's EHR state
        ehr_prov_list2 = Counter([(prov.get_provider_id(), prov.ehr_state) for prov in self.ehr_providers.values()])
        maven_prov_list2 = Counter([(prov['prov_id'], prov['ehr_state']) for prov in self.maven_providers])

        # Identify EHR Providers that have been deactivated in their EHR and write changes to Maven DB
        deactivated_provider_list = list((maven_prov_list2 - ehr_prov_list2).elements())
        if deactivated_provider_list:
            for deactivated_provider in deactivated_provider_list:
                yield from self.update_maven_user_state(deactivated_provider[0], customer_id)

    @ML.coroutine_trace(logger.debug)
    def create_maven_user(self, missing_provider, customer_id):

        for identifier in missing_provider.identifier:
            if identifier.system == "clientEMR" and identifier.label == "Internal":
                provider_id = identifier.value
            elif identifier.system == "clientEMR" and identifier.label == "Username":
                provider_username = identifier.value

        provider_official_name = missing_provider.name.given[0] + " " + missing_provider.name.family[0]
        provider_display_name = provider_official_name

        new_provider = {"customer_id": customer_id,
                        "prov_id": provider_id,
                        "user_name": provider_username,
                        "official_name": provider_official_name,
                        "display_name": provider_display_name,
                        "state": missing_provider.state,
                        "ehr_state": missing_provider.ehr_state,
                        "specialty": missing_provider.specialty[0]
                        }

        # Add user to maven_providers list so that the user can be added to the global providers dictionary
        self.maven_providers.append(new_provider)

        ret = yield from self.post('/synccreateuser',
                                   rawdata=True,
                                   params={"roles[]": "maventask",
                                           "customer_id": customer_id},
                                   data=json.dumps(new_provider))

    @ML.coroutine_trace(logger.debug)
    def update_maven_user_state(self, deactivated_provider_id, customer_id):

        provider = {"customer_id": customer_id,
                    "prov_id": deactivated_provider_id,
                    "ehr_state": USER_STATE.DISABLED.value
                    }

        for prov in [prov for prov in self.maven_providers if prov['prov_id'] == deactivated_provider_id]:
            prov['ehr_state'] = USER_STATE.DISABLED.value

        ret = yield from self.post('/syncupdateuser',
                                   rawdata=True,
                                   params={"roles[]": "maventask",
                                           "customer_id": customer_id},
                                   data=json.dumps(provider))


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
    MC.MavenConfig['customer_id'] = 5

    sync_scvs = UserSyncService('maven user sync')
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(sync_scvs.synchronize_users())

if __name__ == '__main__':
    run()
