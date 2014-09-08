import asyncio
from utils.database.database import AsyncConnectionPool
import maven_config as MC
import json
CONFIG_DATABASE = 'database'
CONFIG_PERSISTENCE = 'search'
EMPTY_RETURN = [{'id': 000000, 'term': "No Results Found", 'code': 000000, 'type': 'none'}]


class tree_persistance():

    def __init__(self, configname):
        print(MC.MavenConfig)
        self.db = AsyncConnectionPool(MC.MavenConfig[configname][CONFIG_DATABASE])
        self.db.schedule(asyncio.get_event_loop())

    @asyncio.coroutine
    def fetch_rule(self, ruleid):
        cmd = []
        cmd.append("SELECT fullspec, ruleid FROM rules.evirule WHERE ruleid =")
        cmd.append(str(ruleid))
        row = yield from self.db.execute_single(' '.join(cmd) + ';', [])

        result = row.fetchone()
        return result
    @asyncio.coroutine
    def fetch_pathways(self):
        cmd = []
        cmdArgs = []
        cmd.append("SELECT pathid, \"pathName\" FROM protocols.unparsed")
        ret = yield from self.db.execute_single(' '.join(cmd) + ";", cmdArgs)
        return ret
    @asyncio.coroutine
    def create_tree(self, treeJSON):
        cmd = []
        cmdArgs = []
        cmd.append("INSERT INTO protocols.unparsed (\"JSONSpec\", \"pathName\") VALUES (%s, %s) RETURNING pathid")
        viableStr = json.dumps(treeJSON)
        cmdArgs.append(viableStr)
        cmdArgs.append(treeJSON['name'])
        id = yield from self.db.execute_single(' '.join(cmd) + ";", cmdArgs)
        return (id.fetchone()[0])


    @asyncio.coroutine
    def get_tree(self, treeid):
        cmd = []
        cmdArgs = []
        cmd.append("SELECT \"JSONSpec\" from protocols.unparsed WHERE pathid = %s")
        n = int(treeid)
        cmdArgs.append(n)
        json = yield from self.db.execute_single(' '.join(cmd) + ";", cmdArgs)
        result = json.fetchone()
        return result
    @asyncio.coroutine
    def delete_pathway(self, treeid):
        cmd = []
        cmdArgs = []
        cmd.append("DELETE from protocols.unparsed  * WHERE pathid = %s")
        n = int(treeid)
        cmdArgs.append(n)
        json = yield from self.db.execute_single(' '.join(cmd) + ";", cmdArgs)
        return

    @asyncio.coroutine
    def update_tree(self, treeJSON):
        cmd = []
        cmdArgs = []
        cmd.append("UPDATE protocols.unparsed SET (\"JSONSpec\") = (%s) WHERE pathid = %s")
        viableStr = json.dumps(treeJSON)
        cmdArgs.append(viableStr)
        cmdArgs.append(treeJSON['id'])
        yield from self.db.execute_single(' '.join(cmd) + ";", cmdArgs)
        return
