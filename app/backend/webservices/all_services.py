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
from app.backend.webservices.transparent import TransparentWebservices
from app.backend.webservices.pathways import PathwaysWebservices
from app.backend.webservices.authentication import AuthenticationWebservices
from app.backend.webservices.patient_mgmt import PatientMgmtWebservices
from app.backend.webservices.user_mgmt import UserMgmtWebservices
from app.backend.webservices.search import SearchWebservices
import utils.streaming.stream_processor as SP
import utils.database.tree_persistance as TP
import utils.streaming.webservices_core as WC
import utils.database.web_persistence as WP
import asyncio
import maven_config as MC
from utils.streaming.http_svcs_wrapper import CONFIG_PERSISTENCE


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
    core_scvs = WC.WebserviceCore('httpserver')
    for c in [AuthenticationWebservices, PatientMgmtWebservices,
              UserMgmtWebservices, SearchWebservices,
              TransparentWebservices, PathwaysWebservices]:
        print(c)
        core_scvs.register_services(c('httpserver'))

    event_loop = asyncio.get_event_loop()
    core_scvs.schedule(event_loop)
    event_loop.run_forever()

if __name__ == '__main__':
    run()
