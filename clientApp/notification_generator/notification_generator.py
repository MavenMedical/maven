# *************************************************************************
# Copyright (c) 2014 - Maven Medical
# ************************
# AUTHOR:
__author__ = 'Yuki Uchino'
# ************************
# DESCRIPTION:   This notification_generator.py contains the classes required to generate
#                EMR-specific notification messages, in order to accommodate the available
#                features in each environment (e.g. WorldVistA will utilize Dave's Java Notification
#                system, whereas the Notifications targeting Epic will have to be constructed in a
#                BPA-friendly manner.)
# ************************
# ASSUMES:
# ************************
# SIDE EFFECTS:
# ************************
# LAST MODIFIED FOR JIRA ISSUE: MAV-150
# *************************************************************************
import asyncio
import maven_config as MC
import maven_logging as ML
import urllib
import urllib.parse
import html
import math
import jinja2
from utils.enums import ALERT_VALIDATION_STATUS, ALERT_TYPES, ALERT_PRIORITY


EMR_TYPE = "emrtype"
EMR_VERSION = "emrversion"
CLIENTAPP_LOCATION = "clientapplocation"
DEBUG = "debug"
COST_ALERT_ICON = "costalerticon"
TEMPLATE_LOAD_PATH = "templateloadpath"
MAX_MSG_LOAD = "maxmsgload"

NG_LOG = ML.get_logger()


class NotificationGenerator():

    def __init__(self, config):

        """ Initialize the Notification Generator class, instantiating all of the helper functions
        required to generate an EMR-specific Notification alert

        :param config: the name of the instance to pull config parameters
        """

        if not config:
            raise MC.InvalidConfig("Notification Generator needs a config entry")
        try:
            self.config = config
            try:
                # self.emrtype = config.get(EMR_TYPE, None)
                # self.emrversion = config.get(EMR_VERSION, None)
                self.DEBUG = config.get(DEBUG, True)
                self.templateEnv = {}

                self.max_msg_load = config.get(MAX_MSG_LOAD, None)

                templateLoader = jinja2.FileSystemLoader('/home/devel/maven/clientApp/notification_generator/VistA/templates')
                self.templateEnv['vista'] = jinja2.Environment(loader=templateLoader)

                templateLoader = jinja2.FileSystemLoader('/home/devel/maven/clientApp/notification_generator/Epic/templates')
                self.templateEnv['epic'] = jinja2.Environment(loader=templateLoader)

                templateLoader = jinja2.FileSystemLoader('/home/devel/maven/clientApp/notification_generator/Web/templates')
                self.templateEnv['web'] = jinja2.Environment(loader=templateLoader)

            except KeyError:
                raise MC.InvalidConfig(config + " did not have sufficient parameters.")

        except Exception as e:
            ML.ERROR("MC.InvalidConfig in " + self.config)
            raise e

    @asyncio.coroutine
    def generate_alert_content(self, composition, emrtype, emrversion):

        # DEBUG trigger, when set to True, messages get sent, when set to False, empty list gets sent
        if self.DEBUG:

            if emrtype == 'vista':
                return self._vista_alert_content_generator(composition, self.templateEnv[emrtype])

            elif emrtype == 'epic' and emrversion in ['2010', '2012']:
                return self._epic_alert_content_generator(composition, self.templateEnv[emrtype])
            elif emrtype == 'web':
                return self._web_alert_content_generator(composition, self.templateEnv[emrtype])
        else:
            return []

    ################################################################################################
    ################################################################################################
    # Start Vista Alert Generator Components
    ################################################################################################
    @ML.coroutine_trace(timing=True, write=NG_LOG.debug)
    def _vista_alert_content_generator(self, composition, templateEnv):

        alert_contents = []
        fhir_alerts = sorted(composition.get_section_by_coding(code_system="maven", code_value="alerts").content,
                             key=lambda x: ALERT_PRIORITY[x.category.name].value,
                             reverse=True)

        # Shared data elements for all alerts so we don't have to keep passing the composition around everywhere
        base_alert_data = {"alert_id": composition.id,
                           "rule_id": 0,
                           "provider": composition.get_author_id(),
                           "user": composition.author.get_provider_username(),
                           "customer_id": composition.customer_id,
                           "userAuth": composition.userAuth,
                           "csn": urllib.parse.quote(composition.encounter.get_csn()),
                           "patient_id": composition.subject.get_pat_id()}

        for alert in fhir_alerts[0:self.max_msg_load]:
            if alert.category == ALERT_TYPES.COST and alert.validation_status > ALERT_VALIDATION_STATUS.DEBUG_ALERT.value:
                content = yield from self._vista_cost_alert_generator(alert, base_alert_data, templateEnv)
                alert_contents.append(content)

            elif alert.category == ALERT_TYPES.REC_RESULT and alert.validation_status > ALERT_VALIDATION_STATUS.DEBUG_ALERT.value:
                content = yield from self._vista_recent_results_alert_generator(alert, base_alert_data, templateEnv)
                alert_contents.append(content)

            elif alert.category == ALERT_TYPES.CDS and alert.validation_status > ALERT_VALIDATION_STATUS.DEBUG_ALERT.value:
                content = yield from self._vista_CDS_alert_generator(alert, base_alert_data, templateEnv)
                alert_contents.append(content)

        ML.DEBUG("Generated %s VistA Alerts" % len(alert_contents))

        return alert_contents

    @asyncio.coroutine
    def _vista_cost_alert_generator(self, alert, base_alert_data, templateEnv):

        # creates the cost alert html. This may want to become more sophisticated over time to
        # dynamically shorten the appearance of a very large active orders list
        TEMPLATE_FILE = "cost_alert2.html"
        TEMPLATE_HEADER = "notificationHeader.html"

        template = templateEnv.get_template(TEMPLATE_FILE)
        templateHeader = templateEnv.get_template(TEMPLATE_HEADER)

        templateVars = yield from self._generate_cost_alert_template_vars(alert, base_alert_data)
        notification_body = templateHeader.render(templateVars)
        notification_body += template.render(templateVars)

        return notification_body

    @asyncio.coroutine
    def _generate_cost_alert_template_vars(self, alert, base_alert_data):

        templateVars = {"alert_id": base_alert_data['alert_id'],
                        "provider": base_alert_data['provider'],
                        "rule_id": base_alert_data['rule_id'],
                        "order_list": alert.cost_breakdown['details'],
                        "total_cost": math.ceil(alert.cost_breakdown['total_cost']),
                        "http_address": MC.http_addr,
                        "encounter_id": base_alert_data['csn'],
                        "patient_id": base_alert_data['patient_id'],
                        "user": base_alert_data['user'],
                        "customer_id": base_alert_data['customer_id'],
                        "user_auth": base_alert_data['userAuth']}

        return templateVars

    @asyncio.coroutine
    def _vista_CDS_alert_generator(self, alert, base_alert_data, templateEnv):

        TEMPLATE_FILE = "cds_alert.html"
        template_sleuth_alert = templateEnv.get_template(TEMPLATE_FILE)

        templateVars = {"alert_tag_line": html.escape(alert.short_title),
                        "alert_description": html.escape(alert.short_description),
                        "evi_id": alert.CDS_rule,
                        "http_address": MC.http_addr,
                        "encounter_id": base_alert_data['csn'],
                        "patient_id": base_alert_data['patient_id'],
                        "user": base_alert_data['user'],
                        "customer_id": base_alert_data['customer_id'],
                        "user_auth": base_alert_data['userAuth']}

        notification_body = template_sleuth_alert.render(templateVars)

        return notification_body

    @asyncio.coroutine
    def _vista_recent_results_alert_generator(self, alert, base_alert_data, templateEnv):

        TEMPLATE_FILE = "duplicate_order_alert.html"
        template_dup_order_alert = templateEnv.get_template(TEMPLATE_FILE)

        templateVars = {"alert_tag_line": html.escape(alert.short_title),
                        "alert_description": html.escape(alert.short_description),
                        "related_observations": alert.related_observations,
                        "http_address": MC.http_addr,
                        "encounter_id": base_alert_data['csn'],
                        "patient_id": base_alert_data['patient_id'],
                        "user": base_alert_data['user'],
                        "customer_id": base_alert_data['customer_id'],
                        "user_auth": base_alert_data['userAuth']}

        notification_body = template_dup_order_alert.render(templateVars)

        return notification_body

    ################################################################################################
    ################################################################################################
    # Start Web Alert Generator Components
    ################################################################################################
    @asyncio.coroutine
    def _web_alert_content_generator(self, composition, templateEnv):
        alert_contents = []

        # creates the cost alert html. This may want to become more sophisticated over time to
        # dynamically shorten the appearance of a very large active orders list
        # cost_alert = yield from self._web_cost_alert_generator(composition, templateEnv)
        # alert_contents.append(cost_alert)

        # sleuth_alerts = yield from self._web_sleuth_alert_generator(composition, templateEnv)
        # if sleuth_alerts is not None and len(sleuth_alerts) > 0:
        #    for sa in sleuth_alerts:
        #        alert_contents.append(sa)

        pathway_alerts = yield from self._web_pathway_alert_generator(composition, templateEnv)
        alert_contents.append(pathway_alerts)

        ML.DEBUG("Generated %s Web Alerts" % len(alert_contents))

        return alert_contents

    @asyncio.coroutine
    def _web_pathway_alert_generator(self, composition, templateEnv):

        TEMPLATE_FILE = "pathway_alert.html"
        template = templateEnv.get_template(TEMPLATE_FILE)

        # TODO - This composition method is ONLY PULLING ONE Pathway alert even if multiple have fired
        pathway_alert = composition.get_alerts_by_type(type=ALERT_TYPES.PATHWAY)

        templateVars = {"http_address": MC.http_addr,
                        "pathway_id": pathway_alert.CDS_rule,
                        "node_id": 1,
                        "encounter_id": urllib.parse.quote(composition.encounter.get_csn()),
                        "encounter_date": composition.encounter.get_admit_date().date().isoformat(),
                        "patient_id": composition.subject.get_pat_id(),
                        "user": composition.author.get_provider_username(),
                        "user_auth": composition.userAuth,
                        "customer_id": composition.customer_id}
        notification_body = template.render(templateVars)

        return notification_body

    @asyncio.coroutine
    def _web_cost_alert_generator(self, composition, templateEnv):

        TEMPLATE_FILE = "cost_alert.html"
        # TEMPLATE2_FILE = "cost_alert2.html"
        # TEMPLATE3_FILE = "notification.js"
        template = templateEnv.get_template(TEMPLATE_FILE)
        # template2 = templateEnv.get_template(TEMPLATE2_FILE)
        # template3 = templateEnv.get_template(TEMPLATE3_FILE)
        # cost_alert = composition.get_alerts_by_type(type=ALERT_TYPES.COST)
        templateVars = self._generate_cost_alert_template_vars(composition)
        notification_body = template.render(templateVars)

        return notification_body

    @asyncio.coroutine
    def _web_sleuth_alert_generator(self, composition, templateEnv):

        TEMPLATE_FILE = "cds_alert.html"
        template_sleuth_alert = templateEnv.get_template(TEMPLATE_FILE)

        sleuth_alert_HTML_contents = []
        user = composition.author.get_provider_username()
        customer = composition.customer_id
        userAuth = composition.userAuth
        csn = urllib.parse.quote(composition.encounter.get_csn())
        patient_id = composition.subject.get_pat_id()

        # composition_alert_section = composition.get_alerts_section()
        CDS_alerts = composition.get_alerts_by_type(type=ALERT_TYPES.CDS)

        # check to see if there's anything in the list. Should probably move this to the FHIR api
        # if composition_alert_section is not None and len(composition_alert_section.content) > 0:

        for alert in CDS_alerts['alert_list']:

            templateVars = {"alert_tag_line": alert.short_title,
                            "alert_description": alert.long_description,
                            "http_address": MC.http_addr,
                            "encounter_id": csn,
                            "patient_id": patient_id,
                            "evi_id": alert.CDS_rule,
                            "user": user,
                            "customer_id": customer,
                            "user_auth": userAuth}

            notification_body = template_sleuth_alert.render(templateVars)
            sleuth_alert_HTML_contents.append(notification_body)

        return sleuth_alert_HTML_contents

    ################################################################################################
    ################################################################################################
    # Start Epic Alert Generator Components
    ################################################################################################
    @asyncio.coroutine
    def _epic_alert_content_generator(self, composition, templateEnv):
        alert_contents = []

        # creates the cost alert html. This may want to become more sophisticated over time to
        # dynamically shorten the appearance of a very large active orders list
        cost_alert = yield from self._epic_cost_alert_generator(composition, templateEnv)
        alert_contents.append(cost_alert)

        sleuth_alerts = yield from self._epic_sleuth_alert_generator(composition, templateEnv)
        if len(sleuth_alerts) > 0:
            for sa in sleuth_alerts:
                alert_contents.append(sa)

        ML.PRINT("Generated %s Epic alerts" % len(alert_contents))

    @asyncio.coroutine
    def _epic_cost_alert_generator(self, composition):
        raise NotImplementedError

    @asyncio.coroutine
    def _epic_sleuth_alert_generator(self, composition):
        raise NotImplementedError
