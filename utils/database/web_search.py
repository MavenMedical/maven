import asyncio
from utils.database.database import AsyncConnectionPool
import maven_config as MC
from utils.database.remote_database_connector import RemoteDatabaseConnector
from functools import lru_cache
CONFIG_DATABASE = 'database'
CONFIG_PERSISTENCE = 'search'
EMPTY_RETURN = [{'id': 000000, 'term': "No Results Found", 'code': 000000, 'type': 'none'}]


@lru_cache()
def web_search(configname):
    server = RemoteDatabaseConnector(MC.MavenConfig[configname][CONFIG_DATABASE])
    ret = server.create_client(web_search_base)
    ret.schedule = lambda *args: None
    return ret


class web_search_base():

    @asyncio.coroutine
    def get_routes(self):
        cmd = []
        cmd_args = []
        cmd.append("SELECT DISTINCT routename FROM terminology.drugclassancestry ORDER BY routename ASC")
        results = yield from self.db.execute_single((' '.join(cmd)), cmd_args)
        arr = []
        for row in results:
            arr.append({'term': row[0]})
        return arr

    def __init__(self, configname):
        print(MC.MavenConfig)
        self.db = AsyncConnectionPool(MC.MavenConfig[configname][CONFIG_DATABASE])
        self.db.schedule(asyncio.get_event_loop())

    @asyncio.coroutine
    def do_search(self, search_str, search_type):
        cmd = []
        cmd_args = []
        if (not search_str):
            return EMPTY_RETURN
        if (search_type == "CPT"):
            cmd.append("SELECT DISTINCT a.cpt_code, a.name FROM public.orderable as a WHERE a.customer_id = -1 AND ord_type = 'Proc' AND (to_tsvector('maven', a.name) @@  plainto_tsquery('maven', %s) OR a.cpt_code = %s) ORDER BY a.name ASC LIMIT 100 ")
            cmd_args.append(search_str)
            cmd_args.append(search_str)
            results = yield from self.db.execute_single((' '.join(cmd)), cmd_args)
            ret = []
            if(results.rowcount == 0):
                return EMPTY_RETURN

            for row in results:
                ret.append({'id': row[0], 'term': row[1], 'code': row[0], 'type': 'CPT'})
            return ret

        if (search_type == "snomed_basic"):
            cmd.append("SET enable_seqscan = off;")
            cmd.append("SELECT x.ancestor, min(x.term),count(*) FROM  (SELECT  b.ancestor,a.term FROM terminology.descriptions a, terminology.conceptancestry b")
            cmd.append("WHERE (to_tsvector('maven',term) @@ plainto_tsquery('maven', %s) OR conceptid = %s)")
            cmd.append("AND active=1 and languagecode='en'")
            cmd.append("AND a.conceptid=b.ancestor) as x")
            cmd.append("GROUP BY")
            cmd.append("x.ancestor")
            cmd.append("ORDER BY count DESC")
            cmd.append("LIMIT 25")
            cmd_args.append(search_str)
            cmd_args.append(search_str)
            results = yield from self.db.execute_single((' '.join(cmd)), cmd_args)
            if(results.rowcount == 0):
                return EMPTY_RETURN
            ret = []
            for row in results:
                 ret.append({'id': int(row[0]), 'term': row[1], 'code': int(row[0]), 'type': 'snomed'})
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

        if (search_type == "snomed_zoom_out"):
            cmd_args = []
            cmd = []
            cmd.append("SELECT DISTINCT max(conceptid) as code, max(term) as term FROM terminology.descriptions AS a INNER JOIN terminology.relationships as b on a.conceptid = b.destinationid WHERE b.sourceid = %s AND b.relationshipgroup = 0 GROUP BY conceptid")
            cmd_args.append(search_str)
            ret = []
            results = yield from self.db.execute_single((' '.join(cmd)), cmd_args)
            if(results.rowcount == 0):
                return EMPTY_RETURN
            for row in results:
                ret.append({'id': int(row[0]), 'term': row[1], 'code': int(row[0]), 'type': 'snomed'})
            return ret

        elif (search_type.split("_")[0] == "snomed"):

            print("QUERYING")
            cmd.append("SET enable_seqscan = off;")
            cmd.append("SELECT x.ancestor, min(x.term),count(*) FROM  (SELECT  b.ancestor,a.term FROM terminology.descriptions a, terminology.conceptancestry b")
            cmd.append("WHERE (to_tsvector('maven',term) @@ plainto_tsquery('maven', %s))")
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
                 ret.append({'id': int(row[0]), 'term': row[1], 'code': int(row[0]), 'type': 'snomed'})
            return ret

        if (search_type == "loinc"):


            cmd.append("SELECT loinc_num, component FROM terminology.loinc WHERE to_tsvector('maven', component) @@ plainto_tsquery('maven', %s) OR loinc_num = %s ")
            cmd.append("LIMIT 50")
            cmd_args.append(search_str)
            cmd_args.append(search_str)
            ret = []
            results = yield from self.db.execute_single(' '.join(cmd), cmd_args)
            if(results.rowcount == 0):
                return EMPTY_RETURN
            for row in results:
                ret.append({'id': row[0], 'term': row[1], 'type': 'loinc'})
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
        cmd.append(str(id))
        yield from self.db.execute_single(' '.join(cmd)+';', cmdArgs)
        cmd = []

        # triggers = ruleJSON['triggers']
        cmd.append("DELETE FROM rules.trigcodes * where ruleid = ")
        cmd.append(str(id))
        yield from self.db.execute_single(' '.join(cmd)+';', [])

        cmd = []
        cmd.append("DELETE FROM rules.codelists * WHERE ruleid = ")
        cmd.append(str(id))
        yield from self.db.execute_single(' '.join(cmd)+';', [])
        count = 0

        count += yield from (self.writeExplicitSnomed('hist_dx', ruleJSON))
        count += yield from self.writeExplicitSnomed('pl_dx', ruleJSON)
        count += yield from self.writeExplicitSnomed('enc_dx', ruleJSON)
        count += yield from self.writeExplicitSnomed('enc_pl_dx', ruleJSON)
        count += yield from self.writeExplicitNDC('ml_med', ruleJSON)
        count += yield from self.writeExplicitCPT('hist_proc', ruleJSON)
        count += yield from self.writeExplicitCPT('enc_proc', ruleJSON)

        cmd = []
        cmdArgs = []
        cmd.append("SELECT distinct a.detailid, b.detailid from rules.codelists a, rules.codelists b  where a.ruleid=b.ruleid and a.isintersect='t' and  b.isintersect='f'"
                       " and a.intlist && b.intlist and "
                       "("
                       "   (a.listtype = 'enc_dx' and b.listtype in ('enc_dx', 'enc_pl_dx')) "
                       "OR (a.listtype = 'pl_dx' AND b.listtype in ('pl_dx', 'enc_pl_dx')) "
                       "OR (a.listtype = 'enc_pl_dx' AND b.listtype in ('pl_dx', 'enc_pl_dx', 'enc_dx'))"
                       ")")

        result = yield from self.db.execute_single(' '.join(cmd) + ';', cmdArgs)
        conflicts = []
        for row in result:
            print(row)
            conflicts.append(row)

        if count == 0:
            cmd = []
            cmdArgs = []
            cmd.append("insert into rules.codelists (ruleid, listtype, isintersect, intlist)")
            cmd.append("(select %s, 'pl_dx', false, array[-99999])")
            cmdArgs.append(ruleJSON['id'])
            yield from self.db.execute_single(' '.join(cmd)+';', cmdArgs)
        if (ruleJSON['triggerType'] == 'NDC'):
            yield from self.writeDrugTriggers(ruleJSON)
        elif (ruleJSON['triggerType'] == 'HCPCS'):
            yield from self.writeCPTTriggers(ruleJSON)
        yield from self.writeLabs(ruleJSON)
        return conflicts

    @asyncio.coroutine
    def writeExplicitSnomed(self, type, rule):
        list = rule.get(type, None)
        id = rule['id']

        if (list):
            cmd = []
            cmdArgs = []
            for cur in list:
                cmd = []
                cmdArgs = []
                if (type.split('_')[0] == 'hist'):
                    cmd.append("INSERT INTO rules.codelists")
                    cmd.append("(ruleid, listtype, isintersect, intlist, framemin, framemax,  detailid)")
                    print(cmd)
                    cmd.append("(SELECT %s, %s, %s, array_agg(child) , %s, %s, %s FROM terminology.conceptancestry WHERE ancestor in %s)")
                    cmdArgs.append(str(id))
                    cmdArgs.append(str(type))
                    cmdArgs.append(cur['exists'] == 'true')
                    cmdArgs.append(cur['minDays'])
                    cmdArgs.append(cur['maxDays'])
                    #    cmdArgs.append(str(cur['codeterm']))
                    cmdArgs.append(cur['did'])
                    cmdArgs.append(tuple(cur['code']))

                else:
                    cmd.append("INSERT INTO rules.codelists")
                    cmd.append("(ruleid, listtype, isintersect, intlist,  detailid)")
                    cmd.append("(SELECT %s, %s, %s, array_agg(child),  %s FROM terminology.conceptancestry WHERE ancestor IN %s )RETURNING detailid ")
                    cmdArgs.append(str(id))
                    cmdArgs.append(str(type))
                    cmdArgs.append(cur['exists'] == 'true')
                    #    cmdArgs.append(str(cur['codeterm']))
                    cmdArgs.append(cur['did'])
                    cmdArgs.append(tuple(cur['code']))

                yield from self.db.execute_single(' '.join(cmd) + ';', cmdArgs)

            return (1)
        return 0

    @asyncio.coroutine
    def writeExplicitCPT(self, type, rule):

        list = rule.get(type, None)
        id = rule['id']

        if (list):
            cmd = []
            cmdArgs = []
            for cur in list:
                cmd = []
                cmdArgs = []
                if (type.split('_')[0] == 'hist'):
                    cmd.append("INSERT INTO rules.codelists")
                    cmd.append("(ruleid, listtype, isintersect, intlist, framemin, framemax)")
                    cmd.append("(SELECT %s, %s, %s, %s, %s, %s)")
                    cmdArgs.append(str(id))
                    cmdArgs.append(str(type))
                    cmdArgs.append(cur['exists'] == 'true')
                    desired_array = [int(numeric_string) for numeric_string in cur['code']]
                    cmdArgs.append(desired_array)
                    cmdArgs.append(cur['minDays'])
                    cmdArgs.append(cur['maxDays'])
                else:
                    cmd.append("INSERT INTO rules.codelists")
                    cmd.append("(ruleid, listtype, intlist, isintersect)")
                    cmd.append("(SELECT %s, %s, %s, %s)")
                    cmdArgs.append(str(id))
                    cmdArgs.append(str(type))
                    desired_array = [int(numeric_string) for numeric_string in cur['code']]
                    cmdArgs.append(desired_array)
                    cmdArgs.append(cur['exists'] == 'true')

                yield from self.db.execute_single(' '.join(cmd)+';', cmdArgs)
                return 1

        return 0

    @asyncio.coroutine
    def writeExplicitNDC(self, type, rule):
        list = rule.get(type, None)
        id = rule['id']

        if (list):
            cmd = []
            cmdArgs = []
            for cur in list:
                cmd = []
                cmdArgs = []

                cmd.append("INSERT INTO rules.codelists")
                cmd.append("(ruleid, listtype, strlist, isintersect)")
                cmd.append("(SELECT %s, %s, array_agg(ndc), %s FROM (SELECT ndc FROM  "
                           " terminology.conceptancestry b inner join terminology.rxsnomeds a on b.child=a.snomed"
                           " inner join terminology.rxnrel c on a.rxcui=c.rxcui1 and c.rela='dose_form_of'"
                           " where b.ancestor in %s"
                           " and c.rxcui2 in (select rxcui from terminology.doseformgroups where"
                           " groupname like %s)"
                           " GROUP BY NDC) as x)")
                cmdArgs.append(id)
                cmdArgs.append(str(type))

                cmdArgs.append(cur['exists'] == 'true')
                cmdArgs.append(tuple(cur['code']))
                cmdArgs.append(cur['route'])
                yield from self.db.execute_single(' '.join(cmd)+';', cmdArgs)
            return 1
        return 0

    @asyncio.coroutine
    def writeDrugTriggers(self, rule):
        ndcs = {}

        for cur in rule['triggers']:
            r = cur['route']
            i = cur['code']
            if r in ndcs:
                ndcs[r].append(i)
            else:
                ndcs[r] = [i]
        cmd = []
        cmdArgs = []
        union = False
        cmd.append("INSERT INTO rules.trigcodes (ruleid, code) ")
        for cur in ndcs:

            if union:
                cmd.append('UNION')
            union = True
            cmd.append("(SELECT %s, ndc FROM "
                       " terminology.conceptancestry b inner join terminology.rxsnomeds a on b.child=a.snomed"
                       " inner join terminology.rxnrel c on a.rxcui=c.rxcui1 and c.rela='dose_form_of'"
                       " left outer join rules.trigcodes t on ndc = t.code "
                       " where b.ancestor in %s"
                       " and c.rxcui2 in (select rxcui from terminology.doseformgroups where"
                       " groupname like %s)"
                       #      " and NOT (ruleid = %s AND code notNull))"
                       " GROUP BY NDC)")
            cmdArgs.append(rule['id'])
            cmdArgs.append(tuple(ndcs[cur]))
            cmdArgs.append(cur)
            # cmdArgs.append(rule['id'])

        yield from self.db.execute_single(' '.join(cmd)+";", cmdArgs)

        return

    @asyncio.coroutine
    def writeCPTTriggers(self, rule):
        for cur in rule['triggers']:
            cmd = []
            cmdArgs = []
            cmd.append("INSERT INTO rules.trigcodes (ruleid, code) ")
            cmd.append("SELECT %s, %s")
            cmdArgs.append(str(rule['id']))
            cmdArgs.append(cur['code'])

            yield from self.db.execute_single(' '.join(cmd)+";", cmdArgs)
        return

    @asyncio.coroutine
    def writeLabs(self, rule):
        labs = rule.get('lab', None)

        id = rule['id']

        delete = "DELETE FROM rules.labeval * WHERE ruleid = %s;"
        yield from self.db.execute_single(delete, [id])
        if labs:
            for lab in labs:
                cmd = []
                cmdArgs = []
                cmd.append("INSERT INTO rules.labeval")
                cmd.append("(ruleid, loinc_codes, threshold, relation, framemin, framemax, defaultval, onlyCheckLast)")
                cmd.append("(SELECT %s, %s, %s, %s, %s, %s, %s, %s)")
                cmdArgs.append(id)
                print(lab['obs_type'])
                cmdArgs.append(lab['obs_type'])
                cmdArgs.append(lab['value'])
                cmdArgs.append(lab['relation'])
                cmdArgs.append(lab['mindays'])
                cmdArgs.append(lab['maxdays'])
                cmdArgs.append(lab['defaultval'])
                cmdArgs.append(lab['lastlab'])
                yield from self.db.execute_single(' '.join(cmd) + ';', cmdArgs)

        return

    def toSQLArray(self, toChange):
        ret = []
        for cur in toChange:
            ret.append(cur)
        return '{' + (' ,'.join(ret)) + '}'

    @asyncio.coroutine
    def fetch_rules(self):
        cmd = []
        cmd.append("SELECT ruleid, name FROM rules.evirule ORDER BY name asc")
        rows = yield from self.db.execute_single(' '.join(cmd)+';', [])
        amalgamation = []
        for row in rows:
            amalgamation.append(row)
        return amalgamation

    @asyncio.coroutine
    def fetch_rule(self, ruleid):

        cmd = []
        cmd.append("SELECT fullspec, ruleid FROM rules.evirule WHERE ruleid =")
        cmd.append(str(ruleid))
        row = yield from self.db.execute_single(' '.join(cmd) + ';', [])

        result = row.fetchone()
        return result

    @asyncio.coroutine
    def delete_rule(self, ruleid):

        cmd = []
        cmd.append("DELETE FROM rules.evirule * WHERE ruleid =")
        cmd.append(str(ruleid))
        yield from self.db.execute_single(' '.join(cmd) + ';', [])
        cmd = []
        cmd.append("DELETE FROM rules.trigCodes * WHERE ruleid =")
        cmd.append(str(ruleid))
        yield from self.db.execute_single(' '.join(cmd) + ';', [])
        cmd = []
        cmd.append("DELETE FROM rules.codelists * WHERE ruleid =")
        cmd.append(str(ruleid))
        yield from self.db.execute_single(' '.join(cmd) + ';', [])
        cmd = []
        cmd.append("DELETE FROM rules.labeval * WHERE ruleid =")
        cmd.append(str(ruleid))
        yield from self.db.execute_single(' '.join(cmd) + ';', [])
        return
