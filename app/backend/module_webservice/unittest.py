#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:   This python file runs the backend application. It uses the 'config.py' file
#               located at the same level in the directory as this file itself.
#************************
#ASSUMES:       Configuration settings in 'config.py'
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-1
#*************************************************************************
import asyncio
#from app.backend.data_router import Receiver
#import app.backend.module_webservice.receiver as receiver


class EchoClient(asyncio.Protocol):
    message = 'HALLO TOM'
    message2 = 'This is the message. It will be echoed2'
    message3 = 'This is the message. It will be echoed3'

    def connection_made(self, transport):
        transport.write(self.message.encode())
        #transport.write(self.message2.encode())
        #transport.write(self.message3.encode())
        #print('data sent: {}'.format(self.message))

    def data_received(self, data):
        print('data received: {}'.format(data.decode()))

    def connection_lost(self, exc):
        print('server closed the connection')
        asyncio.get_event_loop().stop()

loop = asyncio.get_event_loop()
coro = loop.create_connection(EchoClient, '127.0.0.1', 7888)
loop.run_until_complete(coro)
#loop.run_forever()
loop.close()
