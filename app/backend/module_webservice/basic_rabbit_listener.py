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

import amqp
import asyncio

conn = amqp.Connection('localhost')
chan = conn.channel()

chan.queue_declare(queue="incoming_work_queue")
chan.exchange_declare(exchange="maven_exchange", type="direct")
chan.queue_bind(queue="incoming_work_queue", exchange="maven_exchange", routing_key="incoming")

def cBack(msg):
    asyncio.sleep(3)
    incoming_message = msg.body.decode()
    print("Received a message!: " + incoming_message)



chan.basic_consume(queue='incoming_work_queue', no_ack=False, callback=cBack)

while True:
    chan.wait()

chan.close()
conn.close()



