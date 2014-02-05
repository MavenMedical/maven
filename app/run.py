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
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.contrib.fixers import ProxyFix


import backend as maven_backend
import frontend_web as maven_frontend

#application = maven.backend.run(host='0.0.0.0', port=8087, debug=True)
#application = maven_backend.backend.run(debug=True)

application = maven_frontend.frontend_web.run(debug=True)


#application = DispatcherMiddleware(maven_frontend.frontend_web.run(debug=True),{'/webservice': maven_backend.backend.run(host='0.0.0.0',
 #                                                                    port=8088,
  #                                                                   debug=True)})