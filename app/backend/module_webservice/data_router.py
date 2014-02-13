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

import asyncio
import amqp
#import app.configs.config as MAVEN_CONFIG
from app.utils.streaming import servers
from concurrent.futures import ThreadPoolExecutor
#from app.backend.emitter import Emitter as emitter
#from app.backend.emitter import RabbitReceiver as rr

transport_manager = {}

class MavenWebservicesServer():

    def __init__(self):
        pass

    def start_servers(self, listening_loop, emitting_loop):
        rabbit_listener_thread_pool = ThreadPoolExecutor(max_workers=4)
        listening_coroutine = listening_loop.create_server(Receiver, '127.0.0.1', 7888)

        try:
            emitting_loop.run_in_executor(rabbit_listener_thread_pool, Emitter, emitting_loop, transport_manager)
            listening_server = listening_loop.run_until_complete(listening_coroutine)
            print('serving on {}'.format(listening_server.sockets[0].getsockname()))

            listening_loop.run_forever()
            emitting_loop.run_forever()

        except KeyboardInterrupt:
            print("exit")

        finally:
            emitting_loop.close()
            listening_coroutine.close()
            listening_loop.close()


class Receiver(servers.ListeningServer):

    def __init__(self):
        self.name = 'data_receiver'
        ###
        #Set-Up Rabbit Connections for this instance of the WebservicesDataServer Class/Object
        self.rabbit_connection = amqp.Connection('localhost')
        self.rabbit_channel = self.rabbit_connection.channel()
        self.rabbit_exchange = "maven_exchange"
        self.rabbit_incoming_key = 'incoming'

    ###
    #This method is IMPORTANT b/c it overrides the default data_received method as defined in the
    # the Listening Server Class/Object that was imported from app/utils/streaming/servers.py

    def data_received(self, data):
        transport_manager['go'] = self.transport
        asyncio.Task(self.send_rabbit_message(data,
                                              self.rabbit_exchange,
                                              self.rabbit_channel,
                                              self.rabbit_incoming_key))

class Emitter():

    def __init__(self, loop=None, transport_manager=None):
        print('Emitter().py has initialized')
        self.msg = ''
        self.loop = loop
        self.transport_manager = transport_manager
        self.conn = amqp.Connection('localhost')
        self.chan = self.conn.channel()
        self.chan.queue_declare(queue="incoming_work_queue")
        self.chan.exchange_declare(exchange="maven_exchange", type="direct")
        self.chan.queue_bind(queue="incoming_work_queue", exchange="maven_exchange", routing_key="incoming")
        self.chan.basic_consume(queue='incoming_work_queue', no_ack=True, callback=self.amqp_call_back)

        self.run()

    def run(self):
        self.chan.basic_consume(queue='incoming_work_queue', no_ack=True, callback=self.amqp_call_back)
        while True:
            self.chan.wait()

        self.chan.close()
        self.conn.close()

    def amqp_call_back(self, msg):
        self.msg = msg
        incoming_message = msg.body.decode()
        asyncio.set_event_loop(self.loop)
        ################
        future = asyncio.Future()
        asyncio.Task(self.gather_data(future))
        self.loop.run_until_complete(future)

    @asyncio.coroutine
    def gather_data(self, future):
        destination = self.transport_manager['go'].get_extra_info('peername')
        host = destination[0]
        port = 8111 #destination[1]
        message = self.msg
        yield from self.send_data(future, host, port, message)

    @asyncio.coroutine
    def send_data(self, future, host, port, message):
        reader, writer = yield from asyncio.open_connection(host=host, port=port)
        writer.write(message.body)
        writer.close()

        future.set_result('Done')

