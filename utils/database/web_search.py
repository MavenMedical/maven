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
        results = yield from self.db.execute_single((' '.join(cmd)), [])
        print (results);
        ret = []
        for row in results:
            ret.append({'id': int(row[0]), 'term': row[1], 'code': int(row[0]), 'type' : 'snomed'})
        return ret

    @asyncio.coroutine
    def add_to_db(self, ruleJSON):
        print(ruleJSON)
        cmd = []
        cmdArgs = []
        cmd.append("INSERT INTO")
        cmd.append("rules.evirule")
        cmd.append("(name, minage, maxage, sex, codetype, fullspec)")
        cmd.append("VALUES(%s, %s, %s, %s, %s, %s)")
        cmdArgs.append(str(ruleJSON['name']))
        cmdArgs.append(str(ruleJSON['minAge']))
        cmdArgs.append(str(ruleJSON['maxAge']))
        cmdArgs.append(str(ruleJSON['genders']))
        cmdArgs.append(str(ruleJSON['triggerType']))
        cmdArgs.append(str(ruleJSON).replace("'", '"'))

     #   cmd.append("'"+ str(ruleJSON['name'])+"',")
     #   cmd.append(str(ruleJSON['minAge'])+",")
     #   cmd.append(str(ruleJSON['maxAge'])+",")
     #   cmd.append("'"+str(ruleJSON['genders'])+"',")
     #   cmd.append("'"+str(ruleJSON['triggerType'])+"',")
     #   cmd.append("'"+str(ruleJSON).replace("'", '"')+"')")


        cmd.append("RETURNING ruleid")
        c = yield from self.db.execute_single(' '.join(cmd)+';', cmdArgs)
        return c.fetchone()[0]

    @asyncio.coroutine
    def update_db(self, ruleJSON):
        id = ruleJSON['id']
        cmd = []
        cmdArgs = []
        cmd.append("UPDATE")
        cmd.append("rules.evirule")
        cmd.append("SET")
        cmd.append("(name, minage, maxage, sex, codetype, fullspec)")
        cmd.append(" = (%s, %s, %s, %s, %s, %s)")
        cmdArgs.append(str(ruleJSON['name']))
        cmdArgs.append(str(ruleJSON['minAge']))
        cmdArgs.append(str(ruleJSON['maxAge']))
        cmdArgs.append(str(ruleJSON['genders']))
        cmdArgs.append(str(ruleJSON['triggerType']))
        cmdArgs.append(str(ruleJSON).replace("'", '"'))
        cmd.append("WHERE ruleid =")
        cmd.append(str(id));
        yield from self.db.execute_single(' '.join(cmd)+';', cmdArgs)
        cmd = []

        triggers = ruleJSON['triggers']
        cmd.append("DELETE FROM rules.trigcodes * where ruleid = ")
        cmd.append(str(id));
        yield from self.db.execute_single(' '.join(cmd)+';', [])

        for cur in triggers:
            cmd = [];
            cmdArgs = []
            cmd.append("INSERT INTO rules.trigcodes (ruleid, code) ")
            cmd.append("VALUES")
            cmd.append("(%s, %s)")
            cmdArgs.append(str(id))
            cmdArgs.append(cur['code']);
            yield from self.db.execute_single(' '.join(cmd)+';', cmdArgs)
        cmd = []
        cmd.append("DELETE FROM rules.codelists * WHERE ruleid = ")
        cmd.append(str(id))
        yield from self.db.execute_single(' '.join(cmd)+';', [])
        yield from (self.writeExplicit('hist_dx', ruleJSON))
        yield from self.writeExplicit('pl_dx', ruleJSON)
        yield from self.writeExplicit('enc_dx', ruleJSON)

        return
    @asyncio.coroutine
    def writeExplicit(self, type, rule):
        print("TESTTTTT")
        list = rule.get(type, None)
        id = rule['id']
        if (list):
            pos = []
            neg = []
            for cur in list:
                if (cur['negative']):
                    neg.append(cur['code'])
                else:
                    pos.append(cur['code'])

            cmd = []
            cmdArgs = []

            cmd.append("INSERT INTO rules.codelists")
            cmd.append("(ruleid, listtype, isintersect, intlist)")
            cmd.append("VALUES")
            cmd.append("(%s, %s, true, %s)")
            cmdArgs.append(str(id))
            cmdArgs.append(str(type))
            cmdArgs.append(self.toSQLArray(neg))

            yield from self.db.execute_single(' '.join(cmd)+';', cmdArgs)

            cmd = []
            cmdArgs = []

            cmd.append("INSERT INTO rules.codelists")
            cmd.append("(ruleid, listtype, isintersect, intlist)")
            cmd.append("VALUES")
            cmd.append("(%s, %s, false, %s)")
            cmdArgs.append(str(id))
            cmdArgs.append(str(type))

            cmdArgs.append(self.toSQLArray(pos))

            yield from self.db.execute_single(' '.join(cmd)+';', cmdArgs)
            return

    def toSQLArray(self, toChange):
        ret =[]
        for cur in toChange:
            ret.append(cur)
        return '{' + (' ,'.join(ret)) + '}'

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
        cmd =[]
        cmd.append("DELETE FROM rules.trigCodes * WHERE ruleid =")
        cmd.append(str(ruleid))
        yield from self.db.execute_single(' '.join(cmd) + ';', [])
        cmd =[]
        cmd.append("DELETE FROM rules.codelists * WHERE ruleid =")
        cmd.append(str(ruleid))
        yield from self.db.execute_single(' '.join(cmd) + ';', [])

        return