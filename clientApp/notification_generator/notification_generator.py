#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:   This notification_generator.py contains the classes required to generate
#               EMR-specific notification messages, in order to accommodate the available
#               features in each environment (e.g. WorldVistA will utilize Dave's Java Notification
#               system, whereas the Notifications targeting Epic will have to be constructed in a
#               BPA-friendly manner.)
#************************
#ASSUMES:
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-150
#*************************************************************************
import os
import asyncio
import maven_config as MC
import maven_logging as ML
import urllib
import urllib.parse
import math
import jinja2
from jinja2 import Environment, PackageLoader


EMR_TYPE = "emrtype"
EMR_VERSION = "emrversion"
CLIENTAPP_LOCATION = "clientapplocation"
DEBUG = "debug"
COST_ALERT_ICON = "costalerticon"
TEMPLATE_LOAD_PATH = "templateloadpath"


class NotificationGenerator():

    def __init__(self, configname):

        """ Initialize the Notification Generator class, instantiating all of the helper functions
        required to generate an EMR-specific Notification alert

        :param configname: the name of the instance to pull config parameters
        """

        if not configname:
            raise MC.InvalidConfig("Notification Generator needs a config entry")
        try:
            self.configname = configname
            if not configname in MC.MavenConfig:
                raise MC.InvalidConfig(configname+" is not in the MavenConfig map.")
            config = MC.MavenConfig[configname]

            try:
#                self.emrtype = config.get(EMR_TYPE, None)
#                self.emrversion = config.get(EMR_VERSION, None)
                self.DEBUG = config.get(DEBUG, None)
                self.templateEnv = {}
                
                templateLoader = jinja2.FileSystemLoader('/home/devel/maven/clientApp/notification_generator/VistA/templates')
                self.templateEnv['vista'] = jinja2.Environment(loader=templateLoader)

                templateLoader = jinja2.FileSystemLoader('/home/devel/maven/clientApp/notification_generator/Epic/templates')
                self.templateEnv['epic'] = jinja2.Environment(loader=templateLoader)

                templateLoader = jinja2.FileSystemLoader('/home/devel/maven/clientApp/notification_generator/Web/templates')
                self.templateEnv['web'] = jinja2.Environment(loader=templateLoader)

            except KeyError:
                raise MC.InvalidConfig(configname + " did not have sufficient parameters.")

        except Exception as e:
            ML.ERROR("MC.InvalidConfig in "+self.configname)
            raise e

    @asyncio.coroutine
    def generate_alert_content(self, composition, emrtype, emrversion):

        #DEBUG trigger, when set to True, messages get sent, when set to False, empty list gets sent
        if self.DEBUG == True:

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
    @asyncio.coroutine
    def _vista_alert_content_generator(self, composition, templateEnv):

        alert_contents = []

        cost_alert = yield from self._vista_cost_alert_generator(composition, templateEnv)
        alert_contents.append(cost_alert)

        dup_order_alerts = yield from self._vista_duplicate_order_alert_generator(composition, templateEnv)
        if dup_order_alerts is not None:
            for dup_alert in dup_order_alerts:
                alert_contents.append(dup_alert)

        sleuth_alerts = yield from self._vista_sleuth_alert_generator(composition, templateEnv)
        if sleuth_alerts is not None and len(sleuth_alerts) > 0:
            for sa in sleuth_alerts:
                alert_contents.append(sa)

        ML.DEBUG("Generated %s VistA Alerts" % len(alert_contents))

        return alert_contents

    @asyncio.coroutine
    def _vista_cost_alert_generator(self, composition, templateEnv):

        #creates the cost alert html. This may want to become more sophisticated over time to
        #dynamically shorten the appearance of a very large active orders list
        TEMPLATE_FILE = "cost_alert.html"
        TEMPLATE2_FILE = "cost_alert2.html"
        template = templateEnv.get_template(TEMPLATE_FILE)
        template2 = templateEnv.get_template(TEMPLATE2_FILE)
        templateVars = self._generate_cost_alert_template_vars(composition)
        notification_body = template.render(templateVars)
        notification_body += template2.render(templateVars)

        return notification_body

    def _generate_cost_alert_template_vars(self, composition):

        cost_alert = composition.get_alerts(type="cost")

        cost_alert_order_list = cost_alert['cost_details']
        total_cost = cost_alert['total_cost']
        user = composition.get_author_id()
        userAuth = composition.userAuth
        csn = urllib.parse.quote(composition.encounter.get_csn())
        patient_id = composition.subject.get_pat_id()

        templateVars = {"order_list" : cost_alert_order_list,
                        "total_cost" : math.ceil(total_cost),
                        "http_address" : MC.http_addr,
                        "encounter_id" : csn,
                        "patient_id" : patient_id,
                        "user" : user,
                        "user_auth" : userAuth}

        return templateVars

    @asyncio.coroutine
    def _vista_sleuth_alert_generator(self, composition, templateEnv):

        TEMPLATE_FILE = "sleuth_alert.html"
        template_sleuth_alert = templateEnv.get_template( TEMPLATE_FILE )

        sleuth_alert_HTML_contents = []
        user = composition.get_author_id()
        userAuth = composition.userAuth
        csn = urllib.parse.quote(composition.encounter.get_csn())
        patient_id = composition.subject.get_pat_id()

        #composition_alert_section = composition.get_alerts_section()
        CDS_alerts = composition.get_alerts(type="CDS_alerts")

        #check to see if there's anything in the list. Should probably move this to the FHIR api
        #if composition_alert_section is not None and len(composition_alert_section.content) > 0:

        for alert in CDS_alerts['alert_list']:

            templateVars = {"alert_tag_line" : alert.short_title,
                            "alert_description" : alert.description,
                            "http_address" : MC.http_addr,
                            "encounter_id" : csn,
                            "patient_id" : patient_id,
                            "evi_id": alert.CDS_rule,
                            "user" : user,
                            "user_auth" : userAuth}

            notification_body = template_sleuth_alert.render(templateVars)
            sleuth_alert_HTML_contents.append(notification_body)

            return sleuth_alert_HTML_contents

    @asyncio.coroutine
    def _vista_duplicate_order_alert_generator(self, composition, templateEnv):

        TEMPLATE_FILE = "duplicate_order_alert.html"
        template_dup_order_alert = templateEnv.get_template(TEMPLATE_FILE)
        duplicate_order_alert_contents = []

        user = composition.get_author_id()
        userAuth = composition.userAuth
        csn = urllib.parse.quote(composition.encounter.get_csn())
        patient_id = composition.subject.get_pat_id()

        dup_order_alert_dict = composition.get_alerts(type="dup_orders")
        for alert in dup_order_alert_dict['alert_list']:

            templateVars = {"alert_tag_line" : alert.short_title,
                            "alert_description" : alert.description,
                            "http_address" : MC.http_addr,
                            "encounter_id" : csn,
                            "patient_id" : patient_id,
                            "user" : user,
                            "user_auth" : userAuth,
                            "related_observations": alert.related_observations}

            notification_body = template_dup_order_alert.render(templateVars)
            duplicate_order_alert_contents.append(notification_body)

            return duplicate_order_alert_contents


    ################################################################################################
    ################################################################################################
    # Start Web Alert Generator Components
    ################################################################################################
    @asyncio.coroutine
    def _web_alert_content_generator(self, composition, templateEnv):
        alert_contents = []

        #creates the cost alert html. This may want to become more sophisticated over time to
        #dynamically shorten the appearance of a very large active orders list
        cost_alert = yield from self._web_cost_alert_generator(composition, templateEnv)
        alert_contents.append(cost_alert)

        sleuth_alerts = yield from self._web_sleuth_alert_generator(composition, templateEnv)
        if sleuth_alerts is not None and len(sleuth_alerts) > 0:
            for sa in sleuth_alerts:
                alert_contents.append(sa)

        ML.DEBUG("Generated %s Web Alerts" % len(alert_contents))

        return alert_contents

    @asyncio.coroutine
    def _web_cost_alert_generator(self, composition, templateEnv):

        TEMPLATE_FILE = "cost_alert.html"
        TEMPLATE2_FILE = "cost_alert2.html"
        template = templateEnv.get_template(TEMPLATE_FILE)
        template2 = templateEnv.get_template(TEMPLATE2_FILE)
        cost_alert = composition.get_alerts(type="cost")
        templateVars = self._generate_cost_alert_template_vars(composition)
        notification_body = template.render(templateVars)

        return notification_body

    @asyncio.coroutine
    def _web_sleuth_alert_generator(self, composition, templateEnv):

        TEMPLATE_FILE = "sleuth_alert.html"
        template_sleuth_alert = templateEnv.get_template( TEMPLATE_FILE )


        sleuth_alert_HTML_contents = []
        user = composition.get_author_id()
        userAuth = composition.userAuth
        csn = urllib.parse.quote(composition.encounter.get_csn())
        patient_id = composition.subject.get_pat_id()

        #composition_alert_section = composition.get_alerts_section()
        CDS_alerts = composition.get_alerts(type="CDS_alerts")

        #check to see if there's anything in the list. Should probably move this to the FHIR api
        #if composition_alert_section is not None and len(composition_alert_section.content) > 0:

        for alert in CDS_alerts['alert_list']:

            templateVars = {"alert_tag_line" : alert.short_title,
                            "alert_description" : alert.description,
                            "http_address" : MC.http_addr,
                            "encounter_id" : csn,
                            "patient_id" : patient_id,
                            "evi_id": alert.CDS_rule,
                            "user" : user,
                            "user_auth" : userAuth}

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

        #creates the cost alert html. This may want to become more sophisticated over time to
        #dynamically shorten the appearance of a very large active orders list
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
