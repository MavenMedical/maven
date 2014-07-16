#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:   This "client_receiver.py" file contains a "Receiver" class very similar to the
#               Maven-side "Receiver" in the data_router.py file. The main difference that upon receiving
#               data, this Receiver does NOT send to RabbitMQ but rather puts the message into a queue to be
#               processed locally on the hospital client server.
#
#************************
#ASSUMES:
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-65
#*************************************************************************
import asyncio
import os
import json
import pickle
import traceback
import maven_config as MC
import maven_logging as ML
import utils.streaming.stream_processor as SP
import utils.streaming.http_responder as HR
import utils.api.pyfhir.pyfhir_generated as FHIR_API
from clientApp.module_webservice.emr_parser import VistaParser
import clientApp.notification_generator.notification_generator as NG
import clientApp.module_webservice.notification_service as NS


class OutgoingToMavenMessageHandler(HR.HTTPReader):

    def __init__(self, configname, wk):
        HR.HTTPReader.__init__(self, configname)

        #TODO - Need to change the EMR Parser based on config
        #self.emr_parser = VistaParser()
        self.wk = wk

    @asyncio.coroutine
    def read_object(self, obj, key):
        """
        param: obj is list of headers, body
        param: key is key
        """
        #header = obj[0]
        try:
            body = obj[1]
            if not len(body):
                self.write_object(HR.wrap_response(HR.BAD_RESPONSE,b'',None), key)
            else:
                message = body.decode()
                composition = yield from self.create_composition(message)
                if not 'MAVEN_TESTING' in os.environ:
                    ML.PRINT(json.dumps(json.dumps([composition, key], default=FHIR_API.jdefault,sort_keys=True),sort_keys=True))

                #self.write_object(json.dumps([composition, key], default=FHIR_API.jdefault,sort_keys=True).encode(), self.wk)
                self.write_object(pickle.dumps([composition, key]), self.wk)

        except:
            try:
                self.write_object(HR.wrap_response(HR.ERROR_RESPONSE, b'', None), key)
                traceback.print_exc()
            except:
                pass


    @asyncio.coroutine
    def create_composition(self, message):
        composition = VistaParser().create_composition(message)
        return composition


class IncomingFromMavenMessageHandler(HR.HTTPWriter):

    def __init__(self, configname, notification_generator, notification_service=None):
        HR.HTTPWriter.__init__(self, configname)
        self.notification_generator = notification_generator
        self.notification_service = notification_service

    @asyncio.coroutine
    def format_response(self, obj, _):

        #TODO - Need to configure the logic below to load from JSON if Client-App is installed WITHIN hospital
        #TODO - infrastructure b/c we cannot send pickles over the wire (but we can if Client-App is in cloud)
        #json_composition = json.loads(obj.decode())
        #composition = FHIR_API.Composition().create_composition_from_json(json_composition)


        composition = pickle.loads(obj)

        ### tom: this has no authentication yet
        #composition.customer_id
        user = composition.get_author_id()
    
        if self.notification_service.send_messages(user, None):
            notifications = yield from self.notification_generator.generate_alert_content(composition, 'web', None)
            self.notification_service.send_messages(user, notifications)
            return (HR.OK_RESPONSE, b'', [], composition.write_key[0])
        else:
            notifications = yield from self.notification_generator.generate_alert_content(composition, 'vista', None)
        
            alert_notification_content = ""

            if notifications is not None and len(notifications) > 0:
                for notification_body in notifications:
                    alert_notification_content += str(notification_body)
                    #alert_notification_content += ""

            ML.DEBUG(json.dumps(composition, default=FHIR_API.jdefault, indent=4))
            ML.DEBUG("NOTIFY HTML BODY: " + alert_notification_content)

            return (HR.OK_RESPONSE, alert_notification_content, [], composition.write_key[0])


def main(loop):
    outgoingtomavenmessagehandler = 'client consumer socket'
    incomingfrommavenmessagehandler = 'client producer socket'
    notificationservicename = 'client notification service'
    clientemrconfig = 'client emr config'

    MavenConfig = {
        outgoingtomavenmessagehandler:
        {
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSERVERSOCKET,
            SP.CONFIG_READERNAME: outgoingtomavenmessagehandler+".Reader",
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETQUERY,
            SP.CONFIG_WRITERNAME: outgoingtomavenmessagehandler+".Writer",
            #SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_IDENTITYPARSER,
            SP.CONFIG_WRITERDYNAMICKEY:1,
            HR.CONFIG_SSLAUTH: None,
        },
        outgoingtomavenmessagehandler+".Reader":
        {
            SP.CONFIG_HOST:'127.0.0.1',
            SP.CONFIG_PORT:8088
        },

        outgoingtomavenmessagehandler+".Writer":
        {
            SP.CONFIG_WRITERKEY:2
        },

        incomingfrommavenmessagehandler:
        {
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETQUERY,
            SP.CONFIG_READERNAME: incomingfrommavenmessagehandler+".Reader",
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETREPLY,
            SP.CONFIG_WRITERNAME: incomingfrommavenmessagehandler+".Writer",
            SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_IDENTITYPARSER,
            SP.CONFIG_WRITERDYNAMICKEY:2,
        },
        incomingfrommavenmessagehandler+".Reader":
        {
            SP.CONFIG_HOST:'127.0.0.1',
            SP.CONFIG_PORT:8090,
            SP.CONFIG_ONDISCONNECT: SP.CONFIGVALUE_DISCONNECTRESTART,
        },

        incomingfrommavenmessagehandler+".Writer":
        {
            #SP.CONFIG_HOST:'127.0.0.1',
            #SP.CONFIG_PORT:12345,
            SP.CONFIG_WRITERKEY:1,
        },

        clientemrconfig:
        {
            NG.EMR_TYPE: "vista",
            NG.EMR_VERSION : "2.0",
            NG.CLIENTAPP_LOCATION: "cloud",
            NG.DEBUG: True,
            NG.COST_ALERT_ICON: "/clientApp"
        },
        notificationservicename:
        {
            SP.CONFIG_HOST: 'localhost',
            SP.CONFIG_PORT: 8091,
            SP.CONFIG_PARSERTIMEOUT: 120,
            NS.CONFIG_QUEUEDELAY: 60,
        },
    }
    MC.MavenConfig = MavenConfig

    notification_generator = NG.NotificationGenerator(clientemrconfig)
    notification_service = NS.NotificationService(notificationservicename)
    sp_consumer = OutgoingToMavenMessageHandler(outgoingtomavenmessagehandler, 2)
    sp_producer = IncomingFromMavenMessageHandler(incomingfrommavenmessagehandler,
                                                  notification_generator,
                                                  notification_service)


    reader = sp_consumer.schedule(loop)
    emr_writer = sp_producer.schedule(loop)
    notification_service.schedule(loop)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        sp_consumer.close()
        sp_producer.close()
        loop.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    main(loop)

