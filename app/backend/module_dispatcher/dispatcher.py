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
#import app.configs.config as MAVEN_CONFIG
from app.utils.streaming.servers import ListeningServer

class Dispatcher():

    def __init__(self, name):
        self.name = name


def startServer():
    ###
    #Start and configure the asynchronous event-driven loop
    server = ListeningServer()
    loop = asyncio.get_event_loop()
    coro = loop.create_server(server, '127.0.0.1', 8888)
    server = loop.run_until_complete(coro)

    ###
    #Just a statement for the console so you know it's running
    #Again, anywhere we have print statements to confirm stuff is running are
    #likely candidates for being logged by an upstream logger
    print('serving on {}'.format(server.sockets[0].getsockname()))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("exit")

    finally:
        server.close()
        loop.close()