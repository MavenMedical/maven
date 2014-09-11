# *************************************************************************
# Copyright (c) 2014 - Maven Medical
# ************************
# AUTHOR:
__author__ = 'Yuki Uchino'
# ************************
# DESCRIPTION:
#
#
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
import json
import pickle
import maven_config as MC
import maven_logging as ML
import utils.streaming.stream_processor as SP
import utils.streaming.http_responder as HR
import utils.api.pyfhir.pyfhir_generated as FHIR_API
import clientApp.notification_generator.notification_generator as NG
import clientApp.webservice.notification_service as NS
from clientApp.allscripts.allscripts_scheduler import scheduler, CONFIG_SLEEPINTERVAL
import utils.web_client.allscripts_http_client as AHC


CONFIG_API = 'api'
CLIENT_SERVER_LOG = ML.get_logger('clientApp.webservice.allscripts_server')


class IncomingFromMavenMessageHandler(HR.HTTPWriter):

    def __init__(self, configname, notification_generator, notification_fn=None):
        HR.HTTPWriter.__init__(self, configname)
        self.notification_generator = notification_generator
        self.notification_fn = notification_fn

    @asyncio.coroutine
    def format_response(self, obj, _):

        # TODO - Need to configure the logic below to load from JSON if
        #        Client-App is installed WITHIN hospital
        # TODO - infrastructure b/c we cannot send pickles over the wire
        #        (but we can if Client-App is in cloud)
        # json_composition = json.loads(obj.decode())
        # composition = FHIR_API.Composition().create_composition_from_json(json_composition)

        composition = pickle.loads(obj)
        CLIENT_SERVER_LOG.debug(("Received Composition Object from the Maven backend "
                                 + "engine: ID = %s" % composition.id))

        # ## tom: this has no authentication yet
        # composition.customer_id
        user = composition.author.get_provider_id()
        customer = str(composition.customer_id)
        msg = yield from self.notification_generator.generate_alert_content(composition,
                                                                            'web', None)
        CLIENT_SERVER_LOG.debug(("Generated Message content: %s" % msg))

        mobile_msg = [{'TEXT': 'New Pathway', 'LINK': m} for m in msg]
        self.notification_fn('mobile_' + user, customer, mobile_msg)

        if self.notification_fn(user, customer, msg):
            CLIENT_SERVER_LOG.debug(("Successfully sent msg to: %s" % composition.write_key[0]))
            return (HR.OK_RESPONSE, b'', [], composition.write_key[0])
        else:
            notifications = msg

            alert_notification_content = ""

            if notifications is not None and len(notifications) > 0:
                for notification_body in notifications:
                    alert_notification_content += str(notification_body)
                    # alert_notification_content += ""

            ML.DEBUG(json.dumps(composition, default=FHIR_API.jdefault, indent=4))
            ML.DEBUG("NOTIFY HTML BODY: " + alert_notification_content)

            return (HR.OK_RESPONSE, alert_notification_content, [], composition.write_key[0])


def main(loop):
    outgoingtomavenmessagehandler = 'client consumer socket'
    incomingfrommavenmessagehandler = 'client producer socket'
    notificationservicename = 'client notification service'
    clientemrconfig = 'client emr config'
    allscriptsscheduler = 'allscripts_demo'
    customerid = 'customer_id'

    from utils.database.database import AsyncConnectionPool
    import utils.database.web_persistence as WP
    import app.backend.webservices.authentication as AU
    from utils.enums import USER_ROLES

    MavenConfig = {
        outgoingtomavenmessagehandler:
        {
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_EXPLICIT,
            SP.CONFIG_READERNAME: outgoingtomavenmessagehandler + "Reader",
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETQUERY,
            SP.CONFIG_WRITERNAME: outgoingtomavenmessagehandler + ".Writer",
            # SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_IDENTITYPARSER,
        },

        outgoingtomavenmessagehandler + ".Writer":
        {
            SP.CONFIG_WRITERKEY: 2
        },

        incomingfrommavenmessagehandler:
        {
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETQUERY,
            SP.CONFIG_READERNAME: incomingfrommavenmessagehandler + ".Reader",
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_EXPLICIT,
            SP.CONFIG_WRITERNAME: incomingfrommavenmessagehandler + ".Writer",
            SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_IDENTITYPARSER,
            SP.CONFIG_WRITERDYNAMICKEY: 2,
        },
        incomingfrommavenmessagehandler + ".Reader":
        {
            SP.CONFIG_HOST: '127.0.0.1',
            SP.CONFIG_PORT: 8090,
            SP.CONFIG_ONDISCONNECT: SP.CONFIGVALUE_DISCONNECTRESTART,
        },

        clientemrconfig:
        {
            NG.EMR_TYPE: "allscripts",
            NG.EMR_VERSION: "14.0",
            NG.CLIENTAPP_LOCATION: "cloud",
            NG.DEBUG: True,
            NG.COST_ALERT_ICON: "/clientApp",
            NG.MAX_MSG_LOAD: 3
        },
        notificationservicename:
        {
            SP.CONFIG_HOST: 'localhost',
            SP.CONFIG_PORT: 8092,
            SP.CONFIG_PARSERTIMEOUT: 120,
            NS.CONFIG_QUEUEDELAY: 45,
            "persistence": "persistence layer",
            AU.CONFIG_SPECIFICROLE: USER_ROLES.notification.value,
            AU.CONFIG_OAUTH: True,
        },
        'persistence layer': {WP.CONFIG_DATABASE: 'webservices conn pool', },
        'webservices conn pool':
        {
            AsyncConnectionPool.CONFIG_CONNECTION_STRING: MC.dbconnection,
            AsyncConnectionPool.CONFIG_MIN_CONNECTIONS: 4,
            AsyncConnectionPool.CONFIG_MAX_CONNECTIONS: 8
        },
        allscriptsscheduler:
        {
            AHC.http.CONFIG_BASEURL: 'http://192.237.182.238/Unity/UnityService.svc',
            AHC.http.CONFIG_OTHERHEADERS: {'Content-Type': 'application/json'},
            AHC.CONFIG_APPNAME: 'MavenPathways.TestApp',
            AHC.CONFIG_APPUSERNAME: 'MavenPathways',
            AHC.CONFIG_APPPASSWORD: 'MavenPathways123!!',
        },
        'scheduler':
        {
            CONFIG_API: 'allscripts_demo',
            CONFIG_SLEEPINTERVAL: 30,
            "SP": outgoingtomavenmessagehandler
        },
        customerid: 5
    }
    MC.MavenConfig.update(MavenConfig)

    # Instantiate the (allscripts_server.py --> data_router.py) writer
    # and services and add to event loop

    notification_generator = NG.NotificationGenerator(clientemrconfig)
    notification_service, notification_fn = NS.standalone_notification_server(notificationservicename)
    sp_producer = IncomingFromMavenMessageHandler(incomingfrommavenmessagehandler,
                                                  notification_generator,
                                                  notification_fn)

    # Instantiate the allscripts_scheduler.py polling mechanism
    allscripts_scheduler = scheduler('scheduler')
    sp_producer.schedule(loop)
    notification_service.schedule(loop)

    try:
        loop.run_until_complete(allscripts_scheduler.get_updated_schedule())
        loop.run_forever()
    except KeyboardInterrupt:
        sp_producer.close()
        loop.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    main(loop)
