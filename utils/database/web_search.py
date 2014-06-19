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


        return results

    def __init__(self, configname):
        print(MC.MavenConfig);
        self.db = AsyncConnectionPool(MC.MavenConfig[configname][CONFIG_DATABASE])
        self.db.schedule(asyncio.get_event_loop())

    @asyncio.coroutine
    def do_search(self, search_str, search_type):
        print(search_str)
        cmd = []


        cmd.append("SELECT DISTINCT")
        cmd.append("id, term")
        cmd.append("FROM")
        cmd.append("terminology.descriptions")
        cmd.append("WHERE")
        cmd.append("term")
        cmd.append("like")
        cmd.append("'%" + search_str + "%'")
        cmd.append("ORDER BY")
        cmd.append("term")
        cmd.append("LIMIT 10")
        print (cmd);
        results = yield from self.execute((cmd), [])
        return results

    @asyncio.coroutine
    def write_db(self, ruleJSON):
        print (ruleJSON)
        cmd = []
        cmd.append("INSERT INTO")
        cmd.append("rules.evirule")
        cmd.append("(ruleid, name, minage, maxage, sex, codetype, fullspec)")
        cmd.append("VALUES")
        cmd.append("(" + str(ruleJSON['id'])+",")
        cmd.append("'"+ str(ruleJSON['name'])+"',")
        cmd.append(str(ruleJSON['minAge'])+",")
        cmd.append(str(ruleJSON['maxAge'])+",")
        cmd.append("'"+str(ruleJSON['genders'])+"',")
        cmd.append("'"+str(ruleJSON['triggerType'])+"',")
        cmd.append("'"+str(ruleJSON).replace("'", '"')+"')")

        print(cmd)


        return x
    @asyncio.coroutine
    def add_to_db(self, ruleJSON):
        print(ruleJSON)
        cmd = []
        cmd.append("INSERT INTO")
        cmd.append("rules.evirule")
        cmd.append("(name, minage, maxage, sex, codetype, fullspec)")
        cmd.append("VALUES(")
        cmd.append("'"+ str(ruleJSON['name'])+"',")
        cmd.append(str(ruleJSON['minAge'])+",")
        cmd.append(str(ruleJSON['maxAge'])+",")
        cmd.append("'"+str(ruleJSON['genders'])+"',")
        cmd.append("'"+str(ruleJSON['triggerType'])+"',")
        cmd.append("'"+str(ruleJSON).replace("'", '"')+"')")
        cmd.append("RETURNING ruleid")
        c = yield from self.db.execute_single(' '.join(cmd)+';', [])
        return c.fetchone()[0]

    @asyncio.coroutine
    def update_db(self, ruleJSON):
        id = ruleJSON['id']
        cmd = []
        cmd.append("UPDATE")
        cmd.append("rules.evirule")
        cmd.append("SET")
        cmd.append("(name, minage, maxage, sex, codetype, fullspec)")
        cmd.append(" = (")
        cmd.append("'"+ str(ruleJSON['name'])+"',")
        cmd.append(str(ruleJSON['minAge'])+",")
        cmd.append(str(ruleJSON['maxAge'])+",")
        cmd.append("'"+str(ruleJSON['genders'])+"',")
        cmd.append("'"+str(ruleJSON['triggerType'])+"',")
        cmd.append("'"+str(ruleJSON).replace("'", '"')+"')")
        cmd.append("WHERE ruleid =")
        cmd.append(str(id));
        yield from self.db.execute_single(' '.join(cmd)+';', [])
        return

    @asyncio.coroutine
    def fetch_rules(self):
        cmd = []
        cmd.append("SELECT ruleid, name FROM rules.evirule")
        rows = yield from self.db.execute_single(' '.join(cmd)+';', [])
        amalgamation = []
        for row in rows:
            amalgamation.append(row);
        return amalgamation;

    @asyncio.coroutine
    def fetch_rule(self, ruleid):

        cmd =[]
        cmd.append("SELECT fullspec, ruleid FROM rules.evirule WHERE ruleid =")
        cmd.append(str(ruleid))
        row = yield from self.db.execute_single(' '.join(cmd) + ';', [])
        result = row.fetchone()
        return result


    @asyncio.coroutine
    def delete_rule(self, ruleid):

        cmd =[]
        cmd.append("DELETE FROM rules.evirule * WHERE ruleid =")
        cmd.append(str(ruleid))
        yield from self.db.execute_single(' '.join(cmd) + ';', [])

        return