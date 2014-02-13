#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
#__author__='Aidan Fowler'
#************************
#DESCRIPTION: Logger for rule_engine testing
#************************
#ASSUMES:
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-40 Wednesday February 12th
#*************************************************************************

global logging
logging = False

class Logger():

    def log(message):
        global logging
        if (logging):
            print(message)

    def setLogging(command):
        global logging
        if command == True:
            logging = True
        elif command == False:
            logging = False