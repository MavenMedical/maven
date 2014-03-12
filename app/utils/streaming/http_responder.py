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

import asyncio
import maven_config as MC
import maven_logging as ML
import app.utils.streaming.stream_processor as SP
from http_parser.parser import HttpParser
import json
import traceback
import re

CONFIGVALUE_HTTPPARSER = 'http parser'

"""
    #based on sample code taken from: https://pypi.python.org/pypi/http-parser
    p = HttpParser()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    body = []
    try:
        while True:
            data = s.recv(1024)
            if not data:
                break

            recved = len(data)
            nparsed = p.execute(data, recved)
            assert nparsed == rec ved

            if p.is_headers_complete():
                print p.get_headers()

            if p.is_partial_body():
                body.append(p.recv_body())

            if p.is_message_complete():
                break

        print "".join(body)
"""

OK_RESPONSE = b'HTTP/1.0 200 OK'
UNAVAILABLE_RESPONSE = b'HTTP/1.1 503 Service Unavailable'

DEFAULT_HEADERS = \
    [
        b'Content-Type: application/json',
        b'Connection: Keep-Alive',
    ]
    # text/plain


# noinspection PyArgumentList
def wrap_response(response_type, text, extra_header_list=None):
    if not extra_header_list:
        extra_header_list = []
    return b'\r\n'.join([response_type] + DEFAULT_HEADERS + extra_header_list +
                        [b'Content-length: ' + bytes(str(len(text)), "utf-8"), b'',
                         (text if type(text) == bytes else bytes(text, "utf-8"))])


class _HTTPStreamParser(SP.MappingParser):

    starting_re = re.compile(b"(GET|POST|OPTIONS|DELETE|PUT|HEAD)")

    def __init__(self, configname, read_fn, loop, register_fn):
        SP.MappingParser.__init__(self, configname, read_fn, lambda x: x, loop, register_fn)
        self.p = HttpParser()
        self.body = []

    def data_received(self, data):
        splits = _HTTPStreamParser.starting_re.split(data)
        
        for sp in filter(None,splits):
            #print("SP: "+str(sp))
            self.p.execute(sp, len(sp))
            
            if self.p.is_partial_body():
                self.body.append(self.p.recv_body())

            if self.p.is_message_complete():
                coro = self.read_fn([self.p, b''.join(self.body)], self.registered_key)
                self.loop.call_soon_threadsafe(SP.MappingParser.create_task, coro, self.loop)
                self.p = HttpParser()
                self.body = []


class HTTPProcessor(SP.StreamProcessor):

    @asyncio.coroutine
    def read_object(self, obj, key):
        ret = wrap_response(UNAVAILABLE_RESPONSE, b'')
        self.write_object(ret, writer_key = key)

    def __init__(self, configname):
        """ Initialize the StreamProcessor superclass, getting all of the IO and helper functions from 
        the MavenConfig structure.  It creates the StreamProcess, but does not yet make network connections.

        :param configname: the name of the instance to pull config parameters
        """
        try:
            self.config = MC.MavenConfig[configname]
            self.host = self.config.get(SP.CONFIG_HOST, None)
            self.port = self.config[SP.CONFIG_PORT]
        except KeyError:
            raise MC.InvalidConfig(configname + " did not have sufficient parameters.")            
        
        readername = configname + '.reader'
        writername = configname + '.writer'

        self.config.update(
            {
                SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSERVERSOCKET,
                SP.CONFIG_READERNAME: readername,
                SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETREPLY,
                SP.CONFIG_WRITERNAME: writername,
                SP.CONFIG_WRITERDYNAMICKEY: 1,  # this reader's dynamic key
                SP.CONFIG_PARSERTYPE: CONFIGVALUE_HTTPPARSER,
            })
        MC.MavenConfig.update(
            {
                readername:
                    {
                        SP.CONFIG_HOST: self.host,
                        SP.CONFIG_PORT: self.port,
                    },
                writername:
                    {
                        SP.CONFIG_WRITERKEY: 1,
                    },
            })

        SP.StreamProcessor.__init__(self, configname)


class BackboneService(HTTPProcessor):

    def __init__(self, configname):
        HTTPProcessor.__init__(self, configname)
        self.allusers = {'1': {'id': '1', 'firstname': 'Tom', 'lastname': 'D', 'age': '33'}}
        self.nextid = 2

    @asyncio.coroutine
    def read_object(self, obj, key):
        parsed = obj[0]
        body = obj[1]
        print("errno: %s" % obj[0].get_errno())
        print("header: %s" % obj[0].get_headers())
        print("method: %s" % obj[0].get_method())
        print("path: %s" % obj[0].get_path())
        print("query: %s" % obj[0].get_query_string())
        print("status: %s" % obj[0].get_status_code())
        print("body: %s" % obj[1])
        extra = [
                    b'Access-Control-Allow-Headers: X-Requested-With, X-HTTP-Method-Override, Content-Type, Accep',
                    b'Access-Control-Allow-Methods: POST, GET, PUT, DELETE, OPTIONS',
                    b'Access-Control-Allow-Origin: *',
                    b'Content-Type: application/json',
                ]
        method = parsed.get_method()
        path = parsed.get_path()
        try:
            if method == 'OPTIONS':
                ret = wrap_response(OK_RESPONSE, b'OK', extra_header_list=extra)
            elif path == '/users' and method == 'GET':
                ret = wrap_response(OK_RESPONSE, json.dumps([self.allusers[x] for x in sorted(self.allusers.keys())]),
                                    extra_header_list=extra)
            elif path[:6] == '/user/' and method == 'GET':
                ret = wrap_response(OK_RESPONSE, json.dumps(self.allusers[path[6:]]), extra_header_list=extra)
            elif path[:6] == '/user/' and method == 'PUT':
                update = json.loads(body.decode('utf-8'))
                if not self.allusers[path[6:]]['id'] == update['id']:
                    raise Exception()
                self.allusers[path[6:]] = update
                ret = wrap_response(OK_RESPONSE, body, extra_header_list=extra)
            elif path[:6] == '/user/' and method == 'DELETE':
                self.allusers.pop(path[6:])
                ret = wrap_response(OK_RESPONSE, b'OK', extra_header_list=extra)
            elif path == '/user' and method == 'POST':
                self.nextid += 1
                while str(self.nextid) in self.allusers:
                    self.nextid += 1
                update = json.loads(body.decode('utf-8'))
                newuser = \
                    {
                        'id': str(self.nextid),
                        'firstname': update['firstname'],
                        'lastname': update['lastname'],
                        'age': update['age']
                    }
                self.allusers[str(self.nextid)] = newuser
                ret = wrap_response(OK_RESPONSE, json.dumps(newuser), extra_header_list=extra)
            else:
                raise Exception()
        except Exception as e:
            traceback.print_exc()
            ret = wrap_response(UNAVAILABLE_RESPONSE, b'')

        SP.StreamProcessor.write_object(self, ret, key)

#  Mapping from parser types in the config file to the classes that handle them

SP._parser_map[CONFIGVALUE_HTTPPARSER] = _HTTPStreamParser

if __name__ == '__main__':
    MC.MavenConfig = \
        {
            "httpserver":
                {
                    SP.CONFIG_HOST: 'localhost',
                    SP.CONFIG_PORT: 8087,
                },
        }
    hp = BackboneService('httpserver')
    event_loop = asyncio.get_event_loop()
    hp.schedule(event_loop)
    event_loop.run_forever()
