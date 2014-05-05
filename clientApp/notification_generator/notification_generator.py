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
                self.emrtype = config.get(EMR_TYPE, None)
                self.emrversion = config.get(EMR_VERSION, None)
                self.DEBUG = config.get(DEBUG, None)

            except KeyError:
                raise MC.InvalidConfig(configname + " did not have sufficient parameters.")

        except Exception as e:
            ML.ERROR("MC.InvalidConfig in "+self.configname)
            raise e

    @asyncio.coroutine
    def generate_alert_content(self, composition):

        #DEBUG trigger, when set to True, messages get sent, when set to False, empty list gets sent
        if self.DEBUG == True:

            if self.emrtype == 'vista':
                return self._vista_alert_content_generator(composition)

            elif self.emrtype == 'epic' and self.emrversion == '2010' or '2012':
                return self._epic_alert_content_generator(composition)
        else:
            return []


    ################################################################################################
    ################################################################################################
    # Start Vista Alert Generator Components
    ################################################################################################
    @asyncio.coroutine
    def _vista_alert_content_generator(self, composition):
        alert_contents = []

        #creates the cost alert html. This may want to become more sophisticated over time to
        #dynamically shorten the appearance of a very large active orders list
        cost_alert = yield from self._vista_cost_alert_generator(composition)
        alert_contents.append(cost_alert)

        sleuth_alerts = yield from self._vista_sleuth_alert_generator(composition)
        if len(sleuth_alerts) > 0:
            for sa in sleuth_alerts:
                alert_contents.append(sa)

        ML.PRINT("Generated %s VistA Alerts" % len(alert_contents))

        return alert_contents

    @asyncio.coroutine
    def _vista_cost_alert_generator(self, composition):

        templateLoader = jinja2.FileSystemLoader('/home/devel/maven/clientApp/notification_generator/VistA/templates')
        templateEnv = jinja2.Environment(loader=templateLoader)
        TEMPLATE_FILE = "cost_alert.html"
        TEMPLATE2_FILE = "cost_alert2.html"
        template = templateEnv.get_template( TEMPLATE_FILE )
        template2 = templateEnv.get_template( TEMPLATE2_FILE )

        total_cost = 0.0
        user = composition.user
        userAuth = composition.userAuth

        csn = urllib.parse.quote(composition.encounter.get_csn())
        patient_id = composition.subject.get_pat_id()

        cost_breakdown = composition.get_encounter_cost_breakdown()

        cost_alert_order_list = []

        if cost_breakdown is not None:
            for cost in cost_breakdown.content:
                total_cost += math.ceil(cost[1])
                cost_alert_order_list.append((cost[0], math.ceil(cost[1])))

        templateVars = {"order_list" : cost_alert_order_list,
                        "total_cost" : math.ceil(total_cost),
                        "http_address" : MC.http_addr,
                        "encounter_id" : csn,
                        "patient_id" : patient_id,
                        "user" : user,
                        "user_auth" : userAuth}

        notification_body = template.render(templateVars)

        notification_body += template2.render(templateVars)

        return notification_body

    @asyncio.coroutine
    def _vista_sleuth_alert_generator(self, composition):
        sleuth_alert_HTML_contents = []
        notification_content = ""
        total_cost = 0.0
        user = composition.user
        userAuth = composition.userAuth

        csn = urllib.parse.quote(composition.encounter.get_csn())
        patient_id = composition.subject.get_pat_id()

        composition_alert_section = composition.get_alerts_section()

        #check to see if there's anything in the list. Should probably move this to the FHIR api
        if len(composition_alert_section.content) > 0:
            for alert_group in composition_alert_section.content:
                for alert_list in alert_group.values():
                    for alert in alert_list:
                        print(alert.short_title)

                        #TODO - The HTML below has hard-coded locations for Notification Icon. Need to move to config.
                        notification_body = ("<html><body bgcolor=#FFFFFF style='font-family: Arial; color: #444; word-spacing: normal; text-align: left; letter-spacing: 0; font-size: 104%%;'><table><col width=32px><col width=30%%><col width=10%%><col width=60%%><tr><td valign='top'><img src='/home/devel/maven/clientApp/notification_generator/img/evidence-28x35px.png'/></td><td valign='top'><a href='%s/#/episode/%s/patient/%s/login/%s/%s'><b>Maven Sleuth Alert</b></a><br/>%s<br/>$%s</td><td></td><td valign='top' style='font-family: Arial; color: #444; word-spacing: normal; text-align: left; letter-spacing: 0; font-size: 104%%;'>%s</td></body></html>" % (MC.http_addr, csn, patient_id, user, userAuth, alert.short_title, round(total_cost,2), notification_content))
                        sleuth_alert_HTML_contents.append(notification_body)

            return sleuth_alert_HTML_contents


    ################################################################################################
    ################################################################################################
    # Start Epic Alert Generator Components
    ################################################################################################
    @asyncio.coroutine
    def _epic_alert_content_generator(self, composition):
        alert_contents = []

        #creates the cost alert html. This may want to become more sophisticated over time to
        #dynamically shorten the appearance of a very large active orders list
        cost_alert = yield from self._epic_cost_alert_generator(composition)
        alert_contents.append(cost_alert)

        sleuth_alerts = yield from self._epic_sleuth_alert_generator(composition)
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