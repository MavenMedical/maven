import asyncio
import dateutil
from enum import Enum
from collections import defaultdict
from decimal import Decimal
from datetime import date, datetime
import utils.streaming.stream_processor as SP
from utils.database.database import AsyncConnectionPool
from utils.database.database import MappingUtilites as DBMapUtils
import maven_config as MC

CONFIG_DATABASE = 'database'
CONFIG_PERSISTENCE = 'search'

class web_search():
    @asyncio.coroutine
    def execute(self, cmd, cmdargs):

        print(' '.join(cmd))

        cur = yield from self.db.execute_single(' '.join(cmd)+';', cmdargs)

        results = []
        for row in cur:
            id = int(row[0])
            results.append({'id': id, 'term': row[1], 'type': "snomed", 'code':id})
        print(results)

        return results

    def __init__(self, configname):
        print(MC.MavenConfig);
        self.db = AsyncConnectionPool(MC.MavenConfig[configname][CONFIG_DATABASE])
        self.db.schedule(asyncio.get_event_loop())

    @asyncio.coroutine
    def do_search(self, search_str, search_type):
        print(search_str)
        cmd = []
        ret =""

        cmd.append("SELECT")
        cmd.append("id, term")
        cmd.append("FROM")
        cmd.append("terminology.descriptions")
        cmd.append("WHERE")
        cmd.append("term")
        cmd.append("like")
        cmd.append("'%" + search_str + "%'")
        cmd.append("LIMIT 10")
        print (cmd);
        results = yield from self.execute((cmd), [])
        return results


