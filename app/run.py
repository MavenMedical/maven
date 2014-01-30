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

import backend as maven

maven.backend.run(host='0.0.0.0', port=8080, debug=True)

git commit -am "Mave-1 Created skeleton of scalable Maven application with necessary architecture for sub-applications (i.e. backend, frontend_web) which will be run as separate threads synchronously (frontend_web) or asynchronously (backend) as needed."