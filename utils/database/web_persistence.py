import asyncio
import dateutil
from enum import Enum
from collections import defaultdict
from decimal import Decimal
from datetime import date, datetime

from utils.database.database import AsyncConnectionPool
from utils.database.database import MappingUtilites as DBMapUtils
import maven_config as MC

CONFIG_DATABASE = 'database'

Results = Enum('Results',
"""
    patientname
    patientid
    birthdate
    sex
    encounter_date
    encounter_list
    cost
    diagnosis
    allergies
    problems
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
""")

class InvalidRequest(Exception):
    pass


def _prettify_name(s):
    name = s.split(",")
    return (str.title(name[0]) + ", " + str.title(name[1]))

def _prettify_sex(s):
    return str.title(s)

def _prettify_date(s):
    prsr = dateutil.parser()
    d = prsr.parse(s)
    return (d.strftime("%A, %B %d, %Y"))

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
        Results.encounter_date: _prettify_date,
    }        
    formatter = defaultdict(lambda: formatbytype,
                            formatbykeymap.items())
    formatter.update(override)
    return formatter


def build_columns(desired, available, defaults):
    extras= set(desired) - available.keys()
    if extras:
        raise InvalidRequest("patient_info does not support these results: "+str(extras))

    #missing = required - set(desired)
    #if missing:
    #    raise InvalidRequest("patient_info requires the following results: "+str(missing))

    columns = list(desired)
    columns.extend(defaults - set(desired))
    return DBMapUtils().select_rows_from_map([available[x] for x in columns])


class WebPersistence():
    def __init__(self, configname):
        self.db = AsyncConnectionPool(MC.MavenConfig[configname][CONFIG_DATABASE])

    def schedule(self, loop):
        self.db.schedule(loop)

    @asyncio.coroutine
    def execute(self, cmd, cmdargs, display, desired):
        cur = yield from self.db.execute_single(' '.join(cmd)+';',cmdargs)
        
        results = []
        for row in cur:
#            results.append({print((type(v),v, k, display[k], display[k](v))) or desired[k]: display[k](v) for k,v in zip(desired, row)})
            results.append({desired[k]: display[k](v) for k,v in zip(desired, row)})
            
        return results

    
    _default_patient_info = set((Results.encounter_date,))
    _available_patient_info = {
        Results.patientname: "max(patient.patname)",
        Results.patientid: "encounter.pat_id",
        Results.birthdate: "max(patient.birthdate)",
        Results.sex: "max(patient.sex)",
        Results.encounter_date: "max(encounter.contact_date) as contact_date",
        Results.encounter_list: "array_agg(encounter.csn || ' ' || encounter.contact_date)" ,
        Results.cost: "NULL",
        Results.diagnosis: "NULL",
        Results.allergies: "NULL",
        Results.problems: "NULL",
    }
    _display_patient_info = _build_format({
        Results.encounter_list: lambda x: list(map(lambda v: v.split(' '), x)),
        Results.cost: _invalid_num,
    })
        
    @asyncio.coroutine
    def patient_info(self, desired, user, customer, patients=[], limit=""):
        columns = build_columns(desired.keys(), self._available_patient_info,
                                self._default_patient_info)
                
        cmd = []
        cmdargs=[]
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM patient JOIN encounter")
        cmd.append("ON (patient.pat_id = encounter.pat_id AND encounter.customer_id = patient.customer_id)")
        cmd.append("WHERE encounter.customer_id = %s")
        cmdargs.append(customer)
        cmd.append("AND encounter.visit_prov_id = %s")
        cmdargs.append(user)
        if patients:
            if type(patients) is list:
                cmd.append("AND encounter.pat_id in %s")
            else:
                cmd.append("AND encounter.pat_id = %s")
            cmdargs.append(patients)
        cmd.append("GROUP BY encounter.pat_id")
        cmd.append("ORDER BY contact_date")

        if limit:
            cmd.append(limit)

    
        results = yield from self.execute(cmd, cmdargs, self._display_patient_info, desired)
        return results

    _default_total_spend = set()
    _available_total_spend = {
        Results.spending: "sum(order_cost)",
        Results.savings: "NULL",
    }
    _display_total_spend = _build_format({Results.savings: lambda x: -1})
        
    @asyncio.coroutine
    def total_spend(self, desired, provider, customer, patients=[], encounter=None):
        columns = build_columns(desired.keys(), self._available_total_spend,
                                self._default_total_spend)

        cmd = []
        cmdargs=[]
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM mavenorder JOIN encounter")
        cmd.append("ON mavenorder.encounter_id = encounter.csn")
        cmd.append("WHERE encounter.visit_prov_id = %s")
        cmdargs.append(provider)
        cmd.append("AND mavenorder.customer_id = %s")
        cmdargs.append(customer)
        if patients:
            cmd.append("AND encounter.pat_id in %s")
            cmdargs.append(tuple(patients))
        if encounter:
            cmd.append("AND encounter.csn = %s")
            cmdargs.append(encounter)
        
        cur = yield from self.db.execute_single(' '.join(cmd)+';',cmdargs)
        results = yield from self.execute(cmd, cmdargs, self._display_total_spend, desired)
        if results:
            return results[0]
        else:
            return {desired[k]: 0 for k in desired}

    _default_daily_spend = set()
    _available_daily_spend = {
        Results.date: "to_char(datetime,'Mon/DD/YYYY') as dt",
        Results.ordertype: "order_type",
        Results.spending: "sum(order_cost)",
    }
    _display_daily_spend = _build_format()
        
    @asyncio.coroutine
    def daily_spend(self, desired, provider, customer, patients=[], encounter=None):
        columns = build_columns(desired.keys(), self._available_daily_spend,
                                self._default_daily_spend)

        cmd = []
        cmdargs=[]
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM mavenorder JOIN encounter")
        cmd.append("ON mavenorder.encounter_id = encounter.csn")
        cmd.append("WHERE encounter.visit_prov_id = %s")
        cmdargs.append(provider)
        cmd.append("AND mavenorder.customer_id = %s")
        cmdargs.append(customer)
        if patients:
            cmd.append("AND encounter.pat_id in %s")
            cmdargs.append(tuple(patients))
        if encounter:
            cmd.append("AND encounter.csn = %s")
            cmdargs.append(encounter)
        cmd.append("GROUP BY dt, order_type")

        results = yield from self.execute(cmd, cmdargs, self._display_daily_spend, desired)
        return results

    _default_alerts = set((Results.datetime,))
    _available_alerts = {
        Results.alertid:"alert.alert_id",
        Results.patientid:"alert.pat_id",
        Results.datetime:"alert.alert_datetime",
        Results.title:"alert.long_title",
        Results.description:"alert.description",
        Results.outcome:"alert.outcome",
        Results.savings:"alert.saving",
        Results.alerttype:"'Duplicate'",
        Results.ruleid:"alert.sleuth_rule",
        }
    _display_alerts = _build_format()

    @asyncio.coroutine
    def alerts(self, desired, provider, customer, patients=[], limit=""):
        columns = build_columns(desired.keys(), self._available_alerts,
                                self._default_alerts)
        
        cmd=[]
        cmdargs=[]
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM alert")
        cmd.append("WHERE alert.provider_id = %s AND alert.customer_id = %s")
        cmdargs.append(provider)
        cmdargs.append(customer)
        if patients:
            cmd.append("AND alert.pat_id IN %s")
            cmdargs.append(tuple(patients))
        cmd.append("ORDER BY alert.alert_datetime DESC")
        if limit:
            cmd.append(limit)

        results = yield from self.execute(cmd, cmdargs, self._display_alerts, desired)
        return results
        

    _default_orders = set((Results.datetime,))
    _available_orders = {
        Results.ordername:"mavenorder.order_name",
        Results.datetime:"mavenorder.datetime",
        Results.active:"mavenorder.active",
        Results.cost:"mavenorder.order_cost",
        Results.ordertype:"mavenorder.order_type",
        Results.orderid:"mavenorder.orderid",
    }
    _display_orders = _build_format()
    
    @asyncio.coroutine
    def orders(self, desired, customer, encounter, ordertypes=[], limit=""):
        columns = build_columns(desired.keys(), self._available_orders,
                                self._default_orders)


        cmd=[]
        cmdargs =[]
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM mavenorder")
        cmd.append("WHERE mavenorder.customer_id = %s")
        cmdargs.append(customer)
        if encounter:
            cmd.append("AND mavenorder.encounter_id = %s")
            cmdargs.append(encounter)
        if ordertypes:
            cmd.append("AND mavenorder.order_type in %s")
            cmdargs.append(ordertypes)
        cmd.append("ORDER BY mavenorder.datetime desc")
        if limit:
            cmd.append(limit)

        results = yield from self.execute(cmd, cmdargs, self._display_orders, desired)
        return results
        
