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
import json
import pickle
import utils.streaming.stream_processor as SP
import asyncio
import utils.streaming.http_responder as HR
import maven_config as MC
import maven_logging as ML
from clientApp.module_webservice.emr_parser import VistaParser
import utils.api.fhir as api
import clientApp.module_webservice.notification_generator as NG
import os


class OutgoingToMavenMessageHandler(HR.HTTPReader):

    def __init__(self, configname, wk):
        HR.HTTPReader.__init__(self, configname)
        self.wk = wk

    @asyncio.coroutine
    def read_object(self, obj, key):
        """
        param: obj is list of headers, body
        param: key is key
        """
        header = obj[0]
        try:
            self.sslauth(header.get_headers())
            body = obj[1]
            if not len(body):
                self.write_object(HR.wrap_response(HR.BAD_RESPONSE,b'',None), key)
            else:
                message = body.decode()
                composition = yield from self.create_composition(message)
                if not 'MAVEN_TESTING' in os.environ:
                    ML.PRINT(json.dumps(json.dumps([composition, key], default=api.jdefault,sort_keys=True),sort_keys=True))
                self.write_object(json.dumps([composition, key], default=api.jdefault,sort_keys=True).encode(), self.wk)
        except HR.UnauthorizedRequest:
            try:
                self.write_object(HR.wrap_response(HR.UNAUTHORIZED_RESPONSE,b'',None), key)
            except:
                pass

        except:
            try:
                self.write_object(HR.wrap_response(HR.ERROR_RESPONSE, b'', None), key)
            except:
                pass


    @asyncio.coroutine
    def create_composition(self, message):
        composition = VistaParser().create_composition(message)
        return composition


class IncomingFromMavenMessageHandler(HR.HTTPWriter):

    def __init__(self, configname, notification_generator):
        HR.HTTPWriter.__init__(self, configname)
        self.notification_generator = notification_generator

    @asyncio.coroutine
    def format_response(self, obj, _):

        #json_composition = json.loads(obj.decode())
        #composition = api.Composition().create_composition_from_json(json_composition)
        composition = pickle.loads(obj)
        notifications = yield from self.notification_generator.generate_alert_content(composition)

        alert_notification_content = ""

        if notifications is not None and len(notifications) > 0:
            for notification_body in notifications:
                alert_notification_content += str(notification_body)

        ML.DEBUG(json.dumps(composition, default=api.jdefault, indent=4))
        ML.DEBUG("NOTIFY HTML BODY: " + alert_notification_content)

        return (HR.OK_RESPONSE, alert_notification_content, [], composition.maven_route_key[0])


def main(loop):
    outgoingtomavenmessagehandler = 'client consumer socket'
    incomingfrommavenmessagehandler = 'client producer socket'
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
        },

    }
    MC.MavenConfig = MavenConfig

    notification_generator = NG.NotificationGenerator(clientemrconfig)
    sp_consumer = OutgoingToMavenMessageHandler(outgoingtomavenmessagehandler, 2)
    sp_producer = IncomingFromMavenMessageHandler(incomingfrommavenmessagehandler, notification_generator)


    reader = sp_consumer.schedule(loop)
    emr_writer = sp_producer.schedule(loop)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        sp_consumer.close()
        sp_producer.close()
        loop.close()


if __name__ == '__main__':
    ML.DEBUG = ML.stdout_log
    loop = asyncio.get_event_loop()
    main(loop)

