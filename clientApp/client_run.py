#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:   This "client_receiver.py" file contains a "Receiver" class very similar to the
#               Maven-side "Receiver" in the data_router.py file. The main difference that upon receiving
#               data, this Receiver does NOT send to RabbitMQ but rather puts the message into a queue to be
#               processed locally on the hospital client server.
#
#
#
#
#
#
#************************
#ASSUMES:
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-65
#*************************************************************************
import asyncio
from module_webservice import client_server
import argparse


ARGS = argparse.ArgumentParser(description='Maven Client server.')
ARGS.add_argument(
    '--host', action='store', dest='host',
    default='127.0.0.1', help='Host name')
ARGS.add_argument(
    '--port', action='store', dest='port',
    default=7777, type=int, help='Port number')
args = ARGS.parse_args()


def main():

    loop = asyncio.get_event_loop()
    server = client_server.Server()
    server.start(loop, args.host, args.port)

    try:
        loop.run_forever()

    except KeyboardInterrupt:
        print('Exit')

    finally:
        loop.close()


if __name__ == '__main__':
    main()