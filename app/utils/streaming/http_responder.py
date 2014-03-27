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
import urllib.parse
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

# Various http response codes to be returned to the client.
# see http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html for more info
OK_RESPONSE = b'HTTP/1.0 200 OK'
UNAVAILABLE_RESPONSE = b'HTTP/1.0 503 Service Unavailable'
CREATED_RESPONSE = b'HTTP/1.0 201 Created'
NOCONTENT_RESPONSE = b'HTTP/1.0 204 No Content'
BAD_RESPONSE = b'HTTP/1.0 400 Bad Request'
UNAUTHORIZED_RESPONSE = b'HTTP/1.0 401 Unauthorized' # needs to let the client know how to get authorization
NOTFOUND_RESPONSE = b'HTTP/1.0 404 Not Found'
NOTALLOWED_RESPONSE = b'HTTP/1.0 405 Method Not Allowed'
ERROR_RESPONSE = b'HTTP/1.0 500 Internal Server Error'

DEFAULT_HEADERS = \
    [
        b'Content-Type: application/json',
        b'Connection: close',
    ]
    # text/plain


def wrap_response(response_type, text, extra_header_list=None):
    """ wrap_response takes the information required for an http response and creates
    the byte stream to send in reply

    :param response_type: one of the predefined types like "200 OK"
    :param text: the body of the http response
    :extra_header_list: by default the headers Content-Type and Connection are returned,
                        put extra header lines here
                        """

    if not extra_header_list:
        extra_header_list = []
    return b'\r\n'.join([response_type] + DEFAULT_HEADERS + extra_header_list +
                        [b'Content-length: ' + bytes(str(len(text)), "utf-8"), b'',
                         (text if type(text) == bytes else bytes(text, "utf-8"))])


class _HTTPStreamParser(SP.MappingParser):
    """ _HTTPStreamParser is a stream parser that takes a stream of (either one, or multiple 
    pipelined) HTTP requests, divides them into individual requests, parses them into a 
    HttpParser object and a body, and calls read_object (see stream_processor for more info
    on parsers
    """
    
    # Every HTTP message should start with one of these.  So each occurence is a 
    # potential delimited between messages.  Used for breaking up potentially 
    # pipelined messages
    _starting_re = re.compile(b"(GET|POST|OPTIONS|DELETE|PUT|HEAD|TRACE)")

    def __init__(self, configname, read_fn, loop, register_fn):
        """ __init__ initializes the _HttpStreamParser.
        It has a base stream_processor.MappingParser, plus an HttpParser and a body.
        :param configname: the name of this parser in the config file
        :param read_fn: the function to pass completed http request objects
        :param loop: the event loop
        :param register_fn: when a new socket is opened, register a writer for it here
        """
        SP.MappingParser.__init__(self, configname, read_fn, lambda x: x, loop, register_fn)
        ML.DEBUG("created a new http parser")
        self.p = HttpParser()
        self.body = []

    def data_received(self, data):
        """ data_received is called whenever an open socket receives data.
        see http://docs.python.org/3.4/library/asyncio-protocol.html for info on asyncio protocols
        :params data: the bytes received over the socket
        """

        ML.DEBUG("RECV: " + str(data))
        
        # split the data on potential http request boundaries
        splits = _HTTPStreamParser._starting_re.split(data)
        
        # for each non-empty split, parse it
        for sp in filter(None,splits):
            #print("SP: "+str(sp))
            base=0
            while base < len(sp):
                c = self.p.execute(sp[base:], len(sp[base:]))  # parse the chunk of bytes
                l = len(sp[base:])
                base=base+c
            
            # if it contains part of the request's body, process that
            if self.p.is_partial_body():
                self.body.append(self.p.recv_body())

            # if the message is complete, put everything together, and launch a coroutine to handle it
            if self.p.is_message_complete():
                coro = self.read_fn([self.p, b''.join(self.body)], self.registered_key)
                self.loop.call_soon_threadsafe(SP.MappingParser.create_task, coro, self.loop)
                self.p = HttpParser()
                self.body = []

    def eof_received(self):
        ML.DEBUG("EOF")
        return True

class IncompleteRequest(Exception):
    pass


class HTTPProcessor(SP.StreamProcessor):
    """ HTTPProcessor extends stream_processor.StreamProcessor with a web server
    It can create many kinds of web servers, but the motivation is RESTful web services

    As written, when a client connects, a coroutine is schedule to handle the request and respond 
    immediately.  Without much effort it could be re-configured to bundle the request, send it to
    another machine for processing, and pair the reply back with the original socket when it comes back.
    """

    def __init__(self, configname):
        """ Initialize the StreamProcessor superclass, getting all of the IO and helper functions from 
        the MavenConfig structure.  It creates the StreamProcess, but does not yet make network connections.

        :param configname: the name of the instance to pull config parameters
        """

        # read the config parameters
        try:
            self.config = MC.MavenConfig[configname]
            self.host = self.config.get(SP.CONFIG_HOST, None)
            self.port = self.config[SP.CONFIG_PORT]
        except KeyError:
            raise MC.InvalidConfig(configname + " did not have sufficient parameters.")            
        
        # the web service only needs host and port parameters, but stream processor needs
        # more detailed information.  create detailed configuration parameters here
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

        # initialize the base StreamProcessor with this new configuration pameters
        SP.StreamProcessor.__init__(self, configname)

        # The one piece of state specific to this base class - the handler functions and their regexes
        # Any subclass of HttpProcessor should populate this in its __init__
        self.handlers = []


    @asyncio.coroutine
    def read_object(self, obj, key):
        """ read_object takes an http request and a writer key, determines which handler should process 
        request, invokes that handler, and responds with its output.
        
        It should handle catch-all errors, string sanitization, authentication, etc., so that the handler
        functions only worry about the business logic.

        :param obj: a list of [HttpParse, message_body]
        :param key: the key to be used when responding with self.write_object(response_bytes, key)
        """        
        
        headers = obj[0]
        body = obj[1]
        #ML.DEBUG("errno: %s" % headers.get_errno())
        ML.DEBUG("header: %s" % headers.get_headers())
        ML.DEBUG("method: %s" % headers.get_method())
        ML.DEBUG("path: %s" % headers.get_path())
        #ML.DEBUG("status: %s" % headers.get_status_code())
        ML.DEBUG("body: %s" % body)
        req_line = headers.get_method()+' '+headers.get_path()
        query_string = urllib.parse.parse_qs(headers.get_query_string())
        ML.DEBUG("query: %s" % str(query_string))
        #print(req_line)
        ret = None
        try:
            for (r, fn) in self.handlers:
            #print(r, fn)
                m = r.match(req_line)
                if m:  # if the regex matches, call the handler and return a response
                    (resp, body, extras) = yield from fn(headers, body, query_string, m.groups(), key)
                    if headers.get_method() == 'HEAD':  # don't send a body with HEAD
                        ret=wrap_response(resp, b'', extras)
                    else:
                        if resp == OK_RESPONSE and not body: # use No Content when called for
                            resp = NOCONTENT_RESPONSE
                        ret=wrap_response(resp, body, extras)
                    break
        except KeyError:  # key error means an object isn't found
            ret = wrap_response(NOTFOUND_RESPONSE, b'')
        except ValueError:
            ret = wrap_response(BAD_RESPONSE, b'')
        except IncompleteRequest as e :  # key error means an object isn't found
            ret = wrap_response(BAD_RESPONSE, bytes(str(e),'utf-8'))
        except:  # handle general errors gracefully
            traceback.print_exc()
            ret = wrap_response(ERROR_RESPONSE, b'')

        if not ret:  # if there are no matches, respond
            ret = wrap_response(UNAVAILABLE_RESPONSE, b'')

        try:
            self.write_object(ret, writer_key = key)  # send the response
            ML.DEBUG("done writing")
            if headers.get_headers().get('Connection','').upper()=='CLOSE':
                self.unregister_writer(key)
                ML.DEBUG("unregistering")
            else:
                ML.DEBUG(headers.get('Connection'))
        except:
            ML.WARN("connection to %s failed before write happened" % key)

    def add_handler(self, methods, regexpstring, fn):
        """ add_handler registers a handler method for this class
        All handlers are checked against the first line of an http request
        The first match gets to handle the message
        :param methods: a list of http methods (ex ['GET'])
        :param regexpstring: a string representing urls to match.
                             it may contain groups (ex "(\d+)") whose 
                             matches contents are passed to the handler.
        :param fn: the handler function
        """

        if 'GET' in methods and not 'HEAD' in methods:
            methods.append('HEAD')
        regexp = '(?:'+'|'.join(methods)+')\s+'+regexpstring
        self.handlers.append((re.compile(regexp), fn))
        #print(regexp)
        #print(re.match(regexp,b'GET /users/1 HTTP/1.0'))


class HTTPReader(SP.StreamProcessor):
    """ HTTPProcessor extends stream_processor.StreamProcessor with a web server
    It can create many kinds of web servers, but the motivation is RESTful web services

    As written, when a client connects, a coroutine is schedule to handle the request and respond 
    immediately.  Without much effort it could be re-configured to bundle the request, send it to
    another machine for processing, and pair the reply back with the original socket when it comes back.
    """

    def __init__(self, configname):
        """ Initialize the StreamProcessor superclass, getting all of the IO and helper functions from 
        the MavenConfig structure.  It creates the StreamProcess, but does not yet make network connections.

        :param configname: the name of the instance to pull config parameters
        """

        # read the config parameters
        try:
            self.config = MC.MavenConfig[configname]
            #self.host = self.config.get(SP.CONFIG_HOST, None)
            #self.port = self.config[SP.CONFIG_PORT]
        except KeyError:
            raise MC.InvalidConfig(configname + " did not have sufficient parameters.")            
        
        # the web service only needs host and port parameters, but stream processor needs
        # more detailed information.  create detailed configuration parameters here
        self.config.update(
            {
                SP.CONFIG_PARSERTYPE: CONFIGVALUE_HTTPPARSER,
            })

        # initialize the base StreamProcessor with this new configuration pameters
        SP.StreamProcessor.__init__(self, configname)

class HTTPWriter(SP.StreamProcessor):
    
    def __init__(self, configname):
        SP.StreamProcessor.__init__(self, configname)

    @asyncio.coroutine
    def read_object(self, obj, key):
        """ read_object takes an http request and a writer key, determines which handler should process 
        request, invokes that handler, and responds with its output.
        
        It should handle catch-all errors, string sanitization, authentication, etc., so that the handler
        functions only worry about the business logic.

        :param obj: 
        :param key: 
        """        
        
        ret = None
        try:
            (response, body, extras, k) = yield from self.format_response(obj, key)
            if response == OK_RESPONSE and not body: # use No Content when called for
                resp = NOCONTENT_RESPONSE
            ret=wrap_response(response, body, extras)

        except KeyError:  # key error means an object isn't found
            ret = wrap_response(NOTFOUND_RESPONSE, b'')
        except ValueError:
            ret = wrap_response(BAD_RESPONSE, b'')
        except IncompleteRequest as e :  # key error means an object isn't found
            ret = wrap_response(BAD_RESPONSE, bytes(str(e),'utf-8'))
        except:  # handle general errors gracefully
            traceback.print_exc()
            ret = wrap_response(ERROR_RESPONSE, b'')

        if not ret:  # if there are no matches, respond
            ret = wrap_response(UNAVAILABLE_RESPONSE, b'')

        try:
            self.write_object(ret, writer_key = k)  # send the response
            ML.DEBUG("done writing")
            if headers.get_headers().get('Connection','').upper()=='CLOSE':
                self.unregister_writer(k)
                ML.DEBUG("unregistering")
            else:
                ML.DEBUG(headers.get('Connection'))
        except:
            ML.WARN("connection to %s failed before write happened" % k)
    


class BackboneService(HTTPProcessor):
    """ BackboneService is a subclass of HTTPProcessor which interacts with the backbone.js turorial available 
    from git clone https://github.com/thomasdavis/backbonetutorials.git
    
    It keeps an in-memory list of users, with first/last names and ages.
    The web service supports adding, deleting, editing, and listing user(s)
    """

    def __init__(self, configname):
        """ initializes the web service and registers all of the handlers """
        HTTPProcessor.__init__(self, configname)
        self.allusers = {'1': {'id': '1', 'firstname': 'Tom', 'lastname': 'D', 'age': '33'}}
        self.nextid = 2
        
        self.add_handler(['POST'], '/user', self.create_user)
        self.add_handler(['GET', 'OPTIONS'], '/users', self.get_users)
        self.add_handler(['GET', 'OPTIONS'], '/user/(\d+)', self.get_user)
        self.add_handler(['DELETE'], '/user/(\d+)', self.delete_user)
        self.add_handler(['PUT', 'POST'], '/user/(\d+)', self.update_user)

    @asyncio.coroutine
    def get_users(self, _header, _body, _qs, _matches, _key):
        """ this and the following functions demonstrate how to handle web service requests.
        It returns a response code, the message body, and a list of extra header lines.

        Note that it is registered in the __init__ function

        :param header: the HttpParse object
        :param body: the request body
        :param qs: a map from the query string (ex ?x=&y=1&y=2&Y&z=4 becomes {y:[1,2],z:[4]})
        :param matches: a list of url parts matches from the handler's regex
        :param key: not used here, but potentially useful for passing off processing to another machine
        """
        return (OK_RESPONSE, json.dumps([self.allusers[x] for x in sorted(self.allusers.keys())]),None)

    @asyncio.coroutine
    def get_user(self, _header, _body, _qs, matches, _key):
        """ get_user's regex is '/user/(\d+)', so matches = [<user id from regex>] """
        return (OK_RESPONSE, json.dumps(self.allusers[matches[0]]), None)

    @asyncio.coroutine
    def delete_user(self, _header, _body, _qs, matches, _key):
        self.allusers.pop(matches[0])
        return (OK_RESPONSE, b'OK', None)

    @asyncio.coroutine
    def update_user(self, _header, body, _qs, matches, _key):
        """ update_user parses the body as a json object """
        update = json.loads(body.decode('utf-8'))
        if not self.allusers[matches[0]]['id'] == update['id']:
            raise Exception()
        self.allusers[matches[0]] = update
        return (OK_RESPONSE, body, None)

    @asyncio.coroutine
    def create_user(self, _header, body, _qs, _matches, _key):
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
        return (CREATED_RESPONSE, json.dumps(newuser), None)

#  Mapping from parser types in the config file to the classes that handle them

SP._parser_map[CONFIGVALUE_HTTPPARSER] = _HTTPStreamParser

if __name__ == '__main__':
    ML.DEBUG = ML.stdout_log
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
