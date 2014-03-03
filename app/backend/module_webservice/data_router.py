#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:   This file creates a an asynchronous listening server for incoming messages.
#
#************************
#ASSUMES:
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-1
#*************************************************************************
import app.utils.streaming.stream_processor as SP
from xml.etree import ElementTree as ET
import maven_config as MC
import maven_logging as ML
import asyncio
import uuid
import argparse


outgoingmessagehandler = 'responder socket'
incomingmessagehandler = 'receiver socket'



MavenConfig = {
    outgoingmessagehandler:
    {
        SP.CONFIG_READERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
        SP.CONFIG_READERNAME: outgoingmessagehandler+".Reader",
        SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOCLIENTSOCKET,
        SP.CONFIG_WRITERNAME: outgoingmessagehandler+".Writer",
        SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_UNPICKLEPARSER
    },
    outgoingmessagehandler+".Reader":
    {
        SP.CONFIG_HOST:'localhost',
        SP.CONFIG_QUEUE:'incoming_work_queue',
        SP.CONFIG_EXCHANGE:'maven_exchange',
        SP.CONFIG_KEY:'incoming'
    },

    outgoingmessagehandler+".Writer":
    {
        SP.CONFIG_HOST:'127.0.0.1',
        SP.CONFIG_PORT:7888
    },

    incomingmessagehandler:
    {
        SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSERVERSOCKET,
        SP.CONFIG_READERNAME: incomingmessagehandler+".Reader",
        SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
        SP.CONFIG_WRITERNAME: incomingmessagehandler+".Writer",
        SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_IDENTITYPARSER
    },
    incomingmessagehandler+".Reader":
    {
        SP.CONFIG_HOST:'127.0.0.1',
        SP.CONFIG_PORT:8808
    },

    incomingmessagehandler+".Writer":
    {
        SP.CONFIG_HOST:'localhost',
        SP.CONFIG_QUEUE:'incoming_work_queue',
        SP.CONFIG_EXCHANGE:'maven_exchange',
        SP.CONFIG_KEY:'incoming'
    },
}
MC.MavenConfig = MavenConfig

ARGS = argparse.ArgumentParser(description='Maven Client Receiver Configs.')
ARGS.add_argument(
    '--emr', action='store', dest='emr',
    default='Epic', help='EMR Name')
args = ARGS.parse_args()


class OutgoingMessageHandler(SP.StreamProcessor):

    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)
        self.master_list = ['', '', '', '', '']
        self.object_manager = []

    @asyncio.coroutine
    def read_object(self, obj, key):
        #self.write_object(obj.encode())
        yield from self.route_object(obj, key)

    @asyncio.coroutine
    def route_object(self, obj, key):
        message = obj
        message_root = ET.fromstring(message)
        emr_namespace = "urn:" + args.emr
        if emr_namespace in message_root.tag:
            self.write_object(obj.encode(), key)


class IncomingMessageHandler(SP.StreamProcessor):

    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)
        self.master_list = ['', '', '', '', '']
        self.object_manager = []

    @asyncio.coroutine
    def read_object(self, obj, key):
        yield from self.route_object(obj, key)

    @asyncio.coroutine
    def route_object(self, obj, key):
        orders = []
        message = obj.decode()
        message_root = ET.fromstring(message)
        emr_namespace = "urn:" + args.emr
        NS = message_root.tag.split("}")[0].strip("{")
        if emr_namespace in NS:
            orders_array = message_root.find("{%s}Charges" %NS)
            for order in orders_array.findall("{%s}Charge" %NS):
                    order_id = order.find("{%s}ID" %NS)
                    print(order_id.text)
            self.write_object(obj.decode())


def main():
    loop = asyncio.get_event_loop()
    sp_producer = OutgoingMessageHandler(outgoingmessagehandler)
    sp_consumer = IncomingMessageHandler(incomingmessagehandler)
    reader = sp_consumer.schedule(loop)
    emitter = sp_producer.schedule(loop)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        sp_consumer.close()
        sp_producer.close()
        loop.close()


if __name__ == '__main__':
    main()
