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
EMPTY_RETURN = [{'id':000000, 'term':"No Results Found", 'code':000000, 'type':'none'}]
class tree_persistance():

    def __init__(self, configname):
        print(MC.MavenConfig);
        self.db = AsyncConnectionPool(MC.MavenConfig[configname][CONFIG_DATABASE])
        self.db.schedule(asyncio.get_event_loop())
    @asyncio.coroutine
    def fetch_rule(self, ruleid):

        cmd =[]
        cmd.append("SELECT fullspec, ruleid FROM rules.evirule WHERE ruleid =")
        cmd.append(str(ruleid))
        row = yield from self.db.execute_single(' '.join(cmd) + ';', [])

        result = row.fetchone()
        return result
    @asyncio.coroutine
    def create_tree(self, treeJSON):
        cmd = []
        cmdArgs = []
        cmd.append("INSERT INTO protocols.unparsed (\"JSONSpec\") VALUES (%s) RETURNING pathid")
        cmdArgs. append(str(treeJSON).replace("'", '"'))
        id = yield from self.db.execute_single(' '.join(cmd)+ ";", cmdArgs)
        return (id.fetchone()[0])
    def get_tree(self, treeid):
        cmd = []
        cmdArgs = []
        cmd.append("SELECT \"JSONSpec\" from protocols.unparsed WHERE pathid = %s")
        cmdArgs.append(treeid)
        json = yield from self.db.execute_single(' '.join(cmd)+ ";", cmdArgs)
        return (json.fetchone()[0])
    @asyncio.coroutine
    def update_tree(self, treeJSON):
        cmd = []
        cmdArgs = []
        cmd.append("UPDATE protocols.unparsed SET (\"JSONSpec\") = (%s) WHERE pathid = %s")
        cmdArgs.append(str(treeJSON).replace("'", '"'))
        cmdArgs.append(treeJSON['id'])
        yield from self.db.execute_single(' '.join(cmd)+ ";", cmdArgs)
        return