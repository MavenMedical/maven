import asyncio
from enum import Enum
from collections import defaultdict
from decimal import Decimal
from datetime import date, datetime
import dateutil.relativedelta
import dateutil.parser
import json
from functools import lru_cache
from utils.database.remote_database_connector import RemoteDatabaseConnector
from utils.enums import ALERT_VALIDATION_STATUS, FOLLOWUPTASK_STATUS
from utils.database.database import AsyncConnectionPool
from utils.database.database import MappingUtilites as DBMapUtils
import maven_config as MC
import maven_logging as ML

# logger = ML.get_logger()
# ML.set_debug('/tmp/web_persistence.log')

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
    likes
    dislikes
    layoutid
    widget
    template
    element
    priority
    state
    ehrstate
    auditid
    details
    device
    roles
    name
    abbr
    license
    license_exp
    config
    lastlogin
    settings
    profession
    notify1
    notify2
    target_user
    authorid
    taskid
    delivery_method
    task_status
    due_datetime
    expire_datetime
    activityid
    protocol
    protocolname
    msg_subject
    msg_body
    groupid
    group_name
    count
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
    try:
        name = s.split(",")
        return str.title(name[0]) + ", " + str.title(name[1])
    except:
        return s


def _prettify_sex(s):
    return str.title(s)


def _prettify_datetime(s):
    return s.strftime("%Y-%m-%d %H:%M")


def _prettify_lengthofstay(s):
    days = s[0].days
    if days > 1:
        return str(days) + " days"
    else:
        return str(s[0].seconds // 3600) + " hours"


def _invalid_num(x):
    return -1


def _invalid_string(x):
    return ""


def _build_format(override=None):
    formatbytypemap = {
        Decimal: int,
        date: str,
        datetime: str,
        memoryview: bytes,
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
        # Results.encounter_date: _prettify_date,
        Results.lengthofstay: _prettify_lengthofstay,
    }
    formatter = defaultdict(lambda: formatbytype,
                            formatbykeymap.items())
    if override:
        formatter.update(override)
    return formatter


def build_columns(desired, available, defaults):
    extras = set(desired) - available.keys()
    if extras:
        raise InvalidRequest("these results are not supported: " + str(extras))

    # missing = required - set(desired)
    # if missing:
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


def append_extras(cmd, cmdargs, datefield, startdate, enddate, orderby, ascending,
                  groupby, limit, column_map):
    if startdate:
        cmd.append("AND " + column_map[datefield] + " >= %s")
        cmdargs.append(startdate)
    if enddate:
        cmd.append("AND " + column_map[datefield] + " < %s + interval '1 day'")
        cmdargs.append(enddate)
    if groupby:
        try:
            gb = build_set(groupby, column_map)
        except KeyError:
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


@lru_cache()
def WebPersistence(configname):
    server = RemoteDatabaseConnector(MC.MavenConfig[configname][CONFIG_DATABASE])
    ret = server.create_client(WebPersistenceBase)
    ret.schedule = lambda *args: None
    return ret


class WebPersistenceBase():
    def __init__(self, configname):
        self.db = AsyncConnectionPool(MC.MavenConfig[configname][CONFIG_DATABASE])
        self.scheduled = False

    def schedule(self, loop=asyncio.get_event_loop()):
        if not self.scheduled:
            self.db.schedule(loop)
        self.scheduled = True

    @asyncio.coroutine
    def execute(self, cmd, cmdargs, display, desired):
        cur = yield from self.db.execute_single(' '.join(cmd) + ';', cmdargs)
        results = []
        if desired:
            for row in cur:
                # results.append({print((type(v),v, k, display[k], display[k](v)))
                #                or desired[k]: display[k](v) for k,v in zip(desired, row)})
                results.append({desired[k]: display[k](v) for k, v in zip(desired, row)})

        # logger.debug(str(cmd) + " " + str(cmdargs) + " -> " + str(results))
        return results

    @asyncio.coroutine
    def update_password(self, user, newpw, timeout='180d'):
        yield from self.execute(["UPDATE users set (pw, pw_expiration) " +
                                 "= (%s, now() + interval %s) where user_id = %s"],
                                [newpw, timeout, user], {}, {})

    @asyncio.coroutine
    def save_user_settings(self, user, customerid, officialname, displayname):
        yield from self.execute(["UPDATE users set (official_name, display_name) " +
                                 "= (%s, %s) where user_name = UPPER(%s) and customer_id = %s"],
                                [officialname, displayname, user, customerid], {}, {})

    @asyncio.coroutine
    def update_user(self, user, customer, state, desired=None):
        cmd = []
        cmdargs = []
        cmd.append("UPDATE users")
        cmd.append("set (state) = (%s)")
        cmdargs.append(state)
        cmd.append("where user_name = UPPER(%s) and customer_id = %s")
        cmdargs.append(user)
        cmdargs.append(customer)
        if desired:
            columns = build_columns(desired.keys(), self._available_user_info, self._default_user_info)
            cmd.append("returning")
            cmd.append(columns)
            results = yield from self.execute(cmd, cmdargs, self._display_user_info, desired)
            return results
        else:
            yield from self.execute(cmd, cmdargs, {}, {})

    @asyncio.coroutine
    def update_user_notify_preferences(self, user, customer_id, notify_primary, notify_secondary):
        column_map = ["notify_primary",          # 0
                      "notify_secondary"]
        columns = DBMapUtils().select_rows_from_map(column_map)
        cmd = []
        cmd.append("UPDATE user_pref SET (" + columns + ") = (%s, %s)")
        cmd.append("WHERE customer_id=%s and user_name=%s")
        cmdargs = [notify_primary, notify_secondary, customer_id, user]

        try:
            yield from self.execute(cmd, cmdargs, {}, {})
            return True
        except Exception as e:
            ML.EXCEPTION(e)
            return False

    _default_user_notify_prefs_info = set()
    _available_user_notify_prefs_info = {
        Results.customerid: "user_pref.customer_id",
        Results.username: "user_pref.user_name",
        Results.notify1: "user_pref.notify_primary",
        Results.notify2: "user_pref.notify_secondary",
    }
    _display_user_notify_prefs_info = _build_format({
        Results.customerid: lambda x: int(x),
        Results.username: lambda x: str(x),
        Results.notify1: lambda x: str(x),
        Results.notify2: lambda x: str(x)
    })

    @asyncio.coroutine
    def get_users_notify_preferences(self, customer_id):
        desired = {
            Results.customerid: 'customer_id',
            Results.username: 'user_name',
            Results.notify1: 'notify_primary',
            Results.notify2: 'notify_secondary'
        }
        columns = build_columns(desired.keys(), self._available_user_notify_prefs_info,
                                self._default_user_notify_prefs_info)
        cmd = []
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM user_pref WHERE customer_id=%s")

        cmdargs = [customer_id]

        results = yield from self.execute(cmd, cmdargs, self._display_user_notify_prefs_info, desired)

        return results

    @asyncio.coroutine
    def update_customer(self, customer, name, abbr, license_num, license_exp):
        cmd = []
        cmdargs = []
        cmd.append("UPDATE customer set")
        cmd.append("(name, abbr, license_type, license_exp) = (%s,%s,%s,%s)")
        cmdargs.extend([name, abbr, license_num, license_exp])
        cmd.append("where customer_id = %s")
        cmdargs.append(customer)
        self.execute(cmd, cmdargs, _build_format(), {0: 'customer_id'})
        # return [row['customer_id'] for row in ret]

    @asyncio.coroutine
    def add_customer(self, name, abbr, license, license_exp, config):
        cmd = ['INSERT INTO customer (customer_id, ']
        cmdargs = []
        cmd.append('name, abbr, license_type, license_exp, clientapp_config')
        cmdargs.extend([name, abbr, license, license_exp, config])
        cmd.append(') VALUES(((SELECT MAX(customer_id) FROM customer) + 1),%s,%s,%s,%s,%s)')
        cmd.append('returning customer_id')
        ret = yield from self.execute(cmd, cmdargs, _build_format(), {0: 'customer_id'})
        return [row['customer_id'] for row in ret]

    @asyncio.coroutine
    def setup_customer(self, customer, clientapp_settings):
        yield from self.execute(["UPDATE customer set clientapp_settings = %s where customer_id = %s"],
                                [json.dumps(clientapp_settings), customer], {}, {})

        yield from self.db.execute_single("SELECT upsert_alert_config(%s, %s, %s, %s, %s, %s)",
                                          extra=[customer, -1, 'PATHWAY', None, 400, None])

    @asyncio.coroutine
    def update_alert_setting(self, user, customer, alertid, ruleid, category, actioncomment):
        yield from self.execute(["UPDATE alert_setting_hist set(action_comment, datetime) = " +
                                 "(%s, CURRENT_TIMESTAMP) where alert_id=%s and customer_id = " +
                                 "%s and user_id=%s and category=%s and rule_id=%s"],
                                [actioncomment, alertid, customer, user,
                                 category, ruleid], {}, {})

    @asyncio.coroutine
    def rate_alert(self, customer_id, user_id, category, subcategory,
                   alertid, rule_id, scope, action, update=0):

        if update == 1:
            yield from self.execute(["UPDATE alert_setting_hist set (action, datetime) = " +
                                     "(%s, CURRENT_TIMESTAMP) where alert_id = %s and " +
                                     "customer_id = %s and user_id = %s and category = %s " +
                                     "and subcategory = %s and rule_id = %s and scope = %s"],
                                    [action, alertid, customer_id, user_id, category,
                                     subcategory, rule_id, scope], {}, {})
        else:
            yield from self.execute(["INSERT into alert_setting_hist (alert_id, customer_id, " +
                                     "user_id, datetime, category, subcategory, rule_id, " +
                                     "scope, action)" +
                                     "VALUES (%s,%s,%s,CURRENT_TIMESTAMP,%s,%s,%s,%s,%s)"],
                                    [alertid, customer_id, user_id, category, subcategory,
                                     rule_id, scope, action], {}, {})

    @asyncio.coroutine
    def EHRsync_create_user_provider(self, new_provider_dict):

        # Insert into USERS table
        column_map = ["customer_id",          # 0
                      "prov_id",
                      "user_name",
                      "official_name",         # 3
                      "display_name",
                      "state",
                      "ehr_state",
                      "roles",
                      "layouts",
                      "profession"]
        columns = DBMapUtils().select_rows_from_map(column_map)
        cmdargs = [new_provider_dict["customer_id"],
                   new_provider_dict["prov_id"],
                   new_provider_dict["user_name"],
                   new_provider_dict["official_name"],
                   new_provider_dict["display_name"],
                   new_provider_dict["state"],
                   new_provider_dict["ehr_state"],
                   new_provider_dict.get('roles', ["provider"]),
                   new_provider_dict.get('layouts', [2]),
                   new_provider_dict.get('profession')]
        cmd = []
        cmd.append("INSERT INTO users (" + columns + ")")
        cmd.append("VALUES (%s, %s, UPPER(%s), %s, %s, %s, %s, %s, %s, %s) RETURNING user_id")
        yield from self.execute(cmd, cmdargs, _build_format(), {0: 'user_id'})

        # Insert default Notification Settings into USER_PREF table
        column_map = ["customer_id",          # 0
                      "user_name",
                      "notify_primary",
                      "notify_secondary"]
        columns = DBMapUtils().select_rows_from_map(column_map)
        cmd = []
        cmd.append("INSERT INTO user_pref (" + columns + ")")
        cmd.append("VALUES (%s, %s, %s, %s)")
        cmdargs = [new_provider_dict['customer_id'],
                   new_provider_dict['user_name'],
                   'desktop',
                   'off']
        yield from self.execute(cmd, cmdargs, {}, {})

        # If the User is a provider, add them to the provider table
        if not new_provider_dict.get('prov_id', None):
            return
        column_map = ["prov_id",          # 0
                      "customer_id",
                      "prov_name",
                      "specialty"]         # 3

        columns = DBMapUtils().select_rows_from_map(column_map)
        cmdargs = [new_provider_dict["prov_id"],
                   new_provider_dict["customer_id"],
                   new_provider_dict["official_name"],
                   new_provider_dict["specialty"]]
        cmd = []
        cmd.append("INSERT INTO provider (" + columns + ")")
        cmd.append("VALUES (%s, %s, %s, %s)")
        yield from self.execute(cmd, cmdargs, {}, {})

    @asyncio.coroutine
    def EHRsync_update_user_provider(self, new_provider_dict):

        column_map = ["ehr_state"]
        columns = DBMapUtils().select_rows_from_map(column_map)
        cmdargs = [new_provider_dict["ehr_state"],
                   new_provider_dict["customer_id"],
                   new_provider_dict["prov_id"]]
        cmd = []
        cmd.append("UPDATE users")
        cmd.append("SET (" + columns + ") = (%s)")
        cmd.append("WHERE customer_id=%s and prov_id=%s")
        yield from self.execute(cmd, cmdargs, {}, {})

    @asyncio.coroutine
    def record_login(self, username, customer_id, method, ip, authkey, environment=None):
        yield from self.execute(["INSERT INTO logins (user_name, customer_id, method, logintime, ip, authkey, environment)" +
                                 "VALUES (UPPER(%s), %s, %s, now(), %s, %s, %s)"],
                                [username, customer_id, method, ip, authkey, environment], {}, {})

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
        Results.ehrstate: 'users.ehr_state',
        #        Results.failedlogins: 'array_agg(logins.logintime)',
        Results.recentkeys: 'NULL',
        Results.settings: 'customer.clientapp_settings',
        Results.roles: 'users.roles',
    }
    _display_pre_login = _build_format({
        # Results.roles: (lambda x: print(x, type(x)) or x[1:-1].split(',') if x else None)
    })

    @asyncio.coroutine
    def pre_login(self, desired, customer, username, keycheck=None):
        columns = build_columns(desired.keys(), self._available_pre_login,
                                self._default_pre_login)
        cmd = []
        cmdargs = []
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM users")
        if Results.settings in desired:
            cmd.append("INNER JOIN customer on users.customer_id = customer.customer_id")
        cmd.append("WHERE users.customer_id = %s")
        cmdargs.append(customer)
        cmd.append("AND users.user_name = UPPER(%s)")
        cmdargs.append(username)
        # else:
        #     cmd.append(" AND users.prov_id = %s AND users.customer_id = %s")
        #     cmdargs.append(provider[0])
        #     cmdargs.append(provider[1])

        results = yield from self.execute(cmd, cmdargs, self._display_pre_login, desired)
        return results[0]

    _default_user_info = set((Results.userid,))
    _available_user_info = {
        Results.userid: "users.user_id",
        Results.customerid: "users.customer_id",
        Results.provid: "users.prov_id",
        Results.username: "users.user_name",
        Results.officialname: "users.official_name",
        Results.displayname: "users.display_name",
        Results.state: "users.state",
        Results.ehrstate: "users.ehr_state",
        Results.roles: "users.roles",
        Results.profession: "users.profession",
        Results.lastlogin: "logins2.last_login",
        Results.notify1: "user_pref.notify_primary",
        Results.notify2: "user_pref.notify_secondary"
    }
    _display_user_info = _build_format({
        Results.lastlogin: lambda x: x and _prettify_datetime(x),
        Results.settings: lambda x: x and repr(x)
    })

    @asyncio.coroutine
    def user_info(self, desired, customer, orderby=Results.userid, role=None,
                  officialname=None, ascending=True, startdate=None, enddate=None, limit=None):
        columns = build_columns(desired.keys(), self._available_user_info,
                                self._default_user_info)

        cmd = []
        cmdargs = []
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM users")
        if Results.lastlogin in desired:
            cmd.append("LEFT JOIN ( ")
            cmd.append("SELECT user_name, customer_id, max(logintime) as last_login")
            cmd.append("FROM logins where method != 'failed'")
            cmd.append("GROUP BY user_name,customer_id ) logins2")
            cmd.append("ON (users.user_name = logins2.user_name")
            cmd.append("AND users.customer_id = logins2.customer_id)")
        else:
            # can't sort by date if login field is not being used
            startdate = None
            enddate = None
        if (Results.notify1 in desired) or (Results.notify2 in desired):
            # Left Join in case preferences haven't been set yet (or if support user)
            cmd.append("LEFT JOIN user_pref")
            cmd.append("ON user_pref.user_name = users.user_name")
            cmd.append("AND user_pref.customer_id = users.customer_id")
        cmd.append("WHERE users.customer_id = %s")
        cmdargs.append(customer)
        if role:
            cmd.append("AND %s = ANY(users.roles)")
            cmdargs.append(role)
        if officialname:
            substring = "%" + officialname + "%"
            cmd.append("AND UPPER(users.official_name) LIKE UPPER(%s)")
            cmdargs.append(substring)

        append_extras(cmd, cmdargs, Results.lastlogin, startdate, enddate, orderby, ascending,
                      None, limit, self._available_user_info)

        results = yield from self.execute(cmd, cmdargs, self._display_user_info, desired)
        return results

    @asyncio.coroutine
    def customer_specific_user_info(self, desired, limit="", customer_id=None):
        columns = build_columns(desired.keys(), self._available_user_info,
                                self._default_user_info)

        if customer_id is None:
            return

        cmd = []
        cmdargs = [customer_id]
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM users")
        cmd.append("WHERE customer_id=%s")
        if limit:
            cmd.append(limit)

        results = yield from self.execute(cmd, cmdargs, self._display_user_info, desired)
        return results

    @asyncio.coroutine
    def get_customer_id(self, shortname):
        results = yield from self.execute(['SELECT customer_id FROM customer where abbr = %s;'],
                                          (shortname,), _build_format(), {1: 1})
        return results[0][1]

    _default_customer_info = set((Results.abbr,))
    _available_customer_info = {
        Results.customerid: "customer.customer_id",
        Results.name: "customer.name",
        Results.abbr: "customer.abbr",
        Results.license: "customer.license_type",
        Results.license_exp: "customer.license_exp",
        Results.config: "customer.clientapp_config",
        Results.settings: "customer.clientapp_settings",
    }
    _display_customer_info = _build_format({
        Results.license_exp: lambda x: x and _prettify_datetime(x),
        Results.settings: lambda x: x and json.loads(x)
    })

    @asyncio.coroutine
    def customer_info(self, desired, customer=None, limit=""):
        columns = build_columns(desired.keys(), self._available_customer_info,
                                self._default_customer_info)

        cmd = []
        cmdargs = []
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM customer")
        if customer:
            cmd.append("WHERE customer_id = %s")
            cmdargs.append(customer)
        if limit:
            cmd.append(limit)

        results = yield from self.execute(cmd, cmdargs, self._display_customer_info, desired)
        return results

    _default_patient_info = set((Results.encounter_date,))
    _available_patient_info = {
        Results.patientname: "max(patient.patname)",
        Results.patientid: "encounter.patient_id",
        Results.birthdate: "max(patient.birthdate)",
        Results.sex: "max(patient.sex)",
        Results.encounter_date: "max(encounter.contact_date) AS contact_date",
        Results.encounter_list: "array_agg(encounter.csn || ' ' || encounter.contact_date)",
        Results.cost: "0",
        Results.diagnosis: "'None yet'",
        Results.allergies: "'None'",
        Results.problems: "'None yet'",
        Results.admission: "max(encounter.hosp_admsn_time)",
        Results.lengthofstay: 'array_agg(coalesce(encounter.hosp_disch_time, now()) -' +
                              'encounter.hosp_admsn_time)',
    }
    _display_patient_info = _build_format({
        Results.encounter_list: lambda x: list(map(lambda v: v.split(' '), x)),
        Results.cost: _invalid_num,
    })

    @asyncio.coroutine
    def patient_info(self, desired, user, customer, patients=None, limit="", patient_name="",
                     startdate=None, enddate=None):
        columns = build_columns(desired.keys(), self._available_patient_info,
                                self._default_patient_info)

        cmd = []
        cmdargs = []
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM encounter JOIN patient")
        cmd.append("ON patient.patient_id = encounter.patient_id")
        cmd.append("AND encounter.customer_id = patient.customer_id")
        cmd.append("WHERE encounter.customer_id = %s")
        cmdargs.append(customer)
        cmd.append("AND encounter.visit_prov_id = %s")
        cmdargs.append(user)
        if patient_name:
            substring = "%" + patient_name + "%"
            cmd.append("AND UPPER(patient.patname) LIKE UPPER(%s)")
            cmdargs.append(substring)
        if patients:
            cmd.append("AND encounter.patient_id IN %s")
            cmdargs.append(makelist(patients))
        if startdate:
            cmd.append("AND encounter.hosp_admsn_time >= %s")
            cmdargs.append(startdate)
        if enddate:
            cmd.append("AND encounter.hosp_disch_time < %s")
            cmdargs.append(enddate)
        append_extras(cmd, cmdargs, None, None, None, 'contact_date', True, 'encounter.patient_id',
                      limit, self._available_patient_info)

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
        cmdargs = []
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM diagnosis")
        # cmd.append("WHERE customer_id = %s")
        # cmdargs.append(customer)
        if diagnosis:
            substring = "%" + diagnosis + "%"
            cmd.append("WHERE UPPER(dx_name) LIKE UPPER(%s)")
            cmdargs.append(substring)
        cmd.append("ORDER BY dx_name")

        if limit:
            cmd.append(limit)

        results = yield from self.execute(cmd, cmdargs, self._display_diagnosis_info, desired)
        return list(results)

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
    def total_spend(self, desired, customer, provider=None, patients=None, encounter=None,
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
            cmd.append("AND encounter.patient_id IN %s")
            cmdargs.append(makelist(patients))
        if encounter:
            cmd.append("AND encounter.csn = %s")
            cmdargs.append(encounter)
        append_extras(cmd, cmdargs, Results.datetime, startdate, enddate, None, None,
                      None, None, self._available_total_spend)

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
    def daily_spend(self, desired, provider, customer, patients=None, encounter=None,
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
            cmd.append("AND encounter.patient_id IN %s")
            cmdargs.append(makelist(patients))
        if encounter:
            cmd.append("AND encounter.csn = %s")
            cmdargs.append(encounter)
        append_extras(cmd, cmdargs, Results.date, startdate, enddate, None, None,
                      [Results.date, Results.ordertype], None, self._available_daily_spend)

        results = yield from self.execute(cmd, cmdargs, self._display_daily_spend, desired)
        return results

    _default_alerts = set((Results.datetime,))
    _available_alerts = {
        Results.alertid: "max(alert.alert_id)",
        Results.patientid: "array_agg(alert.patient_id)",
        Results.datetime: "max(alert.alert_datetime)",
        Results.title: "max(alert.long_title)",
        Results.description: "max(alert.long_description)",
        Results.outcome: "avg(alert.outcome)",
        Results.savings: "avg(alert.saving)",
        Results.alerttype: "max(alert.category)",
        Results.ruleid: "max(alert.cds_rule)",
        Results.likes: "COUNT(case when alert_setting_hist.action = 'like' then 1 else null end)",
        Results.dislikes: "COUNT(case when alert_setting_hist.action = 'dislike' then 1 else null end)"
    }
    _display_alerts = _build_format({
        Results.title: lambda x: x or '',
        Results.ruleid: lambda x: x,
        Results.datetime: lambda x: x and _prettify_datetime(x),
        })

    @asyncio.coroutine
    def alerts(self, desired, provider, customer, patients=None, limit="",
               startdate=None, enddate=None, orderid=None, categories=None,
               orderby=Results.datetime, ascending=True, alertid=None):
        columns = build_columns(desired.keys(), self._available_alerts,
                                self._default_alerts)

        cmd = []
        cmdargs = []
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM alert")
        if Results.likes in desired or Results.dislikes in desired:
            cmd.append("LEFT JOIN alert_setting_hist ON alert.alert_id = alert_setting_hist.alert_id")
        cmd.append("WHERE alert.provider_id = %s AND alert.customer_id = %s")
        cmdargs.append(provider)
        cmdargs.append(customer)
        cmd.append("AND alert.validation_status > %s")
        cmdargs.append(ALERT_VALIDATION_STATUS.DEBUG_ALERT.value)
        if patients:
            cmd.append("AND alert.patient_id IN %s")
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
        append_extras(cmd, cmdargs, Results.datetime, startdate, enddate, orderby, ascending,
                      "(CASE WHEN cds_rule IS NULL THEN 'alert.alert_id' " +
                      "|| alert.alert_id::varchar ELSE cds_rule::varchar END)",
                      limit, self._available_alerts)

        results = yield from self.execute(cmd, cmdargs, self._display_alerts, desired)
        return results

    _default_audit_info = set((Results.auditid,))
    _available_audit_info = {
        Results.auditid: "audit.audit_id",
        Results.datetime: "audit.datetime",
        Results.userid: "audit.username",
        Results.patientid: "audit.patient",
        Results.action: "audit.action",
        Results.details: "audit.details",
        Results.device: "audit.device",
        Results.target_user: "audit.target_user || ', ' || audit.target_customer",
    }
    _display_audit_info = _build_format({
        Results.auditid: lambda x: x,
        Results.datetime: lambda x: x and _prettify_datetime(x)
    })

    @asyncio.coroutine
    def audit_info(self, desired, username, customer, startdate=None, enddate=None,
                   orderby=Results.datetime, ascending=False, limit=""):
        columns = build_columns(desired.keys(), self._available_audit_info,
                                self._default_audit_info)

        cmd = []
        cmdargs = []
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM audit")
        cmd.append("WHERE audit.username = %s AND audit.customer_id = %s")
        cmdargs.append(username)
        cmdargs.append(customer)
        append_extras(cmd, cmdargs, Results.datetime, startdate, enddate, orderby, ascending,
                      None, limit, self._available_audit_info)

        results = yield from self.execute(cmd, cmdargs, self._display_audit_info, desired)
        return results

    _default_layout_info = set()
    _available_layout_info = {
        Results.layoutid: "layouts.layoutid",
        Results.widget: "layouts.widget",
        Results.template: "layouts.template",
        Results.element: "layouts.element",
        Results.priority: "layouts.priority"
    }
    _display_layout_info = _build_format({
        Results.layoutid: lambda x: x,
    })

    @asyncio.coroutine
    def layout_info(self, desired, user):
        columns = build_columns(desired.keys(), self._available_layout_info,
                                self._default_layout_info)
        cmd = []
        cmdargs = []
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM layouts")
        cmd.append("INNER JOIN users ON layout_id = ANY(users.layouts) WHERE user_id=%s ORDER BY priority")
        cmdargs.append(user)

        results = yield from self.execute(cmd, cmdargs, self._display_layout_info, desired)
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
    def alert_settings(self, desired, user, customer, alertid=None, ruleid=None,
                       category=None, limit=""):
        columns = build_columns(desired.keys(), self._available_alert_settings,
                                self._default_alert_settings)

        cmd = []
        cmdargs = []
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM alert_setting_hist")
        cmd.append("WHERE alert_setting_hist.user_id = %s")
        cmdargs.append(user)
        cmd.append("AND alert_setting_hist.customer_id = %s")
        cmdargs.append(customer)
        if alertid:
            cmd.append("AND alert_setting_hist.alert_id = %s")
            cmdargs.append(alertid)
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
        Results.ordertype: "order_ord.order_type",
        Results.orderid: "order_ord.order_id",
    }
    # _display_orders = _build_format()

    _display_orders = _build_format({
        Results.datetime: lambda x: x and _prettify_datetime(x),
        })

    @asyncio.coroutine
    def orders(self, desired, customer, encounter=None, patientid=None, ordertypes=None, limit="",
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
            cmd.append("AND order_ord.patient_id in %s")
            cmdargs.append(tuple(patientid))
        if ordertypes:
            cmd.append("AND order_ord.order_type IN %s")
            cmdargs.append(ordertypes)
        append_extras(cmd, cmdargs, Results.datetime, startdate, enddate, Results.datetime, False,
                      None, limit, self._available_orders)

        results = yield from self.execute(cmd, cmdargs, self._display_orders, desired)
        return results

    _default_per_encounter = set((Results.encounterid,))
    _available_per_encounter = {
        Results.patientid: "encounter.patient_id",
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
    def per_encounter(self, desired, provider, customer, patients=None, encounter=None,
                      startdate=None, enddate=None):
        columns = build_columns(desired.keys(), self._available_per_encounter,
                                self._default_per_encounter)

        cmd = []
        cmdargs = []
        cmd.append("SELECT")
        cmd.append(columns)
        cmd.append("FROM order_ord JOIN encounter")
        cmd.append("ON order_ord.encounter_id = encounter.csn")
        cmd.append("AND order_ord.customer_id = encounter.customer_id")
        cmd.append("JOIN patient")
        cmd.append("ON encounter.patient_id = patient.patient_id")
        cmd.append("WHERE encounter.visit_prov_id IN %s")
        cmdargs.append(makelist(provider))
        cmd.append("AND order_ord.customer_id = %s")
        cmdargs.append(customer)
        if patients:
            cmd.append("AND encounter.patient_id IN %s")
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
        cmd.append("GROUP BY encounter.csn, encounter.patient_id, patient.patname")
        # TODO : encounter.patient_id is added to the Group by, need test to
        # make sure we are not losing data

        results = yield from self.execute(cmd, cmdargs, self._display_per_encounter, desired)
        return results

    @asyncio.coroutine
    def encounter_report(self, customer, user, patient, date):
        cmd = 'SELECT EncounterReport((SELECT prov_id FROM users WHERE user_id=%s),%s,%s,%s);'
        cur = yield from self.db.execute_single(cmd, [user, patient, date, customer])
        rows = list(cur)
        try:
            return rows[0][0]
        except:
            return None

    @asyncio.coroutine
    def last_checks(self, customer, protocol, patient, node):
        cmd = ["SELECT details, action, max(datetime) FROM trees.activity",
               "WHERE customer_id=%s",
               "AND canonical_id=(SELECT canonical_id from trees.protocol where protocol_id=%s)",
               "AND patient_id=%s",
               "AND node_id=%s",
               "AND (action='checked' OR action='unchecked')",
               "GROUP BY action, details"]
        cmdargs = [customer, protocol, patient, node]
        results = yield from self.execute(cmd, cmdargs, _build_format(),
                                          {0: 'details', 1: 'action', 2: 'datetime'})
        grouped = {}
        for result in results:
            if (result['details'] not in grouped
               or grouped[result['details']][0] < result['datetime']):
                grouped[result['details']] = (result['datetime'], result['action'])
        ret = {k: v[1] for k, v in grouped.items()}
        return ret

    _available_interactions = {
        Results.activityid: "min(a.activity_id)",
        Results.patientid: "a.patient_id",
        Results.patientname: "min(p.patname)",
        Results.datetime: "min(a.datetime) AS time",
        Results.username: 'min(u.official_name)',
        Results.userid: 'a.user_id',
        Results.provid: 'u.prov_id',
        Results.protocolname: 'min(c.name)',
        Results.protocol: 'a.protocol_id',
        Results.count: 'count(*)',
    }

    _display_interactions = _build_format({
        Results.datetime: lambda x: x and _prettify_datetime(x),
    })

    @asyncio.coroutine
    def interactions(self, desired, customer,
                     # provider=None, patients=None, startdate=None, enddate=None,
                     limit=None):
        columns = build_columns(desired.keys(), self._available_interactions, set())
        cmd = ["SELECT", columns, "FROM trees.activity AS a",
               "INNER JOIN users AS u ON a.user_id=u.user_id",
               "INNER JOIN trees.canonical_protocol AS c ON a.canonical_id = c.canonical_id AND a.customer_id=c.customer_id",
               "INNER JOIN patient AS p ON a.patient_id = p.patient_id AND a.customer_id = p.customer_id ",
               "WHERE a.patient_id IS NOT NULL AND a.customer_id = %s",
               "GROUP BY a.patient_id, a.user_id, a.protocol_id, date_trunc('day', a.datetime)",
               "ORDER BY time DESC"]
        cmdargs = [customer]

        if limit:
            cmd.append(limit)
        results = yield from self.execute(cmd, cmdargs, self._display_interactions, desired)
        return results

    @asyncio.coroutine
    def interaction_details(self, customer, userid, patientid, protocolid, startactivity):
        cmd = ["SELECT node_id, datetime, action, details FROM trees.activity WHERE",
               "customer_id = %s AND user_id = %s AND patient_id = %s AND protocol_id = %s",
               "AND activity_id >= %s ORDER BY activity_id"]
        cmdargs = [customer, userid, patientid, protocolid, startactivity]

        desired = {0: 'node_id', 1: 'datetime', 2: 'action', 3: 'details'}

        results = yield from self.execute(cmd, cmdargs,
                                          _build_format({1: _prettify_datetime}), desired)
        return results

    @asyncio.coroutine
    # @ML.coroutine_trace(print)
    def audit_log(self, username, action, customer, patient=None, device=None,
                  details=None, rows=None, target_user_and_customer=None):
        cmd = ['INSERT INTO audit (datetime, username, action, customer_id']
        cmdargs = [username, action, customer]
        extras = ['now(), %s, %s, %s']
        if patient:
            cmd.append(', patient')
            cmdargs.append(patient)
            extras.append(', %s')
        if device:
            cmd.append(', device')
            cmdargs.append(device)
            extras.append(', %s')
        if details:
            cmd.append(', details')
            cmdargs.append(details)
            extras.append(', %s')
        if rows:
            cmd.append(', rows')
            cmdargs.append(rows)
            extras.append(', %s')
        if target_user_and_customer:
            cmd.append(', target_user, target_customer')
            cmdargs += target_user_and_customer
            extras.append(', %s, %s')
        cmd.append(') values (' + ''.join(extras) + ');')
        if target_user_and_customer:
            cmd.append('INSERT INTO audit (datetime, username, action, customer_id, ')
            cmd.append('details, target_user, target_customer)')
            cmd.append(' VALUES (now(), %s, %s, %s, %s, %s, %s);')
            cmdargs += [target_user_and_customer[0], 'affected by: ' + action,
                        target_user_and_customer[1], details, username, customer]

        yield from self.execute(cmd, cmdargs, {}, {})

    @asyncio.coroutine
    def shared_secret(self):
        cmd = ['SELECT shared FROM shared_bytes ORDER BY created_on DESC LIMIT 1']
        ret = yield from self.execute(cmd, [], _build_format(), {0: 0})
        return ret[0][0]

    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    #####
    # PATHWAYS/PROTOCOLS DATABASE SERVICES
    #####
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    @asyncio.coroutine
    def fetch_rule(self, ruleid):
        cmd = []
        cmd.append("SELECT fullspec, ruleid FROM rules.evirule WHERE ruleid =")
        cmd.append(str(ruleid))
        row = yield from self.db.execute_single(' '.join(cmd) + ';', [])
        result = row.fetchone()
        return result

    @asyncio.coroutine
    def get_protocols(self, customer_id, canonical_id=None, includedeleted=False):
        if canonical_id:
            raise Exception('Not implemented yet')
        cmd = []
        cmdArgs = []
        cmd.append("SELECT current_id, name, canonical_id, folder, enabled")
        cmd.append("FROM trees.canonical_protocol")
        cmd.append("WHERE (customer_id=%s OR customer_id IS NULL)")
        cmdArgs.append(customer_id)
        if not includedeleted:
            cmd.append('AND NOT deleted')
        cmd.append("ORDER BY folder, name")
        ret = yield from self.db.execute_single(' '.join(cmd) + ";", cmdArgs)
        return list(ret)

    @asyncio.coroutine
    def get_protocol_children(self, parent_id, includedeleted=False):
        cmd = []
        cmdArgs = []
        cmd.append("SELECT current_id, name, trees.protocol.canonical_id, trees.protocol.customer_id, users.user_name")
        cmd.append("FROM trees.canonical_protocol")
        cmd.append("INNER JOIN trees.protocol")
        cmd.append("INNER JOIN users on user_id=creator")
        cmd.append("on trees.canonical_protocol.canonical_id = trees.protocol.canonical_id")
        cmd.append("WHERE trees.canonical_protocol.parent_id=%s")
        cmdArgs.append(parent_id)
        if not includedeleted:
            cmd.append('AND NOT trees.canonical_protocol.deleted')
        ret = yield from self.db.execute_single(' '.join(cmd) + ";", cmdArgs)
        return list(ret)

    @asyncio.coroutine
    def propagate_pathway(self, parent_canonical, child_canonical, parent_customer, child_customer):
        # copy the newly published version of a pathway
        cmd = ["INSERT INTO trees.protocol (customer_id, description, minage, maxage, sex,",
               "full_spec, canonical_id, deleted, creator, parent_id, tags)",
               "SELECT %s, p.description, p.minage, p.maxage, p.sex, p.full_spec, %s, false,",
               "p.creator, 0, p.tags",
               "FROM trees.canonical_protocol c",
               "INNER join trees.protocol p",
               "ON c.current_id = p.protocol_id",
               "WHERE c.canonical_id = %s AND c.customer_id = %s",
               "returning trees.protocol.protocol_id"]
        cmdArgs = [child_customer, child_canonical, parent_canonical, parent_customer]
        ret = yield from self.db.execute_single(' '.join(cmd) + ";", cmdArgs)
        return list(ret)

    @asyncio.coroutine
    def create_protocol(self, treeJSON, customer_id, user_id, folder=None):

        cmd = ["SELECT trees.insertprotocol(%s, %s, %s, %s, %s, %s, %s, %s)"]
        cmdArgs = [json.dumps(treeJSON), customer_id, user_id, treeJSON['name'],
                   folder, 0.00, 200.00, '%']
        try:
            cur = yield from self.db.execute_single(' '.join(cmd) + ";", cmdArgs)
            tree_id, canonical_id = cur.fetchone()[0]
            # Insert a record into alert_config so that the Pathway actually fires (it's referenced in the evalnode()
            # PL/pgsql function
            cmd = ["INSERT INTO alert_config (customer_id, department, category, rule_id, validation_status, priority)",
                   "VALUES (%s, %s, %s, %s, %s, %s)"]
            cmdArgs = [customer_id, -1, "PATHWAY", canonical_id, 400, 100]
            cur = yield from self.db.execute_single(' '.join(cmd) + ";", cmdArgs)

            # Update/Insert the trees.codelist records for the protocol
            yield from self.upsert_codelists(treeJSON, canonical_id)

            # Return Tree_ID to the front-end
            return tree_id
        except:
            ML.EXCEPTION("Error Inserting {} Protocol for Customer #{}".format(treeJSON['name'], customer_id))
        return None

    @asyncio.coroutine
    def copy_protocol(self, customer_id, user_id, protocol_id, folder=None):

        cmd = ["SELECT trees.insertprotocol",
               "(trees.protocol.full_spec, %s, %s, trees.canonical_protocol.name, %s, %s, %s, %s,",
               "trees.protocol.canonical_id, trees.protocol.protocol_id)",
               "FROM trees.protocol INNER JOIN trees.canonical_protocol",
               "ON trees.protocol.canonical_id = trees.canonical_protocol.canonical_id",
               "WHERE trees.protocol.protocol_id=%s"]
        cmdArgs = [customer_id, user_id, folder, 0.00, 200.00, '%', protocol_id]
        try:
            cur = yield from self.db.execute_single(' '.join(cmd) + ";", cmdArgs)
            tree_id, canonical_id = cur.fetchone()[0]
            # Insert a record into alert_config so that the Pathway actually fires (it's referenced in the evalnode()
            # PL/pgsql function
            cmd = ["INSERT INTO alert_config (customer_id, department, category, rule_id, validation_status, priority)",
                   "VALUES (%s, %s, %s, %s, %s, %s)"]
            cmdArgs = [customer_id, -1, "PATHWAY", canonical_id, 400, 100]
            cur = yield from self.db.execute_single(' '.join(cmd) + ";", cmdArgs)

            full_spec = yield from self.get_protocol(customer_id, tree_id)

            # Update/Insert the trees.codelist records for the protocol
            yield from self.upsert_codelists(full_spec, canonical_id)

            # Return Tree_ID to the front-end
            return {'path_id': tree_id, 'canonical_id': canonical_id, 'full_spec': full_spec, 'folder': folder}
        except:
            ML.EXCEPTION("Error Copying {} Protocol for Customer #{}".format(protocol_id, customer_id))
        return None

    @asyncio.coroutine
    def upsert_codelists(self, treeDict, canonical_id):

        root_node_id = treeDict.get('nodeID', None)

        cmd = ["DELETE FROM trees.codelist",
               "WHERE canonical_id=%s AND "
               "node_id=%s"]
        cmdArgs = [canonical_id, root_node_id]
        yield from self.db.execute_single(' '.join(cmd), extra=cmdArgs)

        for triggerGroup in treeDict.get('triggers'):

            # Extract the Group Relationships
            # groupRelationship = triggerGroup.get('relationship')

            triggerGroupDetails = triggerGroup.get('details', None)

            # Insert the Protocol Triggering Codelist(s) for ENCOUNTER Diagnoses
            enc_dx_triggers = triggerGroupDetails.get('enc_dx', None)
            if enc_dx_triggers:
                yield from self.upsert_snomed_triggers(canonical_id, root_node_id, 'enc_dx', enc_dx_triggers)

            # Insert the Protocol Triggering Codelist(s) for PROBLEM LIST Diagnoses
            pl_dx_triggers = triggerGroupDetails.get('pl_dx', None)
            if pl_dx_triggers:
                yield from self.upsert_snomed_triggers(canonical_id, root_node_id, 'pl_dx', pl_dx_triggers)

            # Insert the Protocol Triggering Codelist(s) for HISTORIC Diagnoses
            hist_dx_triggers = triggerGroupDetails.get('hist_dx', None)
            if hist_dx_triggers:
                yield from self.upsert_snomed_triggers(canonical_id, root_node_id, 'hist_dx', hist_dx_triggers)

            # Insert the Protocol Triggering Codelist(s) for ALL Diagnoses
            all_dx_triggers = triggerGroupDetails.get('all_dx', None)
            if all_dx_triggers:
                yield from self.upsert_snomed_triggers(canonical_id, root_node_id, 'all_dx', all_dx_triggers)

            # Insert codelists for Procedure History
            hist_proc_triggers = triggerGroupDetails.get('hist_proc')
            if hist_proc_triggers:
                yield from self.upsert_snomed_triggers(canonical_id, root_node_id, 'hist_proc', hist_proc_triggers)

    @asyncio.coroutine
    def upsert_snomed_triggers(self, canonical_id, node_id, list_type, triggers):

        for cl in triggers:
            # Parse the "exists" JSON element FROM a string INTO a Python integer
            str_boolean = cl.get('exists', None)
            if str_boolean:
                exists = self.convert_string_to_boolean(str_boolean)
            else:
                exists = None

            # If it's a procedure list, get the str_list
            if list_type == 'hist_proc':
                str_list = cl.get('code', None)
            else:
                # Parse the "code" list of string SNOMEDS into Python integers
                str_list = cl.get('code', None)
                int_list = [int(sl) for sl in str_list]

            # Historic Diagnoses have the framemin/framemax that Encounter Diagnoses do not have, grab 'em
            if list_type == 'hist_dx':
                framemin = int(cl.get('minDays', None))
                framemax = int(cl.get('maxDays', None))
            # Give Encounter Diagnoses a framemin/framemax that will never fail
            else:
                framemin = -99999
                framemax = 99999

            cmd = ["SELECT trees.upsert_codelist(%s, %s, %s::varchar, %s, %s::integer[], %s::varchar[], %s, %s)"]

            # Command arguments for the str-based codelist
            if list_type == 'hist_proc':
                cmdArgs = [canonical_id, node_id, list_type, exists, None, str_list, framemin, framemax]
            # Command arguments for the int-based codelist
            else:
                cmdArgs = [canonical_id, node_id, list_type, exists, int_list, None, framemin, framemax]

            yield from self.db.execute_single(' '.join(cmd), extra=cmdArgs)

    def convert_string_to_boolean(self, str):

        if str is None:
            raise Exception("The EXISTS true/false string sent from the Pathways Rule Editor did not supply a valid string")
        elif str.lower() == 'true':
            return True
        elif str.lower() == 'false':
            return False
        else:
            raise Exception("The EXISTS true/false string sent from the Pathways Rule Editor did not supply a valid string")

    @asyncio.coroutine
    def get_protocol(self, customer_id, protocol_id=None):
        cmd = ["SELECT full_spec from trees.protocol",
               "WHERE protocol_id=%s AND (customer_id IS NULL OR customer_id=%s)"]
        cmdArgs = [protocol_id, customer_id]
        try:
            cur = yield from self.db.execute_single(" ".join(cmd) + ";", cmdArgs)
            result = cur.fetchone()[0]
            result['pathid'] = protocol_id
            return result
        except:
            ML.EXCEPTION("Error Selecting TreeID #{}".format(protocol_id))
            return None

    @asyncio.coroutine
    def get_protocol_history(self, customer_id, canonical_id, limit=None):
        cmd = ["SELECT protocol_id, trees.protocol.canonical_id, creation_time, public.users.official_name, ",
               "(case trees.canonical_protocol.current_id WHEN trees.protocol.protocol_id THEN 1 ELSE 0 END)",
               " as active, trees.canonical_protocol.enabled ",
               "from trees.protocol",
               "INNER JOIN public.users ON users.user_id = trees.protocol.creator",
               "INNER JOIN trees.canonical_protocol",
               "ON trees.protocol.canonical_id = trees.canonical_protocol.canonical_id",
               "WHERE trees.protocol.canonical_id=%s AND (trees.protocol.customer_id IS NULL",
               "OR trees.protocol.customer_id=%s)",
               "ORDER BY active DESC, creation_time DESC"]
        cmdArgs = [canonical_id, customer_id]
        if limit:
            cmd.append(limit)

        ret = yield from self.db.execute_single(' '.join(cmd) + ";", cmdArgs)

        return list(ret)

    @asyncio.coroutine
    def select_active_pathway(self, customer_id, canonical_id, protocol_id):
        cmd = ["UPDATE trees.canonical_protocol SET current_id=%s"]
        cmdArgs = [protocol_id]

        if canonical_id == 0:
            cmd.append('WHERE canonical_id = (SELECT canonical_id FROM trees.protocol where protocol_id=%s)')
            cmdArgs.append(protocol_id)
        else:
            cmd.append('WHERE canonical_id = %s')
            cmdArgs.append(canonical_id)
        cmd.append("and customer_id=%s")
        cmdArgs.append(customer_id)

        try:
            yield from self.db.execute_single(" ".join(cmd) + ";", cmdArgs)
        except:
            ML.EXCEPTION("Error Updating TreeID #{}".format(canonical_id))

    @asyncio.coroutine
    def rename_pathway(self, customer_id, canonical_id, new_name):
        cmd = ["UPDATE trees.canonical_protocol SET name = %s",
               "WHERE canonical_id = %s and customer_id = %s"]
        cmdArgs = [new_name, canonical_id, customer_id]

        try:
            yield from self.db.execute_single(" ".join(cmd) + ";", cmdArgs)
        except:
            ML.EXCEPTION("Error Updating TreeID #{}".format(canonical_id))

    @asyncio.coroutine
    def toggle_pathway(self, customer_id, canonical_id, enabled=False):
        cmd = ["UPDATE trees.canonical_protocol SET enabled=%s ",
               "WHERE (canonical_id=%s and customer_id=%s) RETURNING name, current_id"]
        cmdArgs = [enabled, canonical_id, customer_id]
        try:
            ret = yield from self.db.execute_single(" ".join(cmd) + ";", cmdArgs)
            return ret

        except:
            ML.EXCEPTION("Error Updating TreeID #{}".format(canonical_id))
            return None

    @asyncio.coroutine
    def delete_protocol(self, customer_id, protocol_id=None, canonical_id=None):
        if canonical_id:
            cmd = ["UPDATE trees.canonical_protocol SET deleted=TRUE ",
                   "WHERE (canonical_id=%s and customer_id=%s)"]
            cmdArgs = [canonical_id, customer_id]
            yield from self.delete_codelists_deactivate_alert_config(canonical_id)

        elif protocol_id:
            cmd = ["UPDATE FROM trees.protocol SET deleted=TRUE",
                   "WHERE (protocol_id=%s AND customer_id=%s)"]
            cmdArgs = [protocol_id, customer_id]
        else:
            ML.EXCEPTION('Calling delete_protocol without a protocol or canonical id')
        try:
            yield from self.db.execute_single(" ".join(cmd) + ";", cmdArgs)
        except:
            ML.EXCEPTION("Error Deleting TreeID #{}".format(protocol_id))

    @asyncio.coroutine
    def delete_codelists_deactivate_alert_config(self, canonical_id):
        cmd = ["BEGIN;",
               "DELETE FROM trees.codelist",
               "WHERE canonical_id=%s;",
               "UPDATE public.alert_config",
               "SET validation_status=-100",
               "WHERE rule_id=%s;",
               "COMMIT;"]
        cmdArgs = [canonical_id, canonical_id]
        yield from self.db.execute_single(' '.join(cmd), extra=cmdArgs)

    @asyncio.coroutine
    def update_protocol(self, protocol_id, customer_id, user_id, protocol_json):
        cmd = ['SELECT trees.updateprotocol(%s, %s, %s, %s)']
        cmdArgs = [protocol_id, json.dumps(protocol_json), customer_id, user_id]
        newid = None
        try:
            cur = yield from self.db.execute_single(" ".join(cmd) + ";", cmdArgs)
            newid, canonical_id = cur.fetchone()[0]
            # Update/Insert the trees.codelist records for the protocol
            yield from self.upsert_codelists(protocol_json, canonical_id)

        except:
            newid = None
            ML.EXCEPTION("Error Updating TreeID #{}".format(protocol_json.get('pathid', None)))

        finally:
            return newid

    @asyncio.coroutine
    def post_protocol_activity(self, customer_id, user_id, activity_msg):
        column_map = ["customer_id", "user_id", "patient_id", "protocol_id",
                      "node_id", "datetime", "action", 'details', 'canonical_id']
        columns = DBMapUtils().select_rows_from_map(column_map)

        cmd = ["INSERT INTO trees.activity(" + columns + ")",
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, (SELECT canonical_id FROM trees.protocol WHERE protocol_id = %s)) RETURNING activity_id"]

        node_state_raw = activity_msg.get('node_state', None)
        node_state = node_state_raw.split("-")

        # Splice the last element from the node state (which returns a single element list),
        # and then take the only element from it and turn it into an integer
        node_id = node_state[-1:][0]
        protocol_id = activity_msg.get('protocol_id', None)
        cmdArgs = [customer_id,
                   user_id,
                   activity_msg.get('patient_id', None),
                   protocol_id,
                   node_id,
                   activity_msg.get('datetime', None),
                   activity_msg.get('action', None),
                   activity_msg.get('details', None),
                   protocol_id]
        try:
            cur = yield from self.db.execute_single(" ".join(cmd) + ";", cmdArgs)
            result = cur.fetchone()[0]
        except:
            ML.EXCEPTION("Error Inserting Protocol Activity for User: {}, Protocol: {}, Node: {}".format(user_id,
                                                                                                         activity_msg.get('protocol_id', None),
                                                                                                         node_id))
            result = None

        if result and isinstance(result, int):
            return True
        else:
            return False

    @asyncio.coroutine
    def post_pathway_location(self, customer_id, canonical_id, location_msg):

        location = location_msg.get('location', None)
        # position = location_msg.get('position', None)

        cmd = ["UPDATE trees.canonical_protocol set folder = %s WHERE customer_id=%s and canonical_id=%s"]
        cmdArgs = [location, customer_id, canonical_id]

        result = yield from self.execute(cmd, cmdArgs, {}, {})
        if result:
            return True
        return False

    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    #####
    # TIMED FOLLOW-UP/TASKS DATABASE SERVICES
    #####
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    @asyncio.coroutine
    def insert_followup_task(self, customer_id, author_id, target_username, patient_id, delivery_method,
                             due, expire, msg_subject, msg_body):
        column_map = ["customer_id", "author_id", "patient_id", "delivery",
                      "status", "due", "expire", "msg_subject", "msg_body", "user_id"]
        columns = DBMapUtils().select_rows_from_map(column_map)
        cmd = ["INSERT INTO public.followuptask(" + columns + ")"]
        cmdArgs = [customer_id, author_id, patient_id, delivery_method, FOLLOWUPTASK_STATUS.pending.value,
                   due, expire, msg_subject, msg_body]

        # If a target username is supplied, we need to add the SQL logic that will allow look-up of the target user_id
        if target_username:
            # cmd.append("VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, users.user_id)")
            cmd.append("SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, users.user_id")
            cmd.append("from users where user_name=%s and customer_id=%s")
            cmdArgs.append(target_username)
            cmdArgs.append(customer_id)
        # If no target_username is supplied, make the user_id the same as the author_id
        else:
            cmd.append("VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
            cmdArgs.append(author_id)
        cmd.append("RETURNING task_id")

        task_id = None
        try:
            cur = yield from self.db.execute_single(" ".join(cmd) + ";", cmdArgs)
            task_id = cur.fetchone()[0]
        except:
            ML.EXCEPTION("Error inserting Task - AuthorID={}, Subject={}".format(author_id, msg_subject))

        if task_id and isinstance(task_id, int):
            return task_id
        else:
            return False

    _default_task_info = set((Results.taskid,))
    _available_task_info = {
        Results.username: "users.user_name",
        Results.taskid: "followuptask.task_id",
        Results.customerid: "followuptask.customer_id",
        Results.authorid: "followuptask.author_id",
        Results.userid: "followuptask.user_id",
        Results.patientid: "followuptask.patient_id",
        Results.delivery_method: "followuptask.delivery",
        Results.task_status: "followuptask.status",
        Results.due_datetime: "followuptask.due",
        Results.expire_datetime: "followuptask.expire",
        Results.msg_subject: "followuptask.msg_subject",
        Results.msg_body: "followuptask.msg_body"
    }
    _display_task_info = _build_format({})

    @asyncio.coroutine
    def get_followup_tasks(self, customer_id=None, user_id=None, author_id=None, patient_id=None, datetime=None):
        desired = {
            Results.username: "user_name",
            Results.taskid: "task_id",
            Results.customerid: "customer_id",
            Results.authorid: "author_id",
            Results.userid: "user_id",
            Results.patientid: "patient_id",
            Results.delivery_method: "delivery_method",
            Results.task_status: "status",
            Results.due_datetime: "due",
            Results.expire_datetime: "expire",
            Results.msg_subject: "msg_subject",
            Results.msg_body: "msg_body",
        }
        columns = build_columns(desired.keys(), self._available_task_info,
                                self._default_task_info)
        cmd = ["SELECT",
               columns,
               "FROM public.followuptask",
               "INNER JOIN public.users ON followuptask.user_id = users.user_id"]
        cmdArgs = []
        if customer_id and datetime:
            pass
        elif user_id and patient_id:
            pass
        elif author_id and patient_id:
            pass
        elif datetime:
            timeframe_min = datetime
            timeframe_max = datetime + dateutil.relativedelta.relativedelta(minutes=60)
            cmd.append("WHERE followuptask.due>=%s and followuptask.due <=%s and followuptask.status=%s")
            cmdArgs.extend([timeframe_min, timeframe_max, FOLLOWUPTASK_STATUS.pending.value])
        elif user_id:
            pass
        elif author_id:
            pass

        tasks = None
        try:
            tasks = yield from self.execute(cmd, cmdArgs, self._display_task_info, desired)
        except:
            ML.EXCEPTION("Error Querying for Tasks")

        return tasks

    @asyncio.coroutine
    def update_followup_task_status(self, task_id, status):
        cmd = ["UPDATE public.followuptask",
               "SET status=%s WHERE task_id=%s"]
        cmdArgs = [status, task_id]
        yield from self.db.execute_single(" ".join(cmd) + ";", cmdArgs)

    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    #####
    # NOTIFICATION SERVICE DATABASE SERVICES
    #####
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    @asyncio.coroutine
    def insert_log(self, customer_id, log_datetime, tags, body, username=None, device=None):
        cmd = ["INSERT INTO log(customer_id, log_datetime, username, device, tags, body)",
               "VALUES (%s, %s, %s, %s, (select get_log_tags(%s)), %s)",
               "RETURNING log_id"]
        cmdArgs = [customer_id, log_datetime, username, device, tags, body]

        try:
            log_id = yield from self.db.execute_single(" ".join(cmd) + ";", cmdArgs)
            ML.DEBUG("Log ID {} added".format(log_id))
            return True
        except Exception:
            return False
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    #####
    # USER GROUP DATABASE SERVICES
    #####
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    _default_group_info = set((Results.groupid,))
    _available_group_info = {
        Results.groupid: "user_group.group_id",
        Results.group_name: "user_group.group_name",
    }
    _display_group_info = _build_format({})

    @asyncio.coroutine
    def get_groups(self, customer_id):
        desired = {
            Results.groupid: "id",
            Results.group_name: "term",
        }
        columns = build_columns(desired.keys(), self._available_group_info,
                                self._default_group_info)
        cmd = ["SELECT",
               columns,
               "FROM public.user_group",
               "WHERE customer_id=%s"]
        cmdArgs = [customer_id]

        rtn = None
        try:
            groups = yield from self.execute(cmd, cmdArgs, self._display_group_info, desired)
            rtn = groups
        except:
            ML.EXCEPTION("Error Querying Groups for CustomerID={}".format(customer_id))

        finally:
            return rtn
