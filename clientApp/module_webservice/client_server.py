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
import app.utils.streaming.stream_processor as SP
import app.utils.streaming.http_responder as HR
import maven_config as MC
import maven_logging as ML
import asyncio
import json
import argparse
from clientApp.module_webservice.emr_parser import VistaParser
import clientApp.api.api as api
import pickle


ARGS = argparse.ArgumentParser(description='Maven Client Receiver Configs.')
ARGS.add_argument(
    '--emr', action='store', dest='emr',
    default='Epic', help='EMR Name')
args = ARGS.parse_args()


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
        body = obj[1]
        message = body.decode()
        composition = yield from self.create_composition(message)
        ML.PRINT(json.dumps(json.dumps([composition, key], default=api.jdefault)))
        self.write_object(json.dumps([composition, key], default=api.jdefault).encode(), self.wk)

    @asyncio.coroutine
    def create_composition(self, message):
        #message_root = ET.fromstring(message)
        composition = VistaParser().create_composition(message)
        return composition


class IncomingFromMavenMessageHandler(HR.HTTPWriter):

    def __init__(self, configname):
        HR.HTTPWriter.__init__(self, configname)
        #self.wk = wk

    @asyncio.coroutine
    def format_response(self, obj, _):
        #json_composition = json.loads(obj.decode())
        #composition = api.Composition().create_composition_from_json(json_composition)
        composition = pickle.loads(obj)
        #print(json.dumps(composition, default=api.jdefault, indent=4))
        notification_body = yield from self.generate_notification_html(composition)
        ML.DEBUG("NOTIFY HTML BODY: " + notification_body)
        ML.PRINT('Message was successfully sent around the Maven Cloud loop!')
        return (HR.OK_RESPONSE, notification_body, [], composition.maven_route_key[0])


    @asyncio.coroutine
    def generate_notification_html(self, composition):
        notification_body = ""
        notification_content = ""
        total_cost = 0.0
        for sec in composition.section:
            if sec.title == "Encounter Cost Breakdown":
                for cost in sec.content:
                    total_cost += cost[1]
                    notification_content += ("%s: $%s<br>" % (cost[0], cost[1]))
                print(total_cost)

        notification_body = ("<html><body bgcolor=#FFFFFF style='font-family: Arial; color: #444; word-spacing: normal; text-align: left; letter-spacing: 0; font-size: 104%%;'><table><col width=32px><col width=30%%><col width=10%%><col width=60%%><tr><td valign='top'><img src={{IMGLOGO}} /></td><td valign='top'><a href='http://mavenmedical.net'><b>Encounter Cost Alert</b></a><br/>This Encounter Costs<br/>$%s</td><td></td><td valign='top' style='font-family: Arial; color: #444; word-spacing: normal; text-align: left; letter-spacing: 0; font-size: 104%%;'>%s</td></body></html>" % (str(total_cost), notification_content))
        return notification_body

def main(loop):
    ML.DEBUG = ML.stdout_log
    outgoingtomavenmessagehandler = 'client consumer socket'
    incomingfrommavenmessagehandler = 'client producer socket'

    MavenConfig = {
        outgoingtomavenmessagehandler:
        {
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSERVERSOCKET,
            SP.CONFIG_READERNAME: outgoingtomavenmessagehandler+".Reader",
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETQUERY,
            SP.CONFIG_WRITERNAME: outgoingtomavenmessagehandler+".Writer",
            #SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_IDENTITYPARSER,
            SP.CONFIG_WRITERDYNAMICKEY:1,
        },
        outgoingtomavenmessagehandler+".Reader":
        {
            SP.CONFIG_HOST:'127.0.0.1',
            SP.CONFIG_PORT:12345
        },

        outgoingtomavenmessagehandler+".Writer":
        {
            SP.CONFIG_WRITERKEY:1
        },

        incomingfrommavenmessagehandler:
        {
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETQUERY,
            SP.CONFIG_READERNAME: incomingfrommavenmessagehandler+".Reader",
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETREPLY,
            SP.CONFIG_WRITERNAME: incomingfrommavenmessagehandler+".Writer",
            SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_IDENTITYPARSER,
            #SP.CONFIG_WRITERDYNAMICKEY:2,
        },
        incomingfrommavenmessagehandler+".Reader":
        {
            SP.CONFIG_HOST:'127.0.0.1',
            SP.CONFIG_PORT:8088
        },

        incomingfrommavenmessagehandler+".Writer":
        {
            SP.CONFIG_HOST:'127.0.0.1',
            SP.CONFIG_PORT:12347,
            #SP.CONFIG_WRITERDYNAMICKEY:1,
        },

    }
    MC.MavenConfig = MavenConfig

    sp_consumer = OutgoingToMavenMessageHandler(outgoingtomavenmessagehandler, 2)
    sp_producer = IncomingFromMavenMessageHandler(incomingfrommavenmessagehandler)

    reader = sp_consumer.schedule(loop)
    emr_writer = sp_producer.schedule(loop)

    try:
        loop.run_forever()

    except KeyboardInterrupt:
        sp_consumer.close()
        sp_producer.close()
        loop.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    main(loop)

