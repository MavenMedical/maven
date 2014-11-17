# *************************************************************************
# Copyright (c) 2014 - Maven Medical
#
# ************************
# AUTHOR:
__author__ = 'Yuki Uchino'
# ************************
# DESCRIPTION:   Create an rpc listener for the database server
#
# ************************
# ASSUMES:
# ************************
# SIDE EFFECTS:
# ************************
# LAST MODIFIED FOR JIRA ISSUE: MAV-1
# *************************************************************************
from utils.streaming import stream_processor as SP
import utils.streaming.rpc_processor as RP
from utils.enums import CONFIG_PARAMS
from utils.database.database import AsyncConnectionPool
import asyncio
import maven_config as MC
import utils.database.web_persistence as WP
import utils.database.web_search as WS


def main(loop):

    rpc_server_stream_processor = 'Database Server RPC Stream Processor'

    MavenConfig = {
        rpc_server_stream_processor: {
            SP.CONFIG_WRITERTYPE: SP.CONFIGVALUE_ASYNCIOSOCKETREPLY,
            SP.CONFIG_WRITERNAME: rpc_server_stream_processor + '.Writer2',
            SP.CONFIG_READERTYPE: SP.CONFIGVALUE_ASYNCIOSERVERSOCKET,
            SP.CONFIG_READERNAME: rpc_server_stream_processor + '.Reader2',
            SP.CONFIG_WRITERDYNAMICKEY: 2,
            SP.CONFIG_DEFAULTWRITEKEY: 2,
        },
        rpc_server_stream_processor + '.Writer2': {
            SP.CONFIG_WRITERKEY: 2,
        },
        rpc_server_stream_processor + '.Reader2': {
            SP.CONFIG_PORT: '54729',
        },
        CONFIG_PARAMS.PERSISTENCE_SVC.value: {
            WP.CONFIG_DATABASE: CONFIG_PARAMS.DATABASE_SVC.value, },
        CONFIG_PARAMS.DATABASE_SVC.value:
        {
            AsyncConnectionPool.CONFIG_CONNECTION_STRING: MC.dbconnection,
            AsyncConnectionPool.CONFIG_MIN_CONNECTIONS: 4,
            AsyncConnectionPool.CONFIG_MAX_CONNECTIONS: 16
        },
    }
    MC.MavenConfig.update(MavenConfig)

    persistence = WP.WebPersistenceBase(CONFIG_PARAMS.PERSISTENCE_SVC.value)
    persistence.schedule()
    search = WS.web_search_base(CONFIG_PARAMS.PERSISTENCE_SVC.value)

    rpc = RP.rpc(rpc_server_stream_processor)
    rpc.schedule(loop)

    rpc.register(persistence)
    rpc.register(search)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    main(loop)
