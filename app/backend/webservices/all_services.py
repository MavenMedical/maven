# *************************************************************************
# Copyright (c) 2014 - Maven Medical
#
# ************************
# AUTHOR:
__author__ = 'Yuki Uchino'
# ************************
# DESCRIPTION:   This file provides the webservice calls required for Maven Transparent functionality
#
# ************************
# ASSUMES:
# ************************
# SIDE EFFECTS:
# ************************
# LAST MODIFIED FOR JIRA ISSUE: MAV-303
# *************************************************************************
from utils.streaming.webservices_core import *
from app.backend.webservices.transparent import TransparentWebservices
from app.backend.webservices.pathways import PathwaysWebservices


class AllWebservices(WebserviceCore, PathwaysWebservices, TransparentWebservices):

    def __init__(self, configname):

        # Run the init method (which contains pretty much all set-up)
        super(AllWebservices, self).__init__(configname)

        # Loop through each base classes's functions and find the functions that were decorated with @http_service
        # and add them as handlers
        for base_class in expand_base_class_methods(set(), self.__class__):
            for f in filter(lambda x: (hasattr(x, 'maven_webservice') and hasattr(x, '__call__')), base_class.__dict__.values()):
                self.add_handler(f.maven_webservice[0], f.maven_webservice[1], partial(f, self))


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
    scvs = AllWebservices('httpserver')
    event_loop = asyncio.get_event_loop()
    scvs.schedule(event_loop)
    event_loop.run_forever()

if __name__ == '__main__':
    run()
