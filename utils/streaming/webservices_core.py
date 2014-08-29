# *************************************************************************
# Copyright (c) 2014 - Maven Medical
#
# ************************
# AUTHOR:
__author__ = 'Yuki Uchino'
# ************************
# DESCRIPTION:   This file provides the core components required for various
# webservices used by the front-end, mobile, and others.
#
# ************************
# ASSUMES:
# ************************
# SIDE EFFECTS:
# ************************
# LAST MODIFIED FOR JIRA ISSUE: MAV-303
# *************************************************************************
from utils.streaming.http_svcs_wrapper import CONFIG_PERSISTENCE
import asyncio
import maven_config as MC
import utils.database.web_persistence as WP
import utils.database.tree_persistance as TP
import utils.streaming.stream_processor as SP
import utils.streaming.http_responder as HTTP
import utils.streaming.http_helper as HH
from utils.streaming.http_svcs_wrapper import CONTEXT
from functools import partial


def expand_base_class_methods(s, o):
    for b in o.__bases__:
        expand_base_class_methods(s, b)
    s.update([o])
    return s


class WebserviceCore(HTTP.HTTPProcessor):

    def __init__(self, configname):
        HTTP.HTTPProcessor.__init__(self, configname)

        self.helper = HH.HTTPHelper([CONTEXT.USER, CONTEXT.PROVIDER, CONTEXT.CUSTOMERID,
                                     CONTEXT.ROLES], CONTEXT.KEY)

        # self.register_services([AuthenticationWebservices,
        #                        PatientMgmtWebservices,
        #                        UserMgmtWebservices,
        #                        SearchWebservices])

    def schedule(self, loop):
        HTTP.HTTPProcessor.schedule(self, loop)

    def register_services(self, obj):
        obj.helper = self.helper
        for class_with_svcs in expand_base_class_methods(set(), obj.__class__):
            for f in filter(lambda x: (hasattr(x, 'maven_webservice')
                                       and hasattr(x, '__call__')),
                            class_with_svcs.__dict__.values()):
                self.add_handler(f.maven_webservice[0], f.maven_webservice[1], partial(f, obj))


def run():
    from utils.database.database import AsyncConnectionPool

    MC.MavenConfig = \
        {
            "httpserver":
                {
                    SP.CONFIG_HOST: 'localhost',
                    SP.CONFIG_PORT: 8087,
                    CONFIG_PERSISTENCE: "persistence layer",
                },
            'persistence layer': {WP.CONFIG_DATABASE: 'webservices conn pool', },
            'persistance': {TP.CONFIG_DATABASE: 'webservices conn pool'},
            'search': {TP.CONFIG_DATABASE: 'webservices conn pool'},
            'webservices conn pool':
                {
                    AsyncConnectionPool.CONFIG_CONNECTION_STRING: MC.dbconnection,
                    AsyncConnectionPool.CONFIG_MIN_CONNECTIONS: 4,
                    AsyncConnectionPool.CONFIG_MAX_CONNECTIONS: 8
                }
        }
    svc = WebserviceCore('httpserver')
    event_loop = asyncio.get_event_loop()
    svc.schedule(event_loop)
    event_loop.run_forever()

if __name__ == '__main__':
    run()
