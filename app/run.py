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

import backend as maven_backend
import frontend_web as maven_frontend
from app.backend.module_webservice.data_router import MavenWebservicesServer

#from app.backend.data_router import Emitter as emitter
from werkzeug.contrib.fixers import ProxyFix
#from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Process



def main():

    #with ProcessPoolExecutor(max_workers=2) as executor:
        #executor.submit(start_dispatch_listener())
        #executor.submit(start_backend())

    ###
    #Attempt #1 at running Maven's various applications as seperate Processes
    #p1 = Process(target=startBackEnd())
    #p2 = Process(target=startFrontEnd())

    listening_loop = asyncio.get_event_loop()
    print(listening_loop)
    emitting_loop = asyncio.new_event_loop()
    print(emitting_loop)
    p3 = Process(target=start_webservices(MavenWebservicesServer(), listening_loop, emitting_loop))

   # with ThreadPoolExecutor as executor:
    #    executor.submit(MavenWebservicesServer())
     #   executor.submit(Emitter())

    #p1.start()
    #p2.start()
    p3.start()



def start_frontend():
    app = maven_frontend.frontend_web
    app.wsgi_app = ProxyFix(app.wsgi)
    app.run(host='127.0.0.1', port=8087, debug=True)


def start_backend():
    app = maven_backend.backend
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(host='127.0.0.1', port=8088, debug=True)

def start_webservices(services, listening_loop, emitting_loop):
    #transport_manager = {}
    services.start_servers(listening_loop, emitting_loop)
    listening_loop.close()
    emitting_loop.close()


if __name__ == '__main__':
    main()