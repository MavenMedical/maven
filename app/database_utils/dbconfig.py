##############################################################################
#  Copyright (c) 2014 - Maven Medical
#
#  Description: Configuration for database connection
#  Author: Aidan Fowler
#  Assumes:
#  Side Effects:
#  Last Modified: FOR JIRA ISSUE: MAV-70 Monday February 17th
##############################################################################

#Definitions for the database we are working with
#DATABASE name
DATABASE = 'maven'
#USER information
USERNAME = 'maven'
PASSWORD = 'temporary'
#HOST:PORT
HOST = 'localhost'
PORT = '5432'


CONNECTION_STRING = "dbname=%s user=%s password=%s host=%s port=%s" % (DATABASE,USERNAME,PASSWORD,HOST,PORT)


RULE_TABLE_MAPPING = ("ruleName","ruleDescription","orderType","orderedCPT","minAge","maxAge","withDX","withoutDX","details","onlyInDept","notInDept")