#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:   This python file runs the backend application. It uses the 'config.py' file
#
#************************
#ASSUMES:       Configuration settings in 'config.py'
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-1
#*************************************************************************

import amqp, asyncio

class DispatchServer(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        print('data received: {}'.format(data.decode()))
        self.transport.write(data)
        send_rabbit_message(self, data)
        self.transport.close()

#Set Up Communications with RabbitMQ Server
rabbitConnection = amqp.Connection('localhost')
dispatchChannel = rabbitConnection.channel()

#Start and configure the asynchronous event-driven loop
loop = asyncio.get_event_loop()
coro = loop.create_server(DispatchServer, '127.0.0.1', 8888)
server = loop.run_until_complete(coro)

#Just a statement for the console so you know it's running
print('serving on {}'.format(server.sockets[0].getsockname()))


def send_rabbit_message(self, data):
    message = amqp.Message(data)
    dispatchChannel.basic_publish(message, exchange="mavenExchange", routing_key='incoming')
    yield from asyncio.sleep(30)

try:
    loop.run_forever()
except KeyboardInterrupt:
    print("exit")

finally:
    dispatchChannel.close()
    rabbitConnection.close()
    server.close()
    loop.close()

