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
import backend as maven_backend
import frontend_web as maven_frontend
from backend.module_dispatcher import dispatcher as dispatcher
from werkzeug.contrib.fixers import ProxyFix
from concurrent.futures import ProcessPoolExecutor
#from multiprocessing import Process



def main():

    with ProcessPoolExecutor(max_workers=2) as executor:
        executor.submit(startDispatchListener())
        executor.submit(startBackEnd())

    ###
    #Attempt #1 at running Maven's various applications as seperate Processes
    #p1 = Process(target=startBackEnd())
    #p2 = Process(target=startFrontEnd())
    #p3 = Process(target=startDispatchListener())

    #p1.start()
    #p2.start()
    #p3.start()

def startFrontEnd():
    app = maven_frontend.frontend_web
    app.wsgi_app = ProxyFix(app.wsgi)
    app.run(host='127.0.0.1', port=8087, debug=True)

def startBackEnd():
    app = maven_backend.backend
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(host='127.0.0.1', port=8088, debug=True)

def startDispatchListener():
    dispatcher.startServer()


if __name__ == '__main__':
    main()