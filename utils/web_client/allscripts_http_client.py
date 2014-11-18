import utils.web_client.http_client as http
from aiohttp import OsConnectionError
import asyncio
import json
from functools import wraps
from xml.etree import ElementTree as ETree
from enum import Enum
from maven_config import MavenConfig
import maven_logging as ML
from maven_logging import WARN, EXCEPTION, INFO
import utils.database.memory_cache as memory_cache
import utils.api.pyfhir.pyfhir_generated as FHIR_API
import dateutil.parser
from utils.enums import USER_STATE, CONFIG_PARAMS

ALLSCRIPTS_NUM_PARAMETERS = 6
logger = ML.get_logger()
ML.set_debug()


class COMPLETION_STATUSES(Enum):
    Undefined = 'Undefined'
    Ordered = 'Ordered'
    Preliminary = 'Preliminary'
    Final = 'Final'
    Reviewed = 'Reviewed'
    Pending = 'Pending'
    Canceled = 'Canceled'
    All = 'All'


class CLINICAL_SUMMARY(Enum):
    Allergies = 'allergies'
    History = 'history'
    Immunizations = 'immunizations'
    Medications = 'medications'
    Problems = 'problems'
    Vitals = 'vitals'
    Results = 'results'
    All = 'list'


class TASK_TYPE(Enum):
    REFERRAL = "Referral"
    REVIEW = "Review"
    SENDCHART = "Send Chart"


class UnauthorizedUser(Exception):
    pass


class AllscriptsError(http.HttpClientException):
    pass


def is_power_two(num: int):
    return num != 0 and ((num & (num - 1)) == 0)


def check_output(jobj, empty_ok=False):
    exc = None
    if not jobj:
        raise AllscriptsError("Query returned empty string")
    try:
        obj = json.loads(jobj)
        if "Error" in obj[0]:
            exc = AllscriptsError(obj[0]["Error"])
        elif (not empty_ok) and len(list(obj[0].values())[0]) == 0:
            # exc = AllscriptsError("Query returned empty list")
            return obj
        else:
            return obj
    except:
        raise AllscriptsError("parse error: " + str(jobj))
    raise exc


def isoformat(d: {str, 'date', 'datetime'}):
    if type(d) is str:
        return d
    try:
        return d.replace(microsecond=0).isoformat()
    except TypeError:
        return d.isoformat()


def isoformatday(d: {'date', 'datetime'}):
    if type(d) is str:
        return d
    try:
        return d.date().isoformat()
    except AttributeError:
        return d.isoformat()

hour_cache = memory_cache.MemoryCache(timeout=3600)


class allscripts_api(http.http_api):

    def __init__(self, config: dict):
        """ initialize this adapter for the allscripts professional API
        :params configname: the name of the configuration section in the MavenConfig map
        it's required parameters are:
          CONFIG_BASEURL, CONFIG_APPNAME, CONFIG_APPUSERNAME, CONFIG_APPPASSWORD
        it's optional parameter is CONFIG_OTHERHEADERS
        """
        http.http_api.__init__(self, config, other_headers={"Content-Type": "application/json"})
        self.config = config
        self.postprocess = (lambda x: list(x[0].values())[0])
        self.appname = self.config.get(CONFIG_PARAMS.EHR_API_APPNAME.value, "")
        self.appusername = self.config.get(CONFIG_PARAMS.EHR_API_SVC_USER.value, "")
        self.apppassword = self.config.get(CONFIG_PARAMS.EHR_API_PASSWORD.value, "")
        self.unitytoken = None

    def update_config(self, config):
        appname = self.config.get(CONFIG_PARAMS.EHR_API_APPNAME.value, "")
        appusername = self.config.get(CONFIG_PARAMS.EHR_API_SVC_USER.value, "")
        apppassword = self.config.get(CONFIG_PARAMS.EHR_API_PASSWORD.value, "")
        http_update = http.http_api.update_config(self, config)
        if (appname == self.appname
           and appusername == self.appusername
           and apppassword == self.apppassword
           and not http_update):
            return False
        else:
            self.appname = appname
            self.appusername = appusername
            self.apppassword = apppassword
            self.unitytoken = None
            return True

    def _build_message(self, action: str, *args: [str], user: str=None,
                       patient: str=None, data='null') -> {str: str}:
        """ builds the data section of a message to allscripts
        :param action: the API method to invoke
        :param user: the provider's userid for whom we perform this
        :param patient: the patient whose data to get/interact with
        :param data: seem to always be None for Get calls
        :param *arg: allscripts functions take other parameters as positional
        """
        if len(args) < ALLSCRIPTS_NUM_PARAMETERS:
            args += ('',) * (ALLSCRIPTS_NUM_PARAMETERS - len(args))
        ret = {'Action': action,
               'Appname': self.appname,
               'Token': self.unitytoken,
               'Data': data}
        if user:
            ret['AppUserID'] = user
        if patient:
            ret['PatientID'] = patient

        ret.update(zip(['Parameter' + str(n + 1) for n in range(ALLSCRIPTS_NUM_PARAMETERS)], args))
        return ret

    @asyncio.coroutine
    def _login(self, fut):
        """ function to acquire a new unity token.
        It takes a future to set when it's done.  Only one
        of these functions can be active at a time (other
        tasks needing the token must wait on the future).
        :param fut: an empty future to set_result on when
                    the token is acquired
        """
        while not fut.done():
            try:
                req = yield from self.post('/json/GetToken',
                                           Username=self.appusername,
                                           Password=self.apppassword)
                if not req or req.startswith('error'):
                    raise AllscriptsError('Could not get token - ' + req)
                INFO('Acquired token')
                if self.unitytoken == fut:
                    self.unitytoken = req
                fut.set_result(req)
            except Exception as e:
                WARN(e)
            if not fut.done():
                yield from asyncio.sleep(10)

    def _require_token(func: 'function') -> 'function':
        """ decorator for functions which require a security token before executing
        """
        co_func = asyncio.coroutine(func)

        def worker(self, *args, **kwargs):
            lasterror = None
            lasterrorcount = 0
            while True:
                if not self.unitytoken:
                    fut = asyncio.Future()
                    self.unitytoken = fut
                    asyncio.Task(self._login(fut))
                if isinstance(self.unitytoken, asyncio.Future):
                    yield from self.unitytoken
                try:
                    if self.unitytoken:
                        return (yield from co_func(self, *args, **kwargs))
                except AllscriptsError as e:
                    if lasterror != e.args[0]:
                        lasterrorcount = 0
                        lasterror = e.args[0]
                        EXCEPTION('allscripts exception')
                    else:
                        lasterrorcount += 1
                        if is_power_two(lasterrorcount):
                            WARN("%s times: %s" % (lasterrorcount, e.args[0]))
                    if e.args[0].find('you have been logged out') >= 0 or e.args[0].find('Action is not valid for this license') >= 0:
                        self.unitytoken = None
                        if not lasterrorcount:
                            WARN("resetting unitytoken: " + e.args[0])
                    yield from asyncio.sleep(30)

        return asyncio.coroutine(wraps(func)(worker))

    @asyncio.coroutine
    def test_login(self):
        """ Tests a login and captures the unitytoken, returns None on success, raises on failure
        """
        req = yield from self.post('/json/GetToken',
                                   Username=self.appusername,
                                   Password=self.apppassword)
        if not req:
            raise AllscriptsError('Could not log into Allscripts server')
        elif req.startswith('error'):
            raise AllscriptsError('Could not log into Allscripts server: %s' % (req,))
        else:
            self.unitytoken = req

    @hour_cache.cache_lookup('GetServerInfo', lookup_on_none=True,
                             key_function=memory_cache.allargs)
    @_require_token
    def GetServerInfo(self):
        """ Takes no arguments and returns:
        Returns values for server time zone, server time server datetime offset,
        what type of unity system, the product version, and the start time of this
        unity installation
        """
        try:
            ret = yield from self.post('/json/MagicJson',
                                       data=self._build_message('GetServerInfo'))
            return self.postprocess(check_output(ret))[0]
        except OsConnectionError:
            return False

    @_require_token
    def GetPatient(self, username: str, patient: str):
        """ Gets (demographic and contact mostly) information about a patient
        :param user: the allscripts EHR user ID
        :param patient: the allscripts internal patient ID (from GetPatientByMRN,
                        SearchPatients, or other)
        Returns phone/address/email/employer/ssn/etc (all not needed)
        also, name/dob/gender (needed) and much more
        """
        ret = yield from self.post('/json/MagicJson',
                                   data=self._build_message('GetPatient', user=username,
                                                            patient=patient))
        return self.postprocess(check_output(ret))[0]

    @_require_token
    def GetChangedPatients(self, username: str, since: {str, 'date', 'datetime'}):
        """ Gets a list of patientIDs for patients whose information has changed recently
        :param username: the allscripts ehr username
        :param since: a timestamp - only get patients who changed after this time
                      can be a date/datetime object, or a string "YYYY-MM-DDTHH:MM:SS"
        returns a list of patient ids
        """
        since = isoformat(since)
        ret = yield from self.post('/json/MagicJson',
                                   data=self._build_message('GetChangedPatients', since,
                                                            user=username))
        return [x['patientid'] for x in self.postprocess(check_output(ret, True))]

    @_require_token
    def GetSchedule(self, username: str, startdate: {str, 'date', 'datetime'},
                    changedsince: {str, 'date', 'datetime'}=None, soughtuser: str=None):
        """ Gets a list of scheduled appointments for a provider.
        Each element in the list includes (among others):
        Status (i.e. pending), patiendID, Duration, Patient (full name), TimeIn, ProviderID,
        :param username: the user whose schedule to check
        :param startdate: appears to not really be a start date, but the date to lookup
                          can be a date/datetime object, or a string as "YYYY-MM-DDTHH:MM:SS"
        :param changedsince: a timestamp filter like in GetChangedPatients
        :param soughtuser: get the schedule for a different allscripts user (provider)
        """
        startdate = isoformat(startdate)
        if changedsince:
            changedsince = isoformat(changedsince)
        message = self._build_message('GetSchedule',
                                      startdate,
                                      changedsince or '',
                                      'N',  # includepicture
                                      soughtuser or '',
                                      user=username)

        ret = yield from self.post('/json/MagicJson', data=message)
        return self.postprocess(check_output(ret))

    @staticmethod
    def _append_xml_with_data_as_attribute(root: ETree.Element, name: str, value: str=None):
        child = ETree.Element(name)
        if value:
            child.set('value', value)
        root.append(child)
        return child

    @staticmethod
    def _append_xml_with_data_as_text(root: ETree.Element, name: str, value: str=None):
        child = ETree.Element(name)
        if value:
            child.text = value
        root.append(child)
        return child

    @_require_token
    def GetProcedures(self, username: str, patient: str,
                      completionstatuses: [COMPLETION_STATUSES]=None,
                      rulenames: [str]=None, rulenameexactmatch: bool=False):
        """ Gets a list of procedures for a given patient
        :param username: the allscripts user requesting the data
        :param patient: the patient to search for
        :param completionstatuses: a list containing the acceptable completion statuses
                                   the default [] means get everything
                                   Get the values from the enum COMPLETION_STATUSES
        :param rulenames: the name of the rule thats associated with the procedure
        :param rulenameexactmatch: are the rulenames exact matches, or prefix matches
        """
        XML = ETree.Element('ProcedureSearchCriteria')
        self._append_xml_with_data_as_attribute(XML, 'PatientID', patient)
        self._append_xml_with_data_as_attribute(XML, 'UserLoginName', username)
        completionXML = self._append_xml_with_data_as_attribute(XML, 'CompletionStatuses')
        if completionstatuses:
            for cs in completionstatuses:
                self._append_xml_with_data_as_attribute(completionXML, 'CompletionStatus', cs.value)
        else:
            self._append_xml_with_data_as_attribute(completionXML, 'CompletionStatus', COMPLETION_STATUSES.All.value)
        if rulenames:
            rulenameXML = self._append_xml_with_data_as_attribute(XML, 'RuleNames',
                                                                  'Y' if rulenameexactmatch else 'N')
            for rn in rulenames:
                self._append_xml_with_data_as_attribute(rulenameXML, 'RuleName', rn)
        message = self._build_message('GetProcedures',
                                      ETree.tostring(XML, 'unicode'),
                                      user=username)
        ret = yield from self.post('/json/MagicJson', data=message)
        # allscripts returns this as a json, containing an xml string
        # step 1, check if the string is empty
        ret = self.postprocess(check_output(ret))
        if ret:
            # allscripts returns an XML string, but they split it up in an odd way.
            # it looks like [{'key1':'the text is spl'},{'key1':'it into two'}]
            # step 2 is putting it back together
            ret = ''.join([list(m.values())[0] for m in ret])
            # now that we have an XML string, parse it
            ret = ETree.fromstring(ret)
            # the string should have <Procedures> wrapping a list of <Procedures>
            # where each <Procedure>'s attributes are what's important.
            # we'll return a list of the attribute maps
            ret = [child.attrib for child in ret.getchildren()]
        else:
            # the string is empty, return the empty list
            ret = []
        return ret

    @_require_token
    def GetClinicalSummary(self, username: str, patient: str, sections: [CLINICAL_SUMMARY]=None):
        """ Gets lots of clinical data about a patient
        :param username: the allscripts user
        :param patient: the patient to search for
        :param sections: a filter, taken from the CLINICAL_SUMMARY enum to filter results
                         the default None does not filter
        """
        ret = yield from self.post('/json/MagicJson',
                                   data=self._build_message('GetClinicalSummary',
                                                            sections.value if sections else 'list',
                                                            user=username,
                                                            patient=patient))
        return self.postprocess(check_output(ret))

    @_require_token
    def GetPatientSections(self, username: str, patient: str, months: int):
        """
        """
        ret = yield from self.post('/json/MagicJson',
                                   data=self._build_message('GetPatientSections',
                                                            str(months),
                                                            user=username, patient=patient))
        return self.postprocess(check_output(ret))

    @_require_token
    def GetPatientByMRN(self, username, patientMRN):
        """
        """
        ret = yield from self.post('/json/MagicJson',
                                   data=self._build_message('GetPatientByMRN',
                                                            patientMRN.strip('#'),
                                                            user=username))
        return self.postprocess(check_output(ret))

    @_require_token
    def GetLastLogs(self, username):
        """
        """
        ret = yield from self.post('/json/MagicJson',
                                   data=self._build_message('LastLogs',
                                                            "N",
                                                            "N",
                                                            "50",
                                                            user=username))
        return self.postprocess(check_output(ret))

    @_require_token
    def GetPatientCDA(self, username, patient):
        """
        """
        ret = yield from self.post('/json/MagicJson',
                                   data=self._build_message('GetPatientCDA',
                                                            user=username, patient=patient))
        return self.postprocess(check_output(ret))[0]

    @_require_token
    def GetPatientFull(self, username, patient):
        """
        :param username:
        :param patient:
        :return:
        """
        ret = yield from self.post('/json/MagicJson',
                                   data=self._build_message('GetPatientFull',
                                                            user=username, patient=patient))
        return self.postprocess(check_output(ret))

    @_require_token
    def GetEncounter(self, username, patient):
        """
        :param username:
        :param patient:
        :return:
        """
        ret = yield from self.post('/json/MagicJson',
                                   data=self._build_message('GetEncounter',
                                                            user=username, patient=patient))
        return self.postprocess(check_output(ret))

    @_require_token
    def GetProviders(self):
        """
        :return:
        """
        ret = yield from self.post('/json/MagicJson',
                                   data=self._build_message('GetProviders'))
        return self.postprocess(check_output(ret))

    @hour_cache.cache_lookup('GetProvider', lookup_on_none=True,
                             key_function=memory_cache.allargs)
    @_require_token
    def GetProvider(self, username, searchname=None, searchid=None):
        """ returns provider information from either username or userid
        :param username: the allscripts user on whose behave we are querying
        :param searchname: the username to search for
        :param searchid: the userid to search for
        """
        ret = yield from self.post('/json/MagicJson',
                                   data=self._build_message('GetProvider',
                                                            searchid or '',
                                                            searchname or '',
                                                            user=username))
        return self.postprocess(check_output(ret))

    @hour_cache.cache_lookup('GetUserID', lookup_on_none=True,
                             key_function=memory_cache.allargs)
    @_require_token
    def GetUserID(self, username: str):
        """ Returns the UserID (Internal clientEMR Integer) for the specified username.
        :param username:
        :return:
        """
        ret = yield from self.post('/json/MagicJson',
                                   data=self._build_message('GetUserID',
                                                            user=username))
        return self.postprocess(ret)

    @_require_token
    def GetDocuments(self, username: str, patient: str,
                     startdate: {str, 'date', 'datetime'}, enddate: {str, 'date', 'datetime'},
                     documentid: str=None, documenttype: str=None):
        base = """<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><Magic xmlns="http://www.allscripts.com/Unity"><Action>GetDocuments</Action><UserID>%s</UserID><Appname>%s</Appname><PatientID>%s</PatientID><Token>%s</Token><Parameter1>%s</Parameter1><Parameter2>%s</Parameter2><Parameter3/><Parameter4/><Parameter5/><Parameter6/><data/></Magic></s:Body></s:Envelope>"""
        message = base % (username, self.appname, patient, self.unitytoken,
                          isoformat(startdate), isoformat(enddate))
        ret = yield from self.post('/Unityservice',
                                   data=message, rawdata=True,
                                   headers={
                                       'Content-Type': 'text/xml',
                                       'SOAPAction': '"http://www.allscripts.com/Unity/IUnityService/Magic"'
                                   })
        try:
            root = ETree.fromstring(ret)[0][0][0][1]
            if len(root):
                return [{elem.tag: elem.text for elem in row} for row in root[0]]
            else:
                return []

        except ETree.ParseError as e:
            raise AllscriptsError('Error parsing XML ' + e)

    @_require_token
    def SaveTask(self, username: str, patient: str,
                 msg_subject: str=None, note_format: str="", binary_data: bytes=None,
                 document_id: str="", message_data: str=None, task_type: str=TASK_TYPE.SENDCHART, targetuser: str=None):
        """
        Creates a task/message.
        :param username:
        :param patient: Allscripts Internal Patient ID. Supply PatientID when you want to attach the messsage to a specific patient.
        :param document_id: Not used
        :param msg_subject: Subject of the Message.
        :param message_data: Data that will populate the body of the message
        :param note_format: Not used
        :param binary_data: Define note data if creating a note.
        :param task_type: The type of message to create. Value must be TASK_TYPE.SENDCHART.value for Maven's uses
        :param targetuser: Recipient USERNAME of the message.
        :return:
        """

        if isinstance(message_data, list):
            msg_data = "\n".join(message_data)
            message_data = msg_data

        if targetuser and isinstance(task_type, TASK_TYPE) and message_data and msg_subject:
            ret = yield from self.post('/json/MagicJson',
                                       data=self._build_message('SaveTask', task_type.value, targetuser,
                                                                document_id, message_data, msg_subject,
                                                                note_format, user=username, patient=patient))

            return self.postprocess(check_output(ret))[0]

        else:
            ML.ERROR('Error saving Allscripts Task due to lack of parameters (Target User=%s, Task Type= %s, Subject=%s, Message=%s' % (targetuser, task_type, msg_subject, message_data))

    def build_subject(self, get_patient_result):

        # Extract the demographic information
        firstname = get_patient_result['Firstname']
        lastname = get_patient_result['LastName']
        birthDate = dateutil.parser.parse(get_patient_result['dateofbirth'])
        street = get_patient_result['Addressline1']
        street2 = get_patient_result['AddressLine2']
        city = get_patient_result['City']
        state = get_patient_result['State']
        zip = get_patient_result['ZipCode']
        sex = get_patient_result['gender']
        maritalStatus = get_patient_result['MaritalStatus']

        # Create Medical Record Number (MRN) FHIR Identifier
        fhir_MRN_identifier = FHIR_API.Identifier(label="MRN",
                                                  system="clientEMR",
                                                  value=get_patient_result['mrn'])

        # Create SSN FHIR Identifier
        fhir_SSN_identifier = FHIR_API.Identifier(label="NationalIdentifier",
                                                  system="clientEMR",
                                                  value=get_patient_result['ssn'])

        # Create clientEMR Internal Identifier
        fhir_EMR_identifier = FHIR_API.Identifier(system="clientEMR",
                                                  label="Internal",
                                                  value=get_patient_result['ID'])

        fhir_patient = FHIR_API.Patient(identifier=[fhir_EMR_identifier, fhir_MRN_identifier, fhir_SSN_identifier],
                                        birthDate=birthDate,
                                        name=[FHIR_API.HumanName(given=[firstname],
                                                                 family=[lastname])],
                                        gender=sex,
                                        maritalStatus=maritalStatus,
                                        address=[FHIR_API.Address(line=[street, street2],
                                                                  city=city,
                                                                  state=state,
                                                                  zip=zip)])
        return fhir_patient

    def build_conditions(self, clin_summary_result):

        clin_summary = clin_summary_result[0]
        encounter_dx = clin_summary_result[1]
        fhir_dx_section = FHIR_API.Section(title="Encounter Dx",
                                           code=FHIR_API.CodeableConcept(coding=[FHIR_API.Coding(system="http://loinc.org",
                                                                                                 code="11450-4")]))
        bad_dx_coding = False
        for problem in [detail for detail in clin_summary if detail['section'] == "problems"]:

            # Instantiate the FHIR Condition
            fhir_condition = FHIR_API.Condition()

            # Get the date the condition was asserted
            fhir_condition.dateAsserted = dateutil.parser.parse(problem['displaydate']) or None

            # Ignore Problems sent by Allscripts that are of "Unspecified Diagnosis" or do not contain an "entrycode" element
            if problem.get('entrycode', 'FREETEXT') == 'FREETEXT':
                continue
            # Create the FHIR CodeableConcept that contains the Display Name and terminology (ICD-9) coding
            else:
                code_sys = problem['entrycode'].split("|")
                if len(code_sys) != 2 and bad_dx_coding:
                    continue
                elif len(code_sys) != 2:
                    bad_dx_coding = True
                    ML.WARN("Clin_Summary Contains unparseable Coding/System(s)")
                    continue
                else:
                    code, system = code_sys

            # Figure out whether it's a Problem List/Encounter Dx, or Past Medical History
            # Parsing this string 'Promoted: Yes'
            if code in encounter_dx:
                    fhir_condition.category = "Encounter"
            elif len(problem['detail']) > 0:
                if problem['detail'].replace(" ", "").split(":")[1] == "Yes":
                    fhir_condition.category = "Problem List"
                else:
                    fhir_condition.category = "History"
            else:
                fhir_condition.category = "History"

            if system in ["ICD-9", "ICD9"]:
                fhir_condition.code = FHIR_API.CodeableConcept(coding=[FHIR_API.Coding(system="ICD-9",
                                                                                       code=code,
                                                                                       display=problem['description'])])
            else:
                fhir_condition.code = FHIR_API.CodeableConcept(coding=[FHIR_API.Coding(display=problem['description'])])
                logger.debug("Diagnosis Terminology (ICD-9/10, SNOMED CT) not provided for %s" % problem)

            fhir_dx_section.content.append(fhir_condition)

        return fhir_dx_section

    def build_partial_practitioner(self, provider_result):

        # Extract the demographic information
        firstname = provider_result['FirstName']
        lastname = provider_result['LastName']

        specialty = provider_result['PrimSpecialty']
        profession = provider_result['Profession']

        # Extract User State (active vs inactive)
        if provider_result['ProviderInactive'] == "N":
            ehr_user_state = USER_STATE.ACTIVE.value
        else:
            ehr_user_state = USER_STATE.DISABLED.value

        # Create clientEMR Internal Identifier
        fhir_identifiers = [FHIR_API.Identifier(system="clientEMR",
                                                label="Internal",
                                                value=provider_result['EntryCode']),
                            FHIR_API.Identifier(system="clientEMR",
                                                label="Username",
                                                value=provider_result['UserName'].upper())]

        # Instantiate and build the FHIR Practitioner from the data
        fhir_practitioner = FHIR_API.Practitioner(identifier=fhir_identifiers,
                                                  name=FHIR_API.HumanName(given=[firstname],
                                                                          family=[lastname]),
                                                  specialty=[specialty],
                                                  ehr_state=ehr_user_state,
                                                  role=[profession])
        return fhir_practitioner

    def build_full_practitioner(self, get_provider_result):

        # Extract the demographic information
        firstname = get_provider_result['FirstName']
        lastname = get_provider_result['LastName']
        suffix = get_provider_result['SuffixName']
        specialty = get_provider_result['Specialty']
        street1 = get_provider_result['AddressLine1'].strip()
        street2 = get_provider_result['AddressLine2']
        city = get_provider_result['City']
        state = get_provider_result['State'].strip()
        zipcode = get_provider_result['ZipCode']

        contactInfo = [FHIR_API.Contact(system="Phone",
                                        value=get_provider_result['Phone'].strip()),
                       FHIR_API.Contact(system="Fax",
                                        value=get_provider_result['Fax'].strip())]

        # Create clientEMR Internal Identifier
        fhir_identifiers = [FHIR_API.Identifier(system="clientEMR",
                                                label="Internal",
                                                value=get_provider_result['EntryCode']),
                            FHIR_API.Identifier(system="clientEMR",
                                                label="NPI",
                                                value=get_provider_result['NPI'])]

        # Instantiate and build the FHIR Practitioner from the data
        fhir_practitioner = FHIR_API.Practitioner(identifier=fhir_identifiers,
                                                  name=FHIR_API.HumanName(given=[firstname],
                                                                          family=[lastname],
                                                                          suffix=[suffix]),
                                                  specialty=[specialty],
                                                  telecom=contactInfo,
                                                  address=[FHIR_API.Address(line=[street1, street2],
                                                                            city=city,
                                                                            state=state,
                                                                            zip=zipcode)])
        return fhir_practitioner


if __name__ == '__main__':
    MavenConfig['allscripts_old_demo'] = {
        http.CONFIG_BASEURL: 'http://aws-eehr-11.4.1.unitysandbox.com/Unity/UnityService.svc',
        http.CONFIG_OTHERHEADERS: {
            'Content-Type': 'application/json'
        },
        CONFIG_PARAMS.EHR_API_APPNAME.value: 'web20',
        CONFIG_PARAMS.EHR_API_SVC_USER.value: 'webtwozero',
        CONFIG_PARAMS.EHR_API_PASSWORD.value: 'www!web20!',
    }

    config = {
        # http.CONFIG_BASEURL: 'http://pro14ga.unitysandbox.com/Unity/UnityService.svc',
        # CONFIG_PARAMS.EHR_API_BASE_URL.value: 'https://srt-unity-pro2.allscripts.com/unity_adppro13SSL/unityservice.svc',
        #        CONFIG_PARAMS.EHR_API_BASE_URL.value: 'http://192.237.182.238/Unity/UnityService.svc',
        # CONFIG_PARAMS.EHR_API_BASE_URL.value: 'https://cua-ascriptsuai.gcu-md.local:10443/Unity/UnityService.svc',
        CONFIG_PARAMS.EHR_API_BASE_URL.value: 'https://dev-sqlemr.gcu-md.local:10443/Unity/UnityService.svc',
        # CONFIG_PARAMS.EHR_API_BASE_URL.value: 'http://127.0.0.1/Unity/UnityService.svc',
        # http.CONFIG_BASEURL: 'http://doesnotexist.somejunk.cs.umd.edu/Unity/UnityService.svc',
        http.CONFIG_OTHERHEADERS: {
            'Content-Type': 'application/json'
        },
        CONFIG_PARAMS.EHR_API_APPNAME.value: 'MavenMedical.MavenPathways.ProdApp',
        CONFIG_PARAMS.EHR_API_SVC_USER.value: 'MAV3nPAthWaYsPR0d',
        CONFIG_PARAMS.EHR_API_PASSWORD.value: 'm4VeNpAtHWaYz!3ji',
        # CONFIG_PARAMS.EHR_API_APPNAME.value: 'MavenPathways.TestApp',
        # CONFIG_PARAMS.EHR_API_SVC_USER.value: 'MavenPathways',
        # CONFIG_PARAMS.EHR_API_PASSWORD.value: 'MavenPathways123!!',
    }

    import traceback

    def wrapexn(coro):
        try:
            print(loop.run_until_complete(coro))

        except:
            traceback.print_exc()

    api = allscripts_api(config)
    loop = asyncio.get_event_loop()
    # Ehr_username = 'MAVEN'
    Ehr_username = 'CliffHux'
    # break
    # wrapexn(api.GetProvider(Ehr_username, searchid='10041'))
    if input('GetServerInfo (y/n)? ') == 'y':
        wrapexn(api.GetServerInfo())
    import sys
    sys.exit(0)
    patient = input('Enter a Patient ID to display (e.g., 22): ')
    if not patient:
        patient = '22'
    if input('SaveTask (y/n)? ') == 'y':
        wrapexn(api.SaveTask(username=Ehr_username, patient=patient,
                             msg_subject="Test Message Subject", message_data="This is the text of the message",
                             targetuser="cliffhux"))
    if input('GetDocuments (y/n)? ') == 'y':
        from datetime import date, timedelta
        wrapexn(api.GetDocuments(Ehr_username, patient, date.today() - timedelta(days=1),
                                 date.today()))
    if input('GetPatient (y/n)? ') == 'y':
        wrapexn(api.GetPatient(Ehr_username, patient))
    if input('GetLastLogs (y/n)? ') == 'y':
        wrapexn(api.GetLastLogs(Ehr_username))
    if input('GetChangedPatients (y/n)? ') == 'y':
        wrapexn(api.GetChangedPatients(Ehr_username,
                                       "2014-08-04T12:00:00"))
    if input('GetScheduleChanged (y/n)? ') == 'y':
        wrapexn(api.GetSchedule(Ehr_username,
                                "2014-08-06"))
    if input('GetProcedures (y/n)? ') == 'y':
        gp = api.GetProcedures(Ehr_username, patient,
                               completionstatuses=[COMPLETION_STATUSES.Ordered])
        wrapexn(gp)
    if input('GetClinicalSummary (y/n)? ') == 'y':
        wrapexn(api.GetClinicalSummary(Ehr_username, patient,
                                       CLINICAL_SUMMARY.All))
    if input('GetPatientSections (y/n)? ') == 'y':
        wrapexn(api.GetPatientSections(Ehr_username, patient, 1))
    if input('GetPatientByMRN (y/n)? ') == 'y':
        wrapexn(api.GetPatientByMRN(Ehr_username, patient))
    if input('GetPatientCDA (y/n)? ') == 'y':
        wrapexn(api.GetPatientCDA(Ehr_username, patient))
    if input('GetPatientFull (y/n)? ') == 'y':
        wrapexn(api.GetPatientFull(Ehr_username, patient))
    if input('GetEncounter (y/n)? ') == 'y':
        wrapexn(api.GetEncounter(Ehr_username, patient))
    if input('GetProviders (y/n)? ') == 'y':
        wrapexn(api.GetProviders())
    if input('GetProvider (y/n)? ') == 'y':
        wrapexn(api.GetProvider(Ehr_username, searchname='terry'))
    if input('GetUserID (y/n)? ') == 'y':
        wrapexn(api.GetUserID(Ehr_username))
