##############################################################################
#  Copyright (c) 2014 - Maven Medical
#
#
#  Description: This module extends the StreamProcessor class into a REST web server.
#               I also give a sample application, which interacts with a slightly modified
#               version of the backbone tutorial's user manager application.
#               
#  Author: Tom DuBois
#  Assumes: Nothing for now, eventually that Rabbit will send a message 
#           with a specific format
#  Side Effects: None
#  Last Modified: 
##############################################################################

import urllib.parse
import json
import traceback
import re

import asyncio
from http_parser.parser import HttpParser

import maven_config as MC
import maven_logging as ML
import utils.streaming.stream_processor as SP
import time
import utils.streaming.http_responder as HR
from collections import defaultdict

class CaptureService(HR.HTTPProcessor):
    """ BackboneService is a subclass of HTTPProcessor which interacts with the backbone.js turorial available 
    from git clone https://github.com/thomasdavis/backbonetutorials.git
    
    It keeps an in-memory list of users, with first/last names and ages.
    The web service supports adding, deleting, editing, and listing user(s)
    """

    def __init__(self, configname):
        """ initializes the web service and registers all of the handlers """
        HR.HTTPProcessor.__init__(self, configname)
        self.allusers = {'1': {'id': '1', 'firstname': 'Tom', 'lastname': 'D', 'age': '33'}}
        self.nextid = 2
        
        self.add_handler(['POST'], '/update', self.update_text)
        self.add_handler(['POST'], '/done', self.done)
        self.add_handler(['GET', 'OPTIONS'], '/text', self.get_text)
        self.add_handler(['GET', 'OPTIONS'], '/duration', self.get_duration)
        self.db = defaultdict(list)
        self.finished = defaultdict()
        self.starttimes={}

    @asyncio.coroutine
    def update_text(self, _header, body, qs, _matches, _key):
        """ this and the following functions demonstrate how to handle web service requests.
        It returns a response code, the message body, and a list of extra header lines.

        Note that it is registered in the __init__ function

        :param header: the HttpParse object
        :param body: the request body
        :param qs: a map from the query string (ex ?x=&y=1&y=2&Y&z=4 becomes {y:[1,2],z:[4]})
        :param matches: a list of url parts matches from the handler's regex
        :param key: not used here, but potentially useful for passing off processing to another machine
        """
        user = qs['user'][0]
        if not user in self.finished:
            if not user in self.starttimes:
                self.starttimes[user]=time.time();
            self.db[user].append([time.time()-self.starttimes[user],json.loads(body.decode('utf-8'))])
            print([user,self.db[user][-1]])
            return (HR.OK_RESPONSE, b'' ,None)

    @asyncio.coroutine
    def get_duration(self, _header, _body, qs, matches, _key):
        """ get_user's regex is '/user/(\d+)', so matches = [<user id from regex>] """
        user = qs['user'][0]
        ret = self.db[user][-1][0]
        return (HR.OK_RESPONSE, json.dumps(ret), None)

    @asyncio.coroutine
    def get_text(self, _header, _body, qs, matches, _key):
        """ get_user's regex is '/user/(\d+)', so matches = [<user id from regex>] """
        user = qs['user'][0]
        ret = self.db[user][int(qs['i'][0])]
        print(ret)
        if not ret[1]:
            ret = b''
        else:
            ret = json.dumps(ret)
        return (HR.OK_RESPONSE, ret, None)
#        return (HR.OK_RESPONSE, json.dumps('hi'), None)

    @asyncio.coroutine
    def done(self, _header, _body, qs, matches, _key):
        user = qs['user'][0]
        if not user in self.finished:
            self.db[user].append([time.time()-self.starttimes[user],None])
            print([user,self.db[user][-1]])
            self.finished[user]=True
        return (HR.OK_RESPONSE, b'' ,None)


#  Mapping from parser types in the config file to the classes that handle them

if __name__ == '__main__':
    ML.DEBUG = ML.no_logging
    MC.MavenConfig = \
        {
            "httpserver":
                {
                    SP.CONFIG_HOST: 'localhost',
                    SP.CONFIG_PORT: 8087,
                },
        }
    hp = CaptureService('httpserver')
    event_loop = asyncio.get_event_loop()
    hp.schedule(event_loop)
    event_loop.run_forever()
