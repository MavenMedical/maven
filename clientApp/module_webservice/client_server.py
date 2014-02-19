#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:   This "client_receiver.py" file contains a "Receiver" class very similar to the
#               Maven-side "Receiver" in the data_router.py file. The main difference that upon receiving
#               data, this Receiver does NOT send to RabbitMQ but rather puts the message into a queue to be
#               processed locally on the hospital client server.
#
#
#
#
#
#
#************************
#ASSUMES:
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-65
#*************************************************************************
import asyncio
from app.utils.streaming import servers
from xml.etree import ElementTree as ET


class Server:
    def __init__(self):
        self.server = None
        self.clients = {}

    def start(self, loop, host, port):
        coro = loop.create_server(Receiver, host, port)
        self.server = loop.run_until_complete(coro)

class Receiver(servers.ListeningServer):
    """
    This class inherits from the app/utils/streaming/servers.py ListeningServer object.

    It overrides the __init__.py constructor in order to specify the local queue handling of messages.

    It also overrides the "data_received" method which is crucial to the proper functioning of this
    object.
    """
    def __init__(self):
        self.name = 'client_receiver'
        self.clients = {}

    def data_received(self, data):
        asyncio.Task(self.evaluate_message(data))

    @asyncio.coroutine
    def evaluate_message(self, msg):
        message = msg.decode()
        message_root = ET.fromstring(message)
        message_type = self.get_message_type(message_root.tag)

        if message_type == 'outgoing':
            print('This is an outgoing message from Epic')
            asyncio.Task(self.send_outgoing_message(message.encode()))

    def get_message_type(self, str):
        if "urn:Epic" in str:
            return 'outgoing'
        elif "urn:Maven" in str:
            return 'incoming'

    @asyncio.coroutine
    def send_outgoing_message(self, msg):
        reader, writer = yield from asyncio.open_connection(host='127.0.0.1', port=7888)
        writer.write(msg)
        writer.close()

    @asyncio.coroutine
    def send_to_emr(self, msg):
        print('Saving moolah!')

    def connection_lost(self, exc):
        print('Client closed connection')