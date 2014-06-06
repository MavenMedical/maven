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
PatientInfo = Enum('PatientInfo','name id birthdate sex encounter_date encounter_list cost diagnosis allergies problems')
TotalSpend = Enum('TotalSpend','spending savings')
DailySpend = Enum('DailySpend','date type spending')
Alerts = Enum('Alerts','id patient datetime title description outcome savings')
Orders = Enum('Orders','id name datetime active cost category')

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
    return "NOT VALID YET"

_formattypes = {
    # int: lambda x: x,
    # str: lambda x: x,
    Decimal: int,
    date: str,
    datetime: str,
    type(None): _invalid_string,
}

def _defaultformat():
    return lambda x:_formattypes.get(type(x), lambda x: x)(x)

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

    
    _default_patient_info = set((PatientInfo.encounter_date,))
    _available_patient_info = {
        PatientInfo.name: "max(patient.patname)",
        PatientInfo.id: "encounter.pat_id",
        PatientInfo.birthdate: "max(patient.birthdate)",
        PatientInfo.sex: "max(patient.sex)",
        PatientInfo.encounter_date: "max(encounter.contact_date) as contact_date",
        PatientInfo.encounter_list: "array_agg(encounter.csn || ' ' || encounter.contact_date)" ,
        PatientInfo.cost: "NULL",
        PatientInfo.diagnosis: "NULL",
        PatientInfo.allergies: "NULL",
        PatientInfo.problems: "NULL",
    }
    _display_patient_info = defaultdict(_defaultformat, (
        (PatientInfo.name, _prettify_name),
        (PatientInfo.sex, _prettify_sex),
        (PatientInfo.encounter_date, _prettify_date),
        (PatientInfo.encounter_list, lambda x: list(map(lambda v: v.split(' '), x))),
        (PatientInfo.cost, _invalid_num),
    ))
        
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
        TotalSpend.spending: "sum(order_cost)",
        TotalSpend.savings: "NULL",
    }
    _display_total_spend = defaultdict(_defaultformat, ((TotalSpend.savings, lambda x: -1),))
        
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
        DailySpend.date: "to_char(datetime,'Mon/DD/YYYY') as dt",
        DailySpend.type: "order_type",
        DailySpend.spending: "sum(order_cost)",
    }
    _display_daily_spend = defaultdict(_defaultformat)
        
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

    _default_alerts = set((Alerts.datetime,))
    _available_alerts = {
        Alerts.id:"alert.alert_id",
        Alerts.patient:"alert.pat_id",
        Alerts.datetime:"alert.alert_datetime",
        Alerts.title:"alert.long_title",
        Alerts.description:"alert.description",
        Alerts.outcome:"alert.outcome",
        Alerts.savings:"alert.saving",
        }
    _display_alerts = defaultdict(_defaultformat)

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
        

    _default_orders = set((Orders.datetime,))
    _available_orders = {
        Orders.name:"mavenorder.order_name",
        Orders.datetime:"mavenorder.datetime",
        Orders.active:"mavenorder.active",
        Orders.cost:"mavenorder.order_cost",
        Orders.category:"NULL",
        Orders.id:"mavenorder.orderid",
    }
    _display_orders = defaultdict(_defaultformat)
    
    @asyncio.coroutine
    def orders(self, desired, customer, encounter, limit=""):
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
        cmd.append("ORDER BY mavenorder.datetime desc")
        if limit:
            cmd.append(limit)

        results = yield from self.execute(cmd, cmdargs, self._display_orders, desired)
        return results
        
