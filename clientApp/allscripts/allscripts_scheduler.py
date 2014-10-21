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
from datetime import date, datetime, timedelta
import re
from dateutil.parser import parse
from utils.web_client.allscripts_http_client import AllscriptsError
from clientApp.webservice.composition_builder import CompositionBuilder
import maven_logging as ML
from collections import defaultdict
from utils.enums import CONFIG_PARAMS
icd9_keyword_match = re.compile('\(V?[0-9]+(?:\.[0-9]+)?\)')
icd9_capture = re.compile('(?:\((V?[0-9]+(?:\.[0-9]+)?)\))')
CLIENT_SERVER_LOG = ML.get_logger('clientApp.webservice.allscripts_server')


class scheduler():

    def __init__(self, parent, customer_id, allscripts_api, sleep_interval, disabled):
        self.parent = parent
        self.customer_id = customer_id
        self.allscripts_api = allscripts_api
        self.processed = set()
        self.lastday = None
        self.comp_builder = CompositionBuilder(customer_id, allscripts_api)
        self.active_providers = {}
        self.disabled = disabled
        try:
            self.sleep_interval = float(sleep_interval)
        except ValueError as e:
            CLIENT_SERVER_LOG.exception(e)
            self.sleep_interval = float(45)

    def update_config(self, config):
        self.sleep_interval = float(config.get(CONFIG_PARAMS.EHR_API_POLLING_INTERVAL.value))
        self.disabled = config.get(CONFIG_PARAMS.EHR_DISABLE_INTEGRATION.value, False)

    def update_active_providers(self, active_provider_list):
        self.active_providers = dict(filter(lambda x: x[0][1] == str(self.customer_id), active_provider_list.items()))
        asyncio.Task(self.comp_builder.build_providers())

    @asyncio.coroutine
    def run(self):

        yield from self.comp_builder.build_providers()
        firsts = defaultdict(lambda: True)
        while True:
            try:
                today = date.today()
                if today != self.lastday:
                    self.lastday = today
                    self.processed = set()
                try:
                    sched = yield from self.allscripts_api.GetSchedule(None, today)
                    polling_providers = {x[0] for x in filter(self.check_notification_policy, self.active_providers)}
                    tasks = set()
                    CLIENT_SERVER_LOG.debug('processing %s providers for %s' % (polling_providers, self.customer_id))

                    for appointment in sched:
                        provider = appointment['ProviderID']
                        if provider in polling_providers:
                            patient = appointment['patientID']
                            tasks.add((patient, provider, today, firsts[provider]))
                    for provider in polling_providers:
                        firsts[provider] = False
                    for task in tasks:
                        ML.TASK(self.evaluate(*task))
                except AllscriptsError as e:
                    CLIENT_SERVER_LOG.exception(e)
                # print([(sch['patientID'], sch['ApptTime2'], sch['ProviderID']) for sch in sched])

                # CLIENT_SERVER_LOG.debug(sched)

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
        try:
            # print('evaluating %\s for %s' % (patient, provider))
            now = datetime.now()
            prior = now - timedelta(seconds=12000)
        except:
            import traceback
            traceback.print_exc()
        try:
            documents = yield from self.allscripts_api.GetDocuments(provider_username, patient,
                                                                    prior, now)
            # print('got %d documents' % len(documents))
            # ML.DEBUG('documents: %d' % len(documents))
            if documents:
                # print('\n'.join([str((doc['DocumentID'], doc['SortDate'], doc['keywords'])) for doc in documents]))
                for doc in documents:
                    keywords = doc.get('keywords', '')
                    match = icd9_keyword_match.search(keywords)
                    mydoc = doc.get('mydocument', 'N') == 'Y'
                    docid = doc.get('DocumentID')
                    doctime = doc.get('SortDate', None)
                    enc_datetime = doctime and parse(doctime)
                    todaydoc = enc_datetime and enc_datetime.date() == today
                    newdoc = True
                    if (mydoc and match and newdoc and todaydoc and
                       (patient, provider_id, today, docid) not in self.processed):
                        ML.DEBUG('got doc, (match, newdoc, docid, first) = %s' % str((match, newdoc, docid, first)))
                        self.processed.add((patient, provider_id, today, docid))
                        if not first:
                            # start, stop = match.span()
                            encounter_dx = icd9_capture.findall(keywords)
                            CLIENT_SERVER_LOG.debug("About to send to Composition Builder...")
                            composition = yield from self.comp_builder.build_composition(provider_username, patient, docid, enc_datetime, encounter_dx)
                            CLIENT_SERVER_LOG.debug(("Built composition, about to send to Backend Data Router. Composition ID = %s" % composition.id))
                            ML.TASK(self.parent.evaluate_composition(composition))
                            break
                # processed.update({doc['DocumentID'] for doc in documents})
        except AllscriptsError as e:
            CLIENT_SERVER_LOG.exception(e)
        except Exception as e:
            CLIENT_SERVER_LOG.exception(e)

    def check_notification_policy(self, key):
        provider = self.active_providers.get(key)
        if provider.get('state') == USER_STATE.ACTIVE.value and provider.get('ehr_state') == USER_STATE.ACTIVE.value:
            return True
        else:
            return False
