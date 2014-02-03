__author__ = 'yuki'

import amqp

conn = amqp.Connection('localhost')
chan = amqp.Channel(conn)

chan.queue_declare(queue='hello')

chan._basic_publish(amqp.basic_message.Message(body='Worldly, Bitch'), exchange='',routing_key='', mandatory=False, immediate=True)
print("Sent Hello World")

chan.close()
conn.close()