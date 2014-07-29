import asyncio
import dateutil
from enum import Enum
from collections import defaultdict
from decimal import Decimal
from datetime import date, datetime, timedelta

from utils.database.database import AsyncConnectionPool
from utils.database.database import MappingUtilites as DBMapUtils
import maven_config as MC
import maven_logging as ML

logger = ML.get_logger()
ML.set_debug('/tmp/web_persistence.log')

CONFIG_DATABASE = 'database'

Results = Enum('Results',
"""
    patientname
    patientid
    birthdate
    sex
    encounterid
    encounter_date
    encounter_list
    cost
    diagnosis
    allergies
    problems
    admission
    lengthofstay
    spending
    savings
    date
    ordertype
    orderid
    ordername
    alerttype
    alertid
    ruleid
    datetime
    title
    description
    outcome
    active
    userid
    username
    customerid
    provid
    displayname
    officialname
    password
    passexpired
    userstate
    failedlogins
    startdate
    enddate
    recentkeys
    diagnosisid
    category
    subcategory
    scope
    action
""")


def makelist(v):
    if type(v) is list:
        return tuple(v)
    elif type(v) is tuple:
        return v
    elif type(v) is str:
        return tuple([v])
    else:
        return tuple(v,)


class InvalidRequest(Exception):
    pass


def _prettify_name(s):
    name = s.split(",")
    return str.title(name[0]) + ", " + str.title(name[1])


def _prettify_sex(s):
    return str.title(s)

def _prettify_datetime(s):
    return s.strftime("%Y-%m-%d %H:%M")


def _prettify_lengthofstay(s):
    days = s[0].days
    if days>1:
        return str(days)+" days"
    else:
        return (s[0].seconds // 3600) + " hours"


def _invalid_num(x):
    return -1


def _invalid_string(x):
    return "NOTVALIDYET"


def _build_format(override={}):
    formatbytypemap = {
        Decimal: int,
        date: str,
        datetime: str,
        type(None): _invalid_string,
    }

    def formatbytype(x):
        if type(x) in formatbytypemap:
            return formatbytypemap[type(x)](x)
        else:
            return x
        
    formatbykeymap = {
        Results.patientname: _prettify_name,
        Results.sex: _prettify_sex,
        #Results.encounter_date: _prettify_date,
        Results.lengthofstay: _prettify_lengthofstay,
    }        
    formatter = defaultdict(lambda: formatbytype,
                            formatbykeymap.items())
    formatter.update(override)
    return formatter


def build_columns(desired, available, defaults):
    extras = set(desired) - available.keys()
    if extras:
        raise InvalidRequest("patient_info does not support these results: " + str(extras))

    #missing = required - set(desired)
    #if missing:
    #    raise InvalidRequest("patient_info requires the following results: "+str(missing))

    columns = list(desired)
    columns.extend(defaults - set(desired))
    return DBMapUtils().select_rows_from_map([available[x] for x in columns])

def build_set(items, available):
    try:
        iter(items)
        return ",".join([available[x] for x in items])
    except TypeError:
        return available[items]

def append_extras(cmd, datefield, startdate, enddate, orderby, ascending,
                  groupby, limit, column_map):
    if startdate:
        cmd.append("AND "+column_map[datefield] +" >= %s")
        cmdargs.append(startdate)
    if enddate:
        cmd.append("AND "+column_map[datefield]+ " < %s + interval '1 day'")
        cmdargs.append(enddate)
    if groupby:
        try:
            gb = build_set(groupby, column_map)
        except KeyError :
            gb = groupby
        cmd.append("GROUP BY " + gb)
    if orderby:
        try:
            ob = build_set(orderby, column_map)
        except KeyError:
            ob = orderby
        cmd.append("ORDER BY %s %s" % (ob, "ASC" if ascending else "DESC"))
    if limit:
        cmd.append(limit)
    
class WebPersistence():
    def __init__(self, configname):
        self.db = AsyncConnectionPool(MC.MavenConfig[configname][CONFIG_DATABASE])

    def schedule(self, loop):
        self.db.schedule(loop)

    @asyncio.coroutine
    def execute(self, cmd, cmdargs, display, desired):
        cur = yield from self.db.execute_single(' '.join(cmd) + ';', cmdargs)
        results = []
        if cmd[0] in ['SELECT']:
            for row in cur:
#            results.append({print((type(v),v, k, display[k], display[k](v))) or desired[k]: display[k](v) for k,v in zip(desired, row)})
                results.append({desired[k]: display[k](v) for k,v in zip(desired, row)})

        logger.debug(str(cmd) + " " +str(cmdargs) +" -> " + str(results))
        return results

    @asyncio.coroutine
    def update_password(self, user, newpw, timeout = '180d'):
        yield from self.execute(["UPDATE users set (pw, pw_expiration) = (%s, now() + interval %s) where user_id = %s"],
                                [newpw, timeout, user], {}, {})
    @asyncio.coroutine
    def update_user_settings(self, user, officialname,displayname):
        yield from self.execute(["UPDATE users set (official_name, display_name) = (%s, %s) where user_id = %s"],
                                [officialname, displayname, user], {}, {})

    @asyncio.coroutine
    def rate_alert(self, customer_id, provider_id, category, subcategory, rule_id, scope, action, update=0):

        if update == 1:
            yield from self.execute(["UPDATE alert_setting_hist set (action) = (%s) where customer_id = %s and provider_id = %s " +
                                                                                   "and category = %s and subcategory = %s "+
                                                                                   "and rule_id = %s and scope = %s"],
                                    [action, customer_id, provider_id, category, subcategory, rule_id, scope], {}, {})
        else:
            yield from self.execute(["INSERT into alert_setting_hist (customer_id, provider_id, category, subcategory, rule_id, scope, action)" +
                                     "VALUES (%s,%s,%s,%s,%s,%s,%s)"],
                                    [customer_id, provider_id, category, subcategory, rule_id, scope, action], {}, {})

    @asyncio.coroutine
    def record_login(self, username, method, ip, authkey):
        yield from self.execute(['INSERT INTO logins (user_name, method, logintime, ip, authkey) VALUES (%s, %s, now(), %s, %s)'],
                                [username, method, ip, authkey], {}, {})

    _default_pre_login = set((Results.username,))
    _available_pre_login = {
        Results.userid: 'users.user_id',
        Results.username: 'users.user_name',
        Results.customerid: 'users.customer_id',
        Results.provid: 'users.prov_id',
        Results.displayname: 'users.display_name',
        Results.officialname: "users.official_name",
        Results.password: 'users.pw',
        Results.passexpired: 'users.pw_expiration < now()',
        Results.userstate: 'users.state',
#        Results.failedlogins: 'array_agg(logins.logintime)',
        Results.recentkeys: 'NULL',
    }
    _display_pre_login = _build_format()
        
    @asyncio.coroutine
    def pre_login(self, desired, username=None, provider=[], keycheck=None):
        columns = build_columns(desired.keys(), self._available_pre_login,
                                self._default_pre_login)
        if not username and not provider:
            raise IndexError
        cmd = []
        cmdargs = []
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM users")
        if username:
            cmd.append("WHERE users.user_name = %s")
            cmdargs.append(username)
        else:
            cmd.append("WHERE users.prov_id = %s AND users.customer_id = %s")
            cmdargs.append(provider[0])
            cmdargs.append(provider[1])
        
        results = yield from self.execute(cmd, cmdargs, self._display_pre_login, desired)
        return results[0]
    
    _default_patient_info = set((Results.encounter_date,))
    _available_patient_info = {
        Results.patientname: "max(patient.patname)",
        Results.patientid: "encounter.pat_id",
        Results.birthdate: "max(patient.birthdate)",
        Results.sex: "max(patient.sex)",
        Results.encounter_date: "max(encounter.contact_date) AS contact_date",
        Results.encounter_list: "array_agg(encounter.csn || ' ' || encounter.contact_date)" ,
        Results.cost: "0",
        Results.diagnosis: "'None yet'",
        Results.allergies: "'None'",
        Results.problems: "'None yet'",
        Results.admission: "max(encounter.hosp_admsn_time)",
        Results.lengthofstay: 'array_agg(coalesce(encounter.hosp_disch_time, now()) - encounter.hosp_admsn_time)',
    }
    _display_patient_info = _build_format({
        Results.encounter_list: lambda x: list(map(lambda v: v.split(' '), x)),
        Results.cost: _invalid_num,
    })

    @asyncio.coroutine
    def patient_info(self, desired, user, customer, patients=[], limit="", patient_name="",
                     startdate=None, enddate=None):
        columns = build_columns(desired.keys(), self._available_patient_info,
                                self._default_patient_info)
                
        cmd = []
        cmdargs=[]
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM encounter JOIN patient")
        cmd.append("ON (patient.pat_id = encounter.pat_id AND encounter.customer_id = patient.customer_id)")
        cmd.append("WHERE encounter.customer_id = %s")
        cmdargs.append(customer)
        cmd.append("AND encounter.visit_prov_id = %s")
        cmdargs.append(user)
        if patient_name:
            substring = "%" + patient_name + "%"
            cmd.append("AND UPPER(patient.patname) LIKE UPPER(%s)")
            cmdargs.append(substring)
        if patients:
            cmd.append("AND encounter.pat_id IN %s")
            cmdargs.append(makelist(patients))
        if startdate:
            cmd.append("AND encounter.hosp_admsn_time >= %s")
            cmdargs.append(startdate)
        if enddate:
            cmd.append("AND encounter.hosp_disch_time < %s")
            cmdargs.append(enddate)
        append_extras(cmd, None, None, None, 'contact_date', True, 'encounter.pat_id', limit,
                      self._available_patient_info)

        results = yield from self.execute(cmd, cmdargs, self._display_patient_info, desired)
        return results

    _default_diagnosis_info = set((Results.diagnosis,))
    _available_diagnosis_info = {
        Results.diagnosis: "diagnosis.dx_name",
        Results.diagnosisid: "diagnosis.dx_id",
    }
    _display_diagnosis_info = _build_format({})

    @asyncio.coroutine
    def diagnosis_info(self, desired, user, customer, diagnosis="", limit=""):

        columns = build_columns(desired.keys(), self._available_diagnosis_info,
                                self._default_diagnosis_info)

        cmd = []
        cmdargs=[]
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM diagnosis")
        #cmd.append("WHERE customer_id = %s")
        #cmdargs.append(customer)
        if diagnosis:
            substring = "%" + diagnosis + "%"
            cmd.append("WHERE UPPER(dx_name) LIKE UPPER(%s)")
            cmdargs.append(substring)
        cmd.append("ORDER BY dx_name")

        if limit:
            cmd.append(limit)

        results = yield from self.execute(cmd, cmdargs, self._display_diagnosis_info, desired)
        return []

        
    _default_total_spend = set()
    _available_total_spend = {
        Results.spending: "sum(order_cost)",
        Results.savings: "NULL",
        Results.datetime: "order_ord.order_datetime",
    }
    _display_total_spend = _build_format({
        Results.savings: lambda x: -1,
        Results.spending: lambda x: (x and int(x)) or 0,
    })
        
    @asyncio.coroutine
    def total_spend(self, desired, customer, provider=None, patients=[], encounter=None,
                    startdate=None, enddate=None):
        columns = build_columns(desired.keys(), self._available_total_spend,
                                self._default_total_spend)

        cmd = []
        cmdargs = []
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM order_ord JOIN encounter")
        cmd.append("ON order_ord.encounter_id = encounter.csn")
        cmd.append("WHERE order_ord.customer_id = %s")
        cmdargs.append(customer)
        if provider:
            cmd.append("AND encounter.visit_prov_id = %s")
            cmdargs.append(provider)
        if patients:
            cmd.append("AND encounter.pat_id IN %s")
            cmdargs.append(makelist(patients))
        if encounter:
            cmd.append("AND encounter.csn = %s")
            cmdargs.append(encounter)
        append_extras(cmd, Results.datetime, startdate, enddate, None, None,
                      None, None, self._available_total_spend)
        cur = yield from self.db.execute_single(' '.join(cmd) + ';', cmdargs)
        results = yield from self.execute(cmd, cmdargs, self._display_total_spend, desired)
        if results:
            return results[0]
        else:
            return {desired[k]: 0 for k in desired}

    _default_daily_spend = set()
    _available_daily_spend = {
        Results.date: "order_ord.order_datetime",
        Results.ordertype: "order_ord.order_type",
        Results.spending: "sum(order_cost)",
    }
    _display_daily_spend = _build_format({
        Results.date: lambda d: d.strftime("%m/%d/%Y")
    })
        
    @asyncio.coroutine
    def daily_spend(self, desired, provider, customer, patients=[], encounter=None,
                    startdate=None, enddate=None):
        columns = build_columns(desired.keys(), self._available_daily_spend,
                                self._default_daily_spend)

        cmd = []
        cmdargs = []
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM order_ord JOIN encounter")
        cmd.append("ON order_ord.encounter_id = encounter.csn")
        cmd.append("WHERE encounter.visit_prov_id = %s")
        cmdargs.append(provider)
        cmd.append("AND order_ord.customer_id = %s")
        cmdargs.append(customer)
        if patients:
            cmd.append("AND encounter.pat_id IN %s")
            cmdargs.append(makelist(patients))
        if encounter:
            cmd.append("AND encounter.csn = %s")
            cmdargs.append(encounter)
        append_extras(cmd, Results.date, startdate, enddate, None, None,
                      [Results.date, Results.ordertype], None, self._available_daily_spend)

        results = yield from self.execute(cmd, cmdargs, self._display_daily_spend, desired)
        return results

    _default_alerts = set((Results.datetime,))
    _available_alerts = {
        Results.alertid: "max(alert.alert_id)",
        Results.patientid: "array_agg(alert.pat_id)",
        Results.datetime: "max(alert.alert_datetime)",
        Results.title: "max(alert.long_title)",
        Results.description: "max(alert.long_description)",
        Results.outcome: "avg(alert.outcome)",
        Results.savings: "avg(alert.saving)",
        Results.alerttype: "max(alert.category)",
        Results.ruleid: "max(alert.cds_rule)",
        }
    _display_alerts = _build_format({
        Results.title: lambda x: x or '',
        Results.ruleid: lambda x: x,
        Results.datetime: lambda x: x and _prettify_datetime(x),
        })

    @asyncio.coroutine
    def alerts(self, desired, provider, customer, patients=[], limit="",
               startdate=None, enddate=None, orderid=None, categories=[],
               orderby=Results.datetime, ascending=True, alertid=None):
        columns = build_columns(desired.keys(), self._available_alerts,
                                self._default_alerts)
        
        cmd = []
        cmdargs = []
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM alert")
        cmd.append("WHERE alert.provider_id = %s AND alert.customer_id = %s")
        cmdargs.append(provider)
        cmdargs.append(customer)
        if patients:
            cmd.append("AND alert.pat_id IN %s")
            cmdargs.append(makelist(patients))
        if categories:
            cmd.append("AND alert.category IN %s")
            cmdargs.append(makelist(categories))
        if alertid:
            cmd.append("AND alert.alert_id = %s")
            cmdargs.append(alertid)
        if orderid:
            cmd.append("AND alert.order_id = %s")
            cmdargs.append(orderid)
        append_extras(cmd, Results.datetime, startdate, enddate, orderby, ascending,
                      "(CASE WHEN cds_rule IS NULL THEN 'alert_id' || alert_id::varchar ELSE cds_rule::varchar END)",
                      limit, self._available_alerts)

        results = yield from self.execute(cmd, cmdargs, self._display_alerts, desired)
        return results

    _default_alert_settings = set((Results.ruleid,))
    _available_alert_settings = {
        Results.category: "alert_setting_hist.category",
        Results.subcategory: "alert_setting_hist.subcategory",
        Results.ruleid: "alert_setting_hist.rule_id",
        Results.scope: "alert_setting_hist.scope",
        Results.action: "alert_setting_hist.action"
        }
    _display_alert_settings = _build_format({
        Results.ruleid: lambda x: x,
        })

    @asyncio.coroutine
    def alert_settings(self, desired, provider, customer, ruleid=None, category=None, limit=""):
        columns = build_columns(desired.keys(), self._available_alert_settings,
                                self._default_alert_settings)

        cmd = []
        cmdargs = []
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM alert_setting_hist")
        cmd.append("WHERE alert_setting_hist.provider_id = %s AND alert_setting_hist.customer_id = %s")
        cmdargs.append(provider)
        cmdargs.append(customer)
        if ruleid:
            cmd.append("AND alert_setting_hist.rule_id = %s")
            cmdargs.append(ruleid)
        if category:
            cmd.append("AND alert_setting_hist.category = %s ")
            cmdargs.append(category)
        if limit:
            cmd.append(limit)
        results = yield from self.execute(cmd, cmdargs, self._display_alert_settings, desired)
        return results


    _default_orders = set((Results.datetime,))
    _available_orders = {
        Results.ordername: "order_ord.order_name",
        Results.datetime: "order_ord.order_datetime",
        Results.active: "order_ord.status",
        Results.cost: "order_ord.order_cost",
#        Results.ordertype: "(ARRAY['Medication', 'Consultation', 'Lab-work', 'Procedure', 'Other', 'Imaging'])[floor(random() * 6.0) + 1]",
        Results.ordertype: "order_ord.order_type",
        Results.orderid: "order_ord.order_id",
    }
    #_display_orders = _build_format()

    _display_orders = _build_format({
        Results.datetime: lambda x: x and _prettify_datetime(x),
        })

    @asyncio.coroutine
    def orders(self, desired, customer, encounter=None, patientid=None, ordertypes=[], limit="",
               startdate=None, enddate=None):
        if not encounter and not patientid:
            raise InvalidRequest('Getting orders requires a patient or an encounter')
        columns = build_columns(desired.keys(), self._available_orders,
                                self._default_orders)
        cmd = []
        cmdargs = []
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM order_ord")
        cmd.append("WHERE order_ord.customer_id = %s")
        cmdargs.append(customer)
        if encounter:
            cmd.append("AND order_ord.encounter_id = %s")
            cmdargs.append(encounter)
        else:
            cmd.append("AND order_ord.pat_id in %s")
            cmdargs.append(tuple(patientid))
        if ordertypes:
            cmd.append("AND order_ord.order_type IN %s")
            cmdargs.append(ordertypes)
        append_extras(cmd, Results.datetime, startdate, enddate, Results.datetime, False,
                      None, limit, self._available_orders)

        results = yield from self.execute(cmd, cmdargs, self._display_orders, desired)
        return results
        
    _default_per_encounter = set((Results.encounterid,))
    _available_per_encounter = {
        Results.patientid: "encounter.pat_id",
        Results.patientname: "patient.patname",
        Results.encounterid: "encounter.csn",
        Results.startdate: 'min(hosp_admsn_time)',
        Results.enddate: 'max(hosp_disch_time)',
        Results.diagnosis: "'diagnosis'",
        Results.spending: "sum(order_ord.order_cost)",
    }
    _display_per_encounter = _build_format({
        Results.enddate: lambda x: x and _prettify_datetime(x),
        })
        
    @asyncio.coroutine
    def per_encounter(self, desired, provider, customer, patients=[], encounter=None,
                      startdate=None, enddate=None):
        columns = build_columns(desired.keys(), self._available_per_encounter,
                                self._default_per_encounter)

        cmd = []
        cmdargs=[]
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM order_ord JOIN encounter")
        cmd.append("ON order_ord.encounter_id = encounter.csn")
        cmd.append("JOIN patient")
        cmd.append("ON encounter.pat_id = patient.pat_id")
        cmd.append("WHERE encounter.visit_prov_id IN %s")
        cmdargs.append(makelist(provider))
        cmd.append("AND order_ord.customer_id = %s")
        cmdargs.append(customer)
        if patients:
            cmd.append("AND encounter.pat_id IN %s")
            cmdargs.append(makelist(patients))
        if encounter:
            cmd.append("AND encounter.csn = %s")
            cmdargs.append(encounter)
        if startdate:
            cmd.append("AND encounter.hosp_admsn_time >= %s")
            cmdargs.append(startdate)
        if enddate:
            cmd.append("AND encounter.hosp_disch_time < %s")
            cmdargs.append(enddate)
        cmd.append("GROUP BY encounter.csn, encounter.pat_id, patient.patname")
        #TODO : encounter.pat_id is added to the Group by, need test to make sure we are not losing data

        results = yield from self.execute(cmd, cmdargs, self._display_per_encounter, desired)
        return results
