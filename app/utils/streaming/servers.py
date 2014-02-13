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

class ListeningServer(asyncio.Protocol):
    ###
    #TODO - Proper instantiation method for this very important object
    def __init__(self):
        print('Started')
        pass

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

        #send_rabbit_message(self, data)
        asyncio.Task(send_rabbit_message(self, data, rabbit_connection, dispatch_channel))

    @asyncio.coroutine
    def send_rabbit_message(self, data, exchange, channel, routing_key):
        message = amqp.Message(data)
        channel.basic_publish(message,
                              exchange=exchange,
                              routing_key=routing_key)

class EmittingServer(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('connection from {}'.format(peername))
        self.transport = transport


    def data_received(self, data):
        #TODO
        #will likely want to replace this print function with a logging function
        print('data received: {}'.format(data.decode()))
        self.transport.write(data)
        asyncio.Task(send_rabbit_message(self, data))
        self.transport.close()


@asyncio.coroutine
def send_data(self, data):
    self.transport.write(data)


@asyncio.coroutine
def send_rabbit_message(data, exchange, channel, routing_key):
    message = amqp.Message(data)
    channel.basic_publish(message,
                          exchange=exchange,
                          routing_key=routing_key)


