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
import utils.api.pyfhir.pyfhir_generated as FHIR_API
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
        self.evaluated_states = []
        self.evaluated_states_time_limit = {}
        self.report = lambda s: ML.report('/%s/%s' % (self.customer_id, s))
        self.listening = set()
        self.unitytimeoffset = timedelta()
        self.taskcount = 0
        self.failed_patient_cdas = {}
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
        sched_count = 0
        sched = None
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
                    self.evaluated_states.clear()
                    self.evaluated_states_time_limit.clear()
                try:
                    if sched_count and sched:
                        sched_count -= 1
                    else:
                        sched_count = 5
                        sched = yield from self.allscripts_api.GetSchedule(None, today)
                    polling_providers = {x[0] for x in filter(self.check_notification_policy, self.active_providers)}
                    tasks = set()
                    CLIENT_SERVER_LOG.info('processing %s providers for %s, %s apts' % (polling_providers, self.customer_id, len(sched)))
                    servernow = now - self.unitytimeoffset
                    if servernow.hour > 0:
                        lowertime = (servernow - timedelta(hours=1)).strftime('%H:%M')
                    else:
                        lowertime = '00:00'
                    if servernow.hour < 23:
                        uppertime = (servernow + timedelta(hours=1)).strftime('%H:%M')
                    else:
                        uppertime = '24:00'
                    # skipped = [s for s in sched if lowertime > s['ApptTime'] or s['ApptTime'] <  uppertime]
                    # ML.INFO('skipping %s  not in (%s, %s)' % (skipped[0]['ApptTime'], lowertime, uppertime))
                    for appointment in [s for s in sched if lowertime <= s['ApptTime'] <= uppertime]:
                        provider = appointment['ProviderID']
                        if provider in polling_providers:
                            patient = appointment['patientID']
                            tasks.add((patient, provider, today, self.firsts[provider]))
                        else:
                            ML.report('/' + str(self.customer_id) + '/provider/' + provider + '/not_active_or_listening')
                    for provider in polling_providers:
                        self.firsts[provider] = False
                    CLIENT_SERVER_LOG.info('evaluating %s matching apts' % (len(tasks),))
                    for task in tasks:
                        self.taskcount += 1
                        ML.TASK(self.evaluate(*task))
                        yield from asyncio.sleep(.2)
                except AllscriptsError as e:
                    CLIENT_SERVER_LOG.exception(e)

            except Exception as e:
                CLIENT_SERVER_LOG.exception(e)
            i = 0
            step = 5
            while i < self.sleep_interval or self.disabled:
                i = i + step
                yield from asyncio.sleep(step)
            while self.taskcount:
                yield from asyncio.sleep(step)

    @asyncio.coroutine
    def evaluate(self, patient, provider_id, today, first):
        try:
            CLIENT_SERVER_LOG.debug('evaluating %s/%s' % (patient, provider_id))
            provider = self.active_providers.get((provider_id, str(self.customer_id)))
            provider_username = provider.get('user_name')
            self.report('user/' + provider_username + '/query')

            now = datetime.now()
            prior = now - timedelta(seconds=12000)
            try:
                documents = yield from self.allscripts_api.GetDocuments(provider_username, patient,
                                                                        prior, now)
                self.report('user/' + provider_username + '/got_docs/' + str(len(documents)))
                
                if documents:
                    for doc in documents:
                        # Ignore documents/encounters that were created by other providers
                        if not (doc.get('mydocument', 'N') == 'Y'):
                            self.report('user/' + provider_username + '/not_my_doc')
                            continue

                        # Ignore old encounters
                        doctime = doc.get('SortDate', None)
                        enc_datetime = doctime and parse(doctime)
                        if not (enc_datetime.date() == today):
                            self.report('user/' + provider_username + '/wrong_day_doc')
                            continue

                        # Document ID becomes encounter_id and we extract encounter ICD-9/10 keywords
                        encounter_id = doc.get('DocumentID')
                        encounter_dx = icd9_capture.findall(doc.get('keywords', ''))
                        CLIENT_SERVER_LOG.info(encounter_dx)

                        # This function will call GetCDA and build a proper proc_history ONLY if "185" in encounter_dx
                        proc_history, pat_cda_result = yield from self._build_proc_history_from_cda(provider_username, patient, encounter_id, encounter_dx)

                        # hack because allscripts messes up GetPatientCDA sometimes
                        if proc_history == None and pat_cda_result == None:
                            return

                        # Generate the eval_state hash and see if it's been evaluated before
                        eval_state = hash((provider_id, patient, encounter_id, tuple(sorted(encounter_dx)), tuple(sorted(proc_history))))
                        if eval_state not in self.evaluated_states:
                            self.evaluated_states.append(eval_state)
                            if not first:
                                ML.INFO('building composition')
                                eval_type = 'assessment_and_plan' if len(encounter_dx) > 0 else 'encounter_create'
                                yield from self.build_composition_and_evaluate(provider_username, patient, encounter_id, enc_datetime, encounter_dx, eval_type, pat_cda_result)

            except AllscriptsError as e:
                CLIENT_SERVER_LOG.exception(e)
            except Exception as e:
                CLIENT_SERVER_LOG.exception(e)
        finally:
            self.taskcount -= 1

    @asyncio.coroutine
    def _build_proc_history_from_cda(self, provider_username, patient, encounter_id, encounter_dx_list):

        pat_cda_result = None
        proc_history = []

        if patient in self.failed_patient_cdas:
            return None, None

        # The below IF STATEMENT is the hacky solution to not hitting allscripts too hard on getCDA
        if "185" in encounter_dx_list:

            # Add timer for this extra GetCDA loop for multiple A&P evaluations
            if (provider_username, patient, encounter_id) not in self.evaluated_states_time_limit.keys():
                self.evaluated_states_time_limit.update({(provider_username, patient, encounter_id): datetime.now()})

            if datetime.now() < (self.evaluated_states_time_limit[(provider_username, patient, encounter_id)] + timedelta(minutes=20)):

                # GetCDA call is needed for procedure history, which is a component in the eval_state hash
                try:
                    ML.report('%s/GetPatientCDA' % (self.customer_id,))
                    pat_cda_result = yield from self.allscripts_api.GetPatientCDA(provider_username, patient)
                except Exception as e:
                    ML.WARN('skipping patient %s with prior CDA fail, %s in list for %s' % (patient, len(self.failed_patient_cdas), self.customer_id))
                    ML.report('%s/Failed_GetPatientCDA' % (self.customer_id,))
                    self.failed_patient_cdas[patient]=True
                    return None, None

                procedure_history_section = self.comp_builder.extract_hcpcs_codes_from_cda(pat_cda_result)

                proc_history = []
                if procedure_history_section:
                    for enc_ord in [(order) for order in procedure_history_section.content if isinstance(order.detail[0], FHIR_API.Procedure)]:
                        terminology_code = enc_ord.get_proc_med_terminology_coding()
                        proc_history.append(terminology_code.code)

        return proc_history, pat_cda_result

    @asyncio.coroutine
    def build_composition_and_evaluate(self, provider_username, patient, encounter_id, enc_datetime, encounter_dx, eval_type, pat_cda_result):
        CLIENT_SERVER_LOG.info("About to send to Composition Builder... %s, %s " % (provider_username, encounter_id))
        self.report('user/' + provider_username + '/' + eval_type)
        composition = yield from self.comp_builder.build_composition(provider_username, patient, encounter_id, enc_datetime, encounter_dx, pat_cda_result)
        CLIENT_SERVER_LOG.info(("Sending to backend for %s evaluation. Composition ID = %s" % (composition.id, eval_type)))
        ML.TASK(self.parent.evaluate_composition(composition))

    def check_notification_policy(self, key):
        provider = self.active_providers.get(key)
#        if (provider.get('state') == USER_STATE.ACTIVE.value and provider.get('ehr_state') == USER_STATE.ACTIVE.value
#           and provider.get('user_name') in self.listening):
        if (provider.get('state') == USER_STATE.ACTIVE.value and provider.get('ehr_state') == USER_STATE.ACTIVE.value):
            return True
        else:
            return False
