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
from xml.etree import ElementTree as ET
import maven_config as MC
import maven_logging as ML
import asyncio
import json
import uuid
import argparse
import pickle
from clientApp.module_webservice.emr_parser import VistaParser
import clientApp.api.api as api


ARGS = argparse.ArgumentParser(description='Maven Client Receiver Configs.')
ARGS.add_argument(
    '--emr', action='store', dest='emr',
    default='Epic', help='EMR Name')
args = ARGS.parse_args()


class OutgoingToMavenMessageHandler(SP.StreamProcessor):

    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)


    @asyncio.coroutine
    def read_object(self, obj, _):
        message = obj.decode()
        composition = yield from self.create_composition(message)
        #ML.PRINT(json.dumps(composition, default=api.jdefault, indent=4))
        self.write_object(json.dumps(composition, default=api.jdefault).encode())

    @asyncio.coroutine
    def create_composition(self, message):
        #message_root = ET.fromstring(message)
        composition = VistaParser().create_composition(message)
        return composition


class IncomingFromMavenMessageHandler(SP.StreamProcessor):

    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)
        self.master_list = ['', '', '', '', '']
        self.object_manager = []

    @asyncio.coroutine
    def read_object(self, obj, key):
        self.write_object(obj)
        ML.PRINT('Message was successfully sent around the Maven Cloud loop!')


def main(loop):
    outgoingtomavenmessagehandler = 'client consumer socket'
    incomingfrommavenmessagehandler = 'client producer socket'

    MavenConfig = {
        outgoingtomavenmessagehandler:
        {
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSERVERSOCKET,
            SP.CONFIG_READERNAME: outgoingtomavenmessagehandler+".Reader",
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETQUERY,
            SP.CONFIG_WRITERNAME: outgoingtomavenmessagehandler+".Writer",
            SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_IDENTITYPARSER,
            SP.CONFIG_DEFAULTWRITEKEY:1,
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
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOCLIENTSOCKET,
            SP.CONFIG_WRITERNAME: incomingfrommavenmessagehandler+".Writer",
            SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_IDENTITYPARSER,
            SP.CONFIG_WRITERDYNAMICKEY:1,
        },
        incomingfrommavenmessagehandler+".Reader":
        {
            SP.CONFIG_HOST:'127.0.0.1',
            SP.CONFIG_PORT:8088
        },

        incomingfrommavenmessagehandler+".Writer":
        {
            SP.CONFIG_HOST:'127.0.0.1',
            SP.CONFIG_PORT:12347
        },

    }
    MC.MavenConfig = MavenConfig

    sp_consumer = OutgoingToMavenMessageHandler(outgoingtomavenmessagehandler)
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

