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

def main():

    loop = asyncio.get_event_loop()
    loop2 = asyncio.get_event_loop()
    coro_listen = loop.create_connection(listener, '127.0.0.1', 8888)
    coro_emit = loop2.create_connection(SendFakeData, '127.0.0.1', 8888)
    loop.run_until_complete(coro_listen)
    loop2.run_until_complete(coro_emit)


    try:
        loop.run_forever()
        loop2.run_forever()
        #loop.run_forever(coro_listen)
        for i in range(0, 3):
            loop.run_until_complete(coro_emit)
    except KeyboardInterrupt:
        print("exit")
    finally:
        coro_listen.close()
        loop.close()


class SendFakeData():
    message = 'This is the message. It will be echoed.'

    def connection_made(self, transport):
        asyncio.sleep(5)
        transport.write(self.message.encode())
        print('data sent: {}'.format(self.message))

    def data_received(self, data):
        print('data received: {}'.format(data.decode()))

    def connection_lost(self, exc):
        print('server closed the connection')
        asyncio.get_event_loop().stop()


if __name__ == '__main__':
    main()