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
import asyncio
from collections import Counter
import maven_config as MC
import maven_logging as ML
import utils.web_client.allscripts_http_client as AHC
from utils.enums import USER_STATE, CONFIG_PARAMS

CONFIG_USERSYNCSERVICE = 'sync user service'
CONFIG_SYNCDELAY = 'sync delay'
CONFIG_API = 'api'
logger = ML.get_logger()
ML.set_debug()


class UserSyncService():
    def __init__(self, customer_id, sync_interval, server_interface, ehr_api, disabled):
        self.customer_id = customer_id
        self.sync_delay = sync_interval
        self.server_interface = server_interface or Exception("No Remote Procedures Specified for ClientApp")
        self.ehr_api = ehr_api
        self.loop = asyncio.get_event_loop()

        self.ehr_providers = {}
        self.maven_providers = []
        self.active_providers = {}
        self.provider_list_observers = []
        self.disabled = disabled

    def update_config(self, config):
        self.sync_delay = config.get(CONFIG_PARAMS.EHR_USER_SYNC_INTERVAL.value, 60 * 60)
        self.disabled = config.get(CONFIG_PARAMS.EHR_DISABLE_INTEGRATION.value, False)

    def subscribe(self, observer):
        self.provider_list_observers.append(observer)

    @ML.coroutine_trace(logger.debug)
    def run(self):
        while True:
            if not self.disabled:
                yield from self.evaluate_users(self.customer_id)
            i = 0
            step = 5
            while i < self.sync_delay:
                i = i + step
                yield from asyncio.sleep(step)

    @ML.coroutine_trace(logger.debug)
    def evaluate_users(self, customer_id):
        try:
            try:
                ehr_providers = yield from self.ehr_api.GetProviders()
                for provider in ehr_providers:
                    fhir_provider = self.ehr_api.build_partial_practitioner(provider)
                    self.ehr_providers[fhir_provider.get_provider_id()] = fhir_provider
            except AHC.AllscriptsError as e:
                logger.exception(e)

            self.maven_providers = yield from self.server_interface.get_users_from_db(self.customer_id)

            # Add any new users to the in-memory list of active users
            for provider in self.maven_providers:
                self.active_providers[(provider['prov_id'], str(customer_id))] = provider

            # Go through the two sets of users (Maven, EHR's) and diff/update appropriately
            yield from self.diff_users(customer_id)

            # Share the in-memory list of active providers with the subscribers to this functionality
            # i.e. Notification Service, Allscripts_server, etc.
            self.update_provider_list_observers(self.active_providers)

        except Exception as e:
                logger.exception(e)

    def update_provider_list_observers(self, providers):
        for updateProviderList in self.provider_list_observers:
            updateProviderList(providers)

        # Update the notification preferences of users in the Notification Service
        asyncio.Task(self.server_interface.update_notify_prefs(self.customer_id))

    @ML.coroutine_trace(logger.debug, timing=True)
    def diff_users(self, customer_id):
        # create 2 lists containing provider_id to see if we need to CREATE new users
        ehr_prov_list = Counter([prov.get_provider_id() for prov in self.ehr_providers.values()])
        maven_prov_list = Counter([(prov['prov_id']) for prov in self.maven_providers])

        # Identify new EHR Providers that Maven is not aware of and write new users to Maven DB
        new_provider_list = list((ehr_prov_list - maven_prov_list).elements())
        if new_provider_list:
            for new_provider in new_provider_list:
                yield from self.create_maven_user(self.ehr_providers[new_provider], customer_id)

        # create 2 lists of tuples containing (provider_id, active state) to see if we need to UPDATE user's EHR state
        ehr_prov_list2 = Counter([(prov.get_provider_id(), prov.ehr_state) for prov in self.ehr_providers.values()])
        maven_prov_list2 = Counter([(prov['prov_id'], prov['ehr_state']) for prov in self.maven_providers])

        # Identify EHR Providers that have been deactivated in their EHR and write changes to Maven DB
        deactivated_provider_list = list((maven_prov_list2 - ehr_prov_list2).elements())
        if deactivated_provider_list:
            for deactivated_provider in [prov for prov in deactivated_provider_list if prov[1] == USER_STATE.ACTIVE.value]:
                yield from self.deactivate_user_state(deactivated_provider, customer_id)

        # Identify EHR Providers that have been reactivated in their EHR and write changes to Maven DB
        reactivated_provider_list = list((ehr_prov_list2 - maven_prov_list2).elements())
        if reactivated_provider_list:
            for updated_provider in reactivated_provider_list:
                yield from self.reactivate_user_state(updated_provider, customer_id)

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
                        "specialty": missing_provider.specialty[0],
                        "profession": missing_provider.role[0]
                        }

        # Add user to maven_providers list so that the user can be added to the global providers dictionary
        self.maven_providers.append(new_provider)

        yield from self.server_interface.write_user_create_to_db(self.customer_id, new_provider)
        yield from self.server_interface.write_audit_log(new_provider['user_name'],
                                                         'New User Created',
                                                         new_provider['customer_id'])

    @ML.coroutine_trace(logger.debug)
    def deactivate_user_state(self, updated_provider, customer_id):

        if updated_provider[1] == USER_STATE.ACTIVE.value:
            provider = {"customer_id": customer_id,
                        "prov_id": updated_provider[0],
                        "ehr_state": USER_STATE.DISABLED.value}
            yield from self.server_interface.write_user_update_to_db(self.customer_id, provider)

            for user in [user for user in self.maven_providers if user['prov_id'] == updated_provider[0]]:
                self.active_providers[(user['prov_id'], str(self.customer_id))]['ehr_state'] = USER_STATE.DISABLED.value
                yield from self.server_interface.write_audit_log(user['user_name'],
                                                                 'EHR State Disabled for User',
                                                                 user['customer_id'])

    @ML.coroutine_trace(logger.debug)
    def reactivate_user_state(self, updated_provider, customer_id):

        provider = {"customer_id": customer_id,
                    "prov_id": updated_provider[0],
                    "ehr_state": USER_STATE.ACTIVE.value}
        yield from self.server_interface.write_user_update_to_db(self.customer_id, provider)

        for user in [user for user in self.maven_providers if user['prov_id'] == updated_provider[0]]:
            self.active_providers[(user['prov_id'], str(self.customer_id))]['ehr_state'] = USER_STATE.ACTIVE.value
            yield from self.server_interface.write_audit_log(user['user_name'],
                                                             'EHR State Enabled for User',
                                                             user['customer_id'])

    def update_active_provider_state(self, user_name, state):

        for user in self.maven_providers:
            if user.get('user_name', None) == user_name:
                prov_id = user.get('prov_id')
                break
        self.active_providers[(prov_id, str(self.customer_id))]['state'] = state
        self.update_provider_list_observers(self.active_providers)


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
    MC.MavenConfig['maven user sync'] = {
        'customer_id': 5,
        CONFIG_SYNCDELAY: 60 * 6,
        CONFIG_API: 'allscripts_demo'
    }
    MC.MavenConfig['customer_id'] = 5

    sync_scvs = UserSyncService('maven user sync')
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(sync_scvs.run())

if __name__ == '__main__':
    run()
