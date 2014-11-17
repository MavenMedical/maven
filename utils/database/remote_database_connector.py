from functools import lru_cache
from utils.streaming.rpc_processor import rpc
import asyncio


@lru_cache()
def RemoteDatabaseConnector(configname):
    WebPersistenceServer = rpc(configname)
    print(configname)
    WebPersistenceServer.schedule(asyncio.get_event_loop())
    return WebPersistenceServer
