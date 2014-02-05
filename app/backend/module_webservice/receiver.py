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

import amqp, asyncio

conn = amqp.Connection('localhost')
chan = conn.channel()

chan.queue_declare(queue="dispatcherQueue")
chan.exchange_declare(exchange="mavenExchange", type="direct")
chan.queue_bind(queue="dispatcherQueue", exchange="mavenExchange", routing_key="incoming")

def cBack(msg):
    incoming_message = msg.body.decode()
    print("Received a message!: " + incoming_message)

chan.basic_consume(queue='dispatcherQueue', no_ack=False, callback=cBack)

while True:
    chan.wait()

chan.basic_cancel("TestTag")

chan.close()
conn.close()



