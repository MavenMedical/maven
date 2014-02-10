
#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
#__author__='Aidan Fowler'
#************************
#DESCRIPTION: database connector
#************************
#ASSUMES: we can connect to our database using psycopg2
#************************
#SIDE EFFECTS: None
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-40 Wednesday February 5th
#*************************************************************************
import psycopg2


def connectToDb():
    conn_string = "host='localhost' dbname='maven' user='maven' password='temporary'"
    print ("\nConnecting to database\nConnection Parameters: %s" % conn_string)
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    print ("Connected!\n")
    return cursor