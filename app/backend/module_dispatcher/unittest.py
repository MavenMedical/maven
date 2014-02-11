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
from app.utils.streaming.servers import DispatchServer as listener
#import app.backend.module_webservice.receiver as receiver



loop = asyncio.get_event_loop()

coro = loop.create_server(listener, '127.0.0.1', 8888)
server = loop.run_until_complete(coro)
###
#Just a statement for the console so you know it's running
#Again, anywhere we have print statements to confirm stuff is running are
#likely candidates for being logged by an upstream logger
###
print('serving on {}'.format(server.sockets[0].getsockname()))


@asyncio.coroutine
def delayed_print():
    asyncio.sleep(5)
    print('Hello hello')

try:
    loop.run_until_complete(delayed_print())
    loop.run_forever()
except KeyboardInterrupt:
    print("exit")

finally:
    server.close()
    loop.close()





class SendFakeData(asyncio.Protocol):
    message = 'This is the message. It will be echoed.'

    def connection_made(self, transport):
        #asyncio.sleep(5)
        transport.write(self.message.encode())
        print('data sent: {}'.format(self.message))

    def data_received(self, data):
        print('data received: {}'.format(data.decode()))

    def connection_lost(self, exc):
        print('server closed the connection')
        asyncio.get_event_loop().stop()
