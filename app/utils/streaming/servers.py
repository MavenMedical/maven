#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:   This file provides abstract classes to be instantiated by other modules as necessary.
#               It creates Asynchronous Listeners/Emitters that are can be connected to RabbitMQ and databases
#************************
#ASSUMES:       Configuration settings in 'configs/config.py'
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-51
#*************************************************************************

import amqp, asyncio
#import app.configs.config as MAVEN_CONFIG

class DispatchServer(asyncio.Protocol):
    def connection_made(self, transport):
        #TODO
        #will likely want to replace this print function with a logging function
        peername = transport.get_extra_info('peername')
        print('connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        ###
        #Set Up Communications with RabbitMQ Server
        rabbit_connection = amqp.Connection('localhost')
        dispatch_channel = rabbit_connection.channel()

        ###
        #TODO - will likely want to replace this print function with a logging function
        print('data received: {}'.format(data.decode()))

        ###
        #TODO - will likely want to send a confirmation-of-receipt message
        self.transport.write(data)

        #send_rabbit_message(self, data)
        asyncio.Task(send_rabbit_message(self, data, rabbit_connection, dispatch_channel))
        self.transport.close()


class MessageServer(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        #TODO
        #will likely want to replace this print function with a logging function
        print('data received: {}'.format(data.decode()))
        self.transport.write(data)
        #send_rabbit_message(self, data)
        asyncio.Task(send_rabbit_message(self, data))
        self.transport.close()

@asyncio.coroutine
def send_rabbit_message(self, data, connection, channel):
    message = amqp.Message(data)
    channel.basic_publish(message,
                                  exchange="mavenExchange",
                                  routing_key='incoming')
    channel.close()
    connection.close()

