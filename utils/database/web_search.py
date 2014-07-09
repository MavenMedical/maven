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
        cmd = []
        cmd_args = []
        if (not search_str):
            return EMPTY_RETURN
        if (search_type == "CPT"):
            cmd.append("SELECT a.cpt_code, a.name FROM public.orderable as a WHERE a.customer_id = -1 AND ord_type = 'Proc' AND a.name @@  %s")
            cmd_args.append(search_str)
            results = yield from self.db.execute_single((' '.join(cmd)), cmd_args)
            ret = []
            if(results.rowcount == 0):
                return EMPTY_RETURN

            for row in results:
                ret.append({'id': row[0], 'term': row[1], 'code': row[0], 'type' : 'CPT'})
            return ret


        if (search_type == "snomed_basic"):
            cmd.append("SET enable_seqscan = off;")
            cmd.append("SELECT x.ancestor, min(x.term),count(*) FROM  (SELECT  b.ancestor,a.term FROM terminology.descriptions a, terminology.conceptancestry b")
            cmd.append("where to_tsvector('maven',term) @@ plainto_tsquery('english', %s)")
            cmd.append("and active=1 and languagecode='en'")
            cmd.append("and a.conceptid=b.ancestor) as x")
            cmd.append("GROUP BY")
            cmd.append("x.ancestor")
            cmd.append("ORDER BY count DESC")
            cmd.append("LIMIT 25")
            cmd_args.append(search_str)
            results = yield from self.db.execute_single((' '.join(cmd)), cmd_args)
            if(results.rowcount == 0):
                return EMPTY_RETURN
            ret = []
            for row in results:
                 ret.append({'id': int(row[0]), 'term': row[1], 'code': int(row[0]), 'type' : 'snomed'})
            return ret


        if (search_type == "snomed_zoom_in"):
            cmd_args = []
            cmd = []
            cmd.append("SET enable_seqscan = off;")
            cmd.append("select distinct  a.conceptid, max(a.term), min(b.count) from terminology.descriptions as a, (select distinct CA.ancestor, count(*) from (select sourceid from terminology.relationships as CA  where destinationid = %s AND relationshipgroup = 0)  AS results,")
            cmd.append("terminology.conceptancestry as CA WHERE results.sourceid = CA.ancestor")
            cmd.append("GROUP BY CA.ancestor")
            cmd.append(") as b")
            cmd.append("WHERE b.ancestor = a.conceptid")
            cmd.append("GROUP BY a.conceptid")
            cmd.append("ORDER BY min(count) DESC")
            cmd.append("LIMIT 30")
            cmd_args.append(search_str)
            ret = []
            results = yield from self.db.execute_single((' '.join(cmd)), cmd_args)
            if(results.rowcount == 0):
                return EMPTY_RETURN
            for row in results:
                ret.append({'id': int(row[0]), 'term': row[1], 'code': int(row[0]), 'type' : 'snomed'})
            return ret

        elif (search_type.split("_")[0] == "snomed" ):

            print("QUERYING")
            cmd.append("SET enable_seqscan = off;")
            cmd.append("SELECT x.ancestor, min(x.term),count(*) FROM  (SELECT  b.ancestor,a.term FROM terminology.descriptions a, terminology.conceptancestry b")
            cmd.append("WHERE to_tsvector('maven',term) @@ plainto_tsquery('english', %s)")
            cmd.append("AND active=1 and languagecode='en'")
            cmd.append("AND a.conceptid  = b.ancestor")
            cmd.append("AND a.conceptid IN (SELECT child FROM terminology.conceptancestry b WHERE b.ancestor = %s)) AS x")
            cmd.append("GROUP BY")
            cmd.append("x.ancestor")
            cmd.append("ORDER BY count DESC")
            cmd.append("LIMIT 25")
            cmd_args.append(search_str)

            snomed_type = search_type.split("_")[1]
            if (snomed_type == 'drug'):
                cmd_args.append(373873005)
            if (snomed_type == 'diagnosis'):
                cmd_args.append(404684003)

            results = yield from self.db.execute_single((' '.join(cmd)), cmd_args)
            ret = []
            if(results.rowcount == 0):
                return EMPTY_RETURN
            for row in results:
                 ret.append({'id': int(row[0]), 'term': row[1], 'code': int(row[0]), 'type' : 'snomed'})
            return ret

        if (search_type == "loinc"):


            cmd.append("SELECT loinc_num, component FROM terminology.loinc WHERE to_tsvector('maven', component) @@ plainto_tsquery('english', %s)")
            cmd.append("LIMIT 50")
            cmd_args.append(search_str)

            ret = []
            results = yield from self.db.execute_single(' '.join(cmd), cmd_args )
            if(results.rowcount == 0):
                return EMPTY_RETURN
            for row in results:
                ret.append({'id': row[0], 'term': row[1], 'type':'loinc'})
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


        cmd = []
        cmd.append("DELETE FROM rules.codelists * WHERE ruleid = ")
        cmd.append(str(id))
        yield from self.db.execute_single(' '.join(cmd)+';', [])
        yield from (self.writeExplicitSnomed('hist_dx', ruleJSON))
        yield from self.writeExplicitSnomed('pl_dx', ruleJSON)
        yield from self.writeExplicitSnomed('enc_dx', ruleJSON)
        yield from self.writeExplicitSnomed('enc_pl_dx', ruleJSON)
        yield from self.writeExplicitCPT('hist_proc', ruleJSON)
        yield from self.writeExplicitCPT('enc_proc', ruleJSON)
        if (ruleJSON['triggerType'] == 'drug'):
            yield from self.writeDrugTriggers(ruleJSON)
        elif (ruleJSON['triggerType'] == 'proc'):
            yield from self.writeCPTTriggers(ruleJSON)
        yield from self.writeLabs(ruleJSON)
        return
    @asyncio.coroutine
    def writeExplicitSnomed(self, type, rule):
        list = rule.get(type, None)
        id = rule['id']

        if (list):
            cmd = []
            cmdArgs = []
            pos = []
            neg = []
            for cur in list:
                 cmd = []
                 cmdArgs = []
                 if (type.split('_')[0] == 'hist'):
                     cmd.append("INSERT INTO rules.codelists")
                     cmd.append("(ruleid, listtype, isintersect, intlist, framemin, framemax)")
                     print (cmd)
                     cmd.append("(SELECT %s, %s, %s, array_agg(child) , %s, %s FROM terminology.conceptancestry WHERE ancestor = %s)")
                     cmdArgs.append(str(id))
                     cmdArgs.append(str(type))
                     cmdArgs.append(cur['negative']=='true')
                     cmdArgs.append(cur['minDays'])
                     cmdArgs.append(cur['maxDays'])
                     cmdArgs.append(cur['code'])
                 else:
                     cmd.append("INSERT INTO rules.codelists")
                     cmd.append("(ruleid, listtype, isintersect, intlist)")
                     cmd.append("(SELECT %s, %s, %s, array_agg(child) FROM terminology.conceptancestry WHERE ancestor = %s)")
                     cmdArgs.append(str(id))
                     cmdArgs.append(str(type))
                     cmdArgs.append(cur['negative']=='true')
                     cmdArgs.append(cur['code'])
                 yield from self.db.execute_single(' '.join(cmd)+';', cmdArgs)



        return
    @asyncio.coroutine
    def writeExplicitCPT(self, type, rule):
        list = rule.get(type, None)
        id = rule['id']

        if (list):
            cmd = []
            cmdArgs = []
            pos = []
            neg = []
            for cur in list:
                 cmd = []
                 cmdArgs = []
                 if (type.split('_')[0] == 'hist'):
                     cmd.append("INSERT INTO rules.codelists")
                     cmd.append("(ruleid, listtype, isintersect, intlist, framemin, framemax)")
                     cmd.append("(SELECT %s, %s, %s, %s, %s, %s)")
                     cmdArgs.append(str(id))
                     cmdArgs.append(str(type))
                     cmdArgs.append(cur['negative']=='true')
                     cmdArgs.append([int(cur['code'])])
                     cmdArgs.append(cur['minDays'])
                     cmdArgs.append(cur['maxDays'])
                 else:
                     cmd.append("INSERT INTO rules.codelists")
                     cmd.append("(ruleid, listtype, intlist, isintersect)")
                     cmd.append("(SELECT %s, %s, %s, %s)")
                     cmdArgs.append(str(id))
                     cmdArgs.append(str(type))
                     cmdArgs.append([int(cur['code'])])
                     cmdArgs.append(cur['negative']=='true')
                 yield from self.db.execute_single(' '.join(cmd)+';', cmdArgs)



    @asyncio.coroutine
    def writeDrugTriggers(self, rule):

          for cur in rule['triggers']:
            cmd = [];
            cmdArgs = []
            NDC = []
            cmd.append("INSERT INTO rules.trigcodes (ruleid, code) ")
            cmd.append("(select distinct %s ndc from terminology.drugclassancestry a "
                       "inner join terminology.drugclass b on a.classaui=b.rxaui "
                       "inner join terminology.conceptancestry c on b.snomedid=c.child "
                       "where c.ancestor=%s)")
            cmdArgs.append(str(rule['id']))
            cmdArgs.append(cur['code'])

            yield from self.db.execute_single(' '.join(cmd)+";", cmdArgs)
          return
    @asyncio.coroutine
    def writeCPTTriggers(self, rule):
          for cur in rule['triggers']:
            cmd = [];
            cmdArgs = []
            NDC = []
            cmd.append("INSERT INTO rules.trigcodes (ruleid, code) ")
            cmd.append("SELECT %s, %s")
            cmdArgs.append(str(rule['id']))
            cmdArgs.append(cur['code'])

            yield from self.db.execute_single(' '.join(cmd)+";", cmdArgs)
          return
    @asyncio.coroutine
    def writeLabs(self, rule):
        labs =  rule.get('lab', None)

        id = rule['id']

        delete = "DELETE FROM rules.labeval * WHERE ruleid = %s;"
        yield from self.db.execute_single(delete, [id])
        if labs:
            for lab in labs:
                cmd =[]
                cmdArgs =[]
                cmd.append("INSERT INTO rules.labeval")
                cmd.append("(ruleid, loinc_codes, threshold, relation, framemin, framemax, defaultval)")
                cmd.append("(SELECT %s, %s, %s, %s, %s, %s, %s)")
                cmdArgs.append(id)
                print (lab['obs_type'])
                cmdArgs.append(lab['obs_type'])
                cmdArgs.append(lab['value'])
                cmdArgs.append(lab['relation'])
                cmdArgs.append(lab['mindays'])
                cmdArgs.append(lab['maxdays'])
                cmdArgs.append(lab['defaultval'])
                yield from self.db.execute_single(' '.join(cmd) + ';', cmdArgs)

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
        cmd =[]
        cmd.append("DELETE FROM rules.labeval * WHERE ruleid =")
        cmd.append(str(ruleid))
        yield from self.db.execute_single(' '.join(cmd) + ';', [])
        return