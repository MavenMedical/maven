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
from app.backend.module_rule_engine import order_object as OO
import pickle




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
    def read_object(self, obj, _):
        yield from self.route_object(obj)

    @asyncio.coroutine
    def route_object(self, obj):
        message = obj
        message_root = ET.fromstring(message)
        emr_namespace = "urn:" + args.emr
        if emr_namespace in message_root.tag:
            self.write_object(obj)


class IncomingMessageHandler(SP.StreamProcessor):

    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)
        self.master_list = ['', '', '', '', '']
        self.object_manager = []

    @asyncio.coroutine
    def read_object(self, obj, _):
        orders = []
        message = obj[0].decode()
        message_root = ET.fromstring(message)
        emr_namespace = "urn:" + args.emr
        NS = message_root.tag.split("}")[0].strip("{")
        if emr_namespace in NS:
            orders_array = message_root.find("{%s}Charges" %NS)
            orders_basket = OO.OrderBasket(key=obj[1])
            for order in orders_array.findall("{%s}Charge" %NS):
                order_id = order.find("{%s}ID" %NS).text
                order_params = [str(order_id), 15545, 342, [4,3], '4']
                orders_basket.add_order(OO.OrderObject(order_params))
            self.write_object(pickle.dumps(orders_basket))


def main(loop):

    outgoingtohospitalsmessagehandler = 'responder socket'
    incomingtomavenmessagehandler = 'receiver socket'



    MavenConfig = {
        outgoingtohospitalsmessagehandler:
        {
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
            SP.CONFIG_READERNAME: outgoingtohospitalsmessagehandler+".Reader",
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETREPLY,
            SP.CONFIG_WRITERNAME: outgoingtohospitalsmessagehandler+".Writer",
            SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_UNPICKLEPARSER,
            SP.CONFIG_WRITERDYNAMICKEY:1,
        },
        outgoingtohospitalsmessagehandler+".Reader":
        {
            SP.CONFIG_HOST:'localhost',
            SP.CONFIG_QUEUE:'incoming_work_queue',
            SP.CONFIG_EXCHANGE:'maven_exchange',
            SP.CONFIG_KEY:'incoming'
        },

        outgoingtohospitalsmessagehandler+".Writer":
        {
            SP.CONFIG_WRITERKEY:1
        },

        incomingtomavenmessagehandler:
        {
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSERVERSOCKET,
            SP.CONFIG_READERNAME: incomingtomavenmessagehandler+".Reader",
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_THREADEDRABBIT,
            SP.CONFIG_WRITERNAME: incomingtomavenmessagehandler+".Writer",
            SP.CONFIG_PARSERTYPE: SP.CONFIGVALUE_UNPICKLEPARSER,
        },
        incomingtomavenmessagehandler+".Reader":
        {
            SP.CONFIG_HOST:'127.0.0.1',
            SP.CONFIG_PORT:8088
        },

        incomingtomavenmessagehandler+".Writer":
        {
            SP.CONFIG_HOST:'localhost',
            SP.CONFIG_QUEUE:'incoming_work_queue',
            SP.CONFIG_EXCHANGE:'maven_exchange',
            SP.CONFIG_KEY:'incoming'
        },
    }
    MC.MavenConfig = MavenConfig


    #loop = asyncio.get_event_loop()
    sp_consumer = IncomingMessageHandler(incomingtomavenmessagehandler)
    sp_producer = OutgoingMessageHandler(outgoingtohospitalsmessagehandler)

    reader = sp_consumer.schedule(loop)
    emitter = sp_producer.schedule(loop)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        sp_consumer.close()
        sp_producer.close()
        loop.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    main(loop)
