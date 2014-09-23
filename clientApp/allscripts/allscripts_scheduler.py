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
from utils.enums import USER_STATE, NOTIFICATION_STATE
from datetime import date, datetime, timedelta
import re
from dateutil.parser import parse
from utils.web_client.allscripts_http_client import AllscriptsError
from clientApp.webservice.composition_builder import CompositionBuilder
import maven_logging as ML

icd9_match = re.compile('\(V?[0-9]+(?:\.[0-9]+)?\)')
CLIENT_SERVER_LOG = ML.get_logger('clientApp.webservice.allscripts_server')


class scheduler():

    def __init__(self, parent, customer_id, allscripts_api, sleep_interval):
        self.parent = parent
        self.customer_id = customer_id
        self.allscripts_api = allscripts_api
        self.processed = set()
        self.lastday = None
        self.comp_builder = CompositionBuilder(customer_id, allscripts_api)
        self.sleep_interval = sleep_interval
        self.active_providers = {}

    def update_active_providers(self, active_provider_list):
        self.active_providers = active_provider_list

    @asyncio.coroutine
    def run(self):

        yield from self.comp_builder.build_providers()
        first = True
        while True:
            try:
                today = date.today()
                if today != self.lastday:
                    self.lastday = today
                    self.processed = set()
                    sched = []
                try:
                    for provider in self.active_providers:
                        sched = yield from self.allscripts_api.GetSchedule(self.active_providers.get(provider)['user_name'], today)
                        tasks = set()
                        for appointment in sched:
                            patient = appointment['patientID']
                            provider = appointment['ProviderID']
                            tasks.add((patient, provider, today, first))
                        for task in tasks:
                            ML.TASK(self.evaluate(*task))

                except AllscriptsError as e:
                    CLIENT_SERVER_LOG.exception(e)
                # print([(sch['patientID'], sch['ApptTime2'], sch['ProviderID']) for sch in sched])

                # CLIENT_SERVER_LOG.debug(sched)

            except Exception as e:
                CLIENT_SERVER_LOG.exception(e)
            yield from asyncio.sleep(self.sleep_interval)
            first = False

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
                    match = icd9_match.search(keywords)
                    docid = doc.get('DocumentID')
                    doctime = doc.get('SortDate', None)
                    todaydoc = doctime and datetime.date(parse(doctime)) == today
                    newdoc = True
                    if match and newdoc and todaydoc and (patient, provider_id, today, docid) not in self.processed:
                        ML.DEBUG('got doc, (match, newdoc, docid, first) = %s' % str((match, newdoc, docid, first)))
                        self.processed.add((patient, provider_id, today, docid))
                        if not first:
                            # start, stop = match.span()
                            CLIENT_SERVER_LOG.debug("About to send to Composition Builder...")
                            composition = yield from self.comp_builder.build_composition(provider_username, patient, docid)
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

        if provider.get('state') == USER_STATE.ACTIVE.value and provider.get('ehr_state') == USER_STATE.ACTIVE.value and provider.get('notification_state', None) is not None:
            return True
        elif provider.get('state') == USER_STATE.ACTIVE.value and provider.get('ehr_state') == USER_STATE.ACTIVE.value and provider.get('notification_state', None) == NOTIFICATION_STATE.MOBILE:
            return True
        else:
            return False
