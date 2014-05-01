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
import asyncio
import maven_config as MC
import maven_logging as ML
import urllib
import urllib.parse


EMR_TYPE = "emrtype"
EMR_VERSION = "emrversion"
CLIENTAPP_LOCATION = "clientapplocation"


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

            except KeyError:
                raise MC.InvalidConfig(configname + " did not have sufficient parameters.")

        except Exception as e:
            ML.ERROR("MC.InvalidConfig in "+self.configname)
            raise e

    @asyncio.coroutine
    def generate_alert_content(self, composition):
        if self.emrtype == 'vista':
            return self._vista_alert_content_generator(composition)

        elif self.emrtype == 'epic' and self.emrversion == '2010' or '2012':
            return self._epic_cost_HTML_content_generator(composition)

    @asyncio.coroutine
    def _vista_alert_content_generator(self, composition):
        alert_contents = []

        #creates the cost alert html. This may want to become more sophisticated over time to shorten the appearance of a very large active orders list
        cost_alert = yield from self._vista_cost_alert_generator(composition)
        alert_contents.append(cost_alert)

        sleuth_alerts = yield from self._vista_sleuth_alert_generator(composition)
        if len(sleuth_alerts) > 0:
            for sa in sleuth_alerts:
                alert_contents.append(sa)

        ML.PRINT("Generated %s alert HTMLs" % len(alert_contents))

        return alert_contents



    @asyncio.coroutine
    def _vista_cost_alert_generator(self, composition):
        notification_body = ""
        notification_content = ""
        total_cost = 0.0
        user = composition.user
        userAuth = composition.userAuth

        csn = urllib.parse.quote(composition.encounter.get_csn())
        patient_id = composition.subject.get_pat_id()

        cost_breakdown = composition.get_encounter_cost_breakdown()

        if cost_breakdown is not None:
            for cost in cost_breakdown.content:
                total_cost += cost[1]
                notification_content += ("%s: $%s<br>" % (cost[0], cost[1]))
            print(total_cost)

        notification_body = ("<html><body bgcolor=#FFFFFF style='font-family: Arial; color: #444; word-spacing: normal; text-align: left; letter-spacing: 0; font-size: 104%%;'><table><col width=32px><col width=30%%><col width=10%%><col width=60%%><tr><td valign='top'><img src={{IMGLOGO}} /></td><td valign='top'><a href='%s/#/episode/%s/patient/%s/login/%s/%s'><b>Encounter Cost Alert</b></a><br/>This Encounter Costs<br/>$%s</td><td></td><td valign='top' style='font-family: Arial; color: #444; word-spacing: normal; text-align: left; letter-spacing: 0; font-size: 104%%;'>%s</td></body></html>" % (MC.http_addr, csn, patient_id, user, userAuth, round(total_cost,2), notification_content))
        return notification_body

    @asyncio.coroutine
    def _vista_sleuth_alert_generator(self, composition):
        sleuth_alert_HTML_contents = []
        notification_body = ""
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

                        notification_body = ("<html><body bgcolor=#FFFFFF style='font-family: Arial; color: #444; word-spacing: normal; text-align: left; letter-spacing: 0; font-size: 104%%;'><table><col width=32px><col width=30%%><col width=10%%><col width=60%%><tr><td valign='top'><img src={{IMGLOGO}} /></td><td valign='top'><a href='%s/#/episode/%s/patient/%s/login/%s/%s'><b>Maven Sleuth Alert</b></a><br/>%s<br/>$%s</td><td></td><td valign='top' style='font-family: Arial; color: #444; word-spacing: normal; text-align: left; letter-spacing: 0; font-size: 104%%;'>%s</td></body></html>" % (MC.http_addr, csn, patient_id, user, userAuth, alert.short_title, round(total_cost,2), notification_content))
                        sleuth_alert_HTML_contents.append(notification_body)

            return sleuth_alert_HTML_contents



    @asyncio.coroutine
    def _epic_cost_HTML_content_generator(self, composition):
        raise NotImplementedError