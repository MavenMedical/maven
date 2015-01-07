# *************************************************************************
# Copyright (c) 2014 - Maven Medical
# ************************
# AUTHOR:
__author__ = 'Tom DuBois'
# ************************
# DESCRIPTION:
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
from utils.enums import USER_STATE  # , NOTIFICATION_STATE
from datetime import datetime, timedelta
import re
from dateutil.parser import parse
from utils.web_client.allscripts_http_client import AllscriptsError
from clientApp.webservice.composition_builder import CompositionBuilder
import maven_logging as ML
from collections import defaultdict
from utils.enums import CONFIG_PARAMS
icd9_keyword_match = re.compile('\(V?[0-9]+(?:\.[0-9]+)?(?:(?:\s+)?\|(?:\s+)?\w+)?\)')
icd9_capture = re.compile('(?:\((V?[0-9]+(?:\.[0-9]+)?)(?:(?:\s+)?\|(?:\s+)?\w+(?:\.\w+)?)?\))')
CLIENT_SERVER_LOG = ML.get_logger('clientApp.webservice.clientapp_main_server')


class scheduler():

    def __init__(self, parent, customer_id, allscripts_api, sleep_interval, disabled):
        self.parent = parent
        self.customer_id = customer_id
        self.allscripts_api = allscripts_api
        self.lastday = None
        self.comp_builder = CompositionBuilder(customer_id, allscripts_api)
        self.active_providers = {}
        self.disabled = disabled
        self.firsts = defaultdict(lambda: True)
        self.evaluations = {}
        self.report = lambda s: ML.report('/%s/%s' % (self.customer_id, s))
        self.listening = set()
        self.unitytimeoffset = timedelta()
        try:
            self.sleep_interval = float(sleep_interval)
        except ValueError as e:
            CLIENT_SERVER_LOG.exception(e)
            self.sleep_interval = float(45)

    def update_config(self, config):
        self.report('update_config')
        self.sleep_interval = float(config.get(CONFIG_PARAMS.EHR_API_POLLING_INTERVAL.value))
        self.disabled = config.get(CONFIG_PARAMS.EHR_DISABLE_INTEGRATION.value, False)
        if self.disabled:
            self.firsts = defaultdict(lambda: True)

    def update_active_providers(self, active_provider_list):
        self.report('update_active_providers')
        self.active_providers = dict(filter(lambda x: x[0][1] == str(self.customer_id), active_provider_list.items()))
        asyncio.Task(self.comp_builder.build_providers())

    def update_listening(self, user, state):
        if state:
            self.listening.add(user)
            ML.report('/' + str(self.customer_id) + '/user/' + user + '/started_listening')
        else:
            self.listening.discard(user)
            ML.report('/' + str(self.customer_id) + '/user/' + user + '/stopped_listening')

    @asyncio.coroutine
    def run(self):

        yield from self.comp_builder.build_providers()
        while True:
            self.report('polling')
            try:
                now = datetime.now()
                today = (now - self.unitytimeoffset).date()
                if today != self.lastday:
                    # servertime = now
                    serverinfo = yield from self.allscripts_api.GetServerInfo()
                    servertime = datetime.strptime(serverinfo['ServerTime'], '%Y-%m-%dT%H:%M:%S')
                    self.unitytimeoffset = now - servertime
                    self.lastday = today = servertime.date()
                    self.evaluations.clear()
                try:
                    sched = yield from self.allscripts_api.GetSchedule(None, today)
                    polling_providers = {x[0] for x in filter(self.check_notification_policy, self.active_providers)}
                    tasks = set()
                    CLIENT_SERVER_LOG.debug('processing %s providers for %s' % (polling_providers, self.customer_id))

                    for appointment in sched:
                        provider = appointment['ProviderID']
                        if provider in polling_providers:
                            patient = appointment['patientID']
                            tasks.add((patient, provider, today, self.firsts[provider]))
                        else:
                            ML.report('/' + str(self.customer_id) + '/provider/' + provider + '/not_active_or_listening')
                    for provider in polling_providers:
                        self.firsts[provider] = False
                    for task in tasks:
                        ML.TASK(self.evaluate(*task))
                except AllscriptsError as e:
                    CLIENT_SERVER_LOG.exception(e)

            except Exception as e:
                CLIENT_SERVER_LOG.exception(e)
            i = 0
            step = 5
            while i < self.sleep_interval or self.disabled:
                i = i + step
                yield from asyncio.sleep(step)

    @asyncio.coroutine
    def evaluate(self, patient, provider_id, today, first):
        CLIENT_SERVER_LOG.debug('evaluating %s/%s' % (patient, provider_id))
        provider = self.active_providers.get((provider_id, str(self.customer_id)))
        provider_username = provider.get('user_name')
        self.report('user/' + provider_username + '/query')

        now = datetime.now()
        prior = now - timedelta(seconds=12000)

        try:
            documents = yield from self.allscripts_api.GetDocuments(provider_username, patient,
                                                                    prior, now)
            if documents:
                for doc in documents:
                    # Ignore documents/encounters that were created by other providers
                    if not (doc.get('mydocument', 'N') == 'Y'):
                        continue

                    # Ignore old encounters
                    doctime = doc.get('SortDate', None)
                    enc_datetime = doctime and parse(doctime)
                    if not (enc_datetime.date() == today):
                        continue

                    # Add the provider/patient/encounter key to dictionary of evaluations if we haven't already
                    encounter_id = doc.get('DocumentID')
                    if (provider_id, patient, encounter_id) not in self.evaluations.keys():
                        self.evaluations[(provider_id, patient, encounter_id)] = {"encounter_create": True,
                                                                                  "assessment_and_plan": True}
                    # Check the keywords, and if there are ICD9 keywords we know that the clinician is already
                    # at the Assessment & Plan, so perform the "assessment_and_plan" evaluation (if haven't already)
                    document_keywords = doc.get('keywords', '')
                    has_ICD9_keywords = icd9_keyword_match.search(document_keywords)
                    encounter_dx = icd9_capture.findall(document_keywords)

                    if has_ICD9_keywords and self.evaluations[(provider_id, patient, encounter_id)].get('assessment_and_plan'):
                        if not first:
                            yield from self.build_composition_and_evaluate(provider_username, patient, encounter_id, enc_datetime, encounter_dx, 'assessment_and_plan')
                        # Set the flag in the evaluations dictionary so we don't do this evaluation again
                        self.evaluations[(provider_id, patient, encounter_id)]['assessment_and_plan'] = False
                        self.evaluations[(provider_id, patient, encounter_id)]['encounter_create'] = False

                    # If there are no ICD9 keywords, perform the "encounter_create" evaluation (if we haven't already)
                    elif self.evaluations[(provider_id, patient, encounter_id)].get('encounter_create'):
                        if not first:
                            yield from self.build_composition_and_evaluate(provider_username, patient, encounter_id, enc_datetime, encounter_dx, 'encounter_create')
                        self.evaluations[(provider_id, patient, encounter_id)]['encounter_create'] = False

        except AllscriptsError as e:
            CLIENT_SERVER_LOG.exception(e)
        except Exception as e:
            CLIENT_SERVER_LOG.exception(e)

    @asyncio.coroutine
    def build_composition_and_evaluate(self, provider_username, patient, encounter_id, enc_datetime, encounter_dx, eval_type):
        CLIENT_SERVER_LOG.debug("About to send to Composition Builder... %s, %s " % (provider_username, encounter_id))
        self.report('user/' + provider_username + '/' + eval_type)
        composition = yield from self.comp_builder.build_composition(provider_username, patient, encounter_id, enc_datetime, encounter_dx)
        CLIENT_SERVER_LOG.debug(("Sending to backend for %s evaluation. Composition ID = %s" % (composition.id, eval_type)))
        ML.TASK(self.parent.evaluate_composition(composition))

    def check_notification_policy(self, key):
        provider = self.active_providers.get(key)
        if (provider.get('state') == USER_STATE.ACTIVE.value and provider.get('ehr_state') == USER_STATE.ACTIVE.value
           and provider.get('user_name') in self.listening):
            return True
        else:
            return False
