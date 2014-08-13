import utils.web_client.http_client as http
import asyncio
import json
from xml.etree import ElementTree as ETree
from enum import Enum
from functools import wraps, lru_cache
from maven_config import MavenConfig
from maven_logging import WARN

ALLSCRIPTS_NUM_PARAMETERS = 6

CONFIG_APPNAME = 'appname'
CONFIG_APPUSERNAME = 'appusername'
CONFIG_APPPASSWORD = 'apppassword'


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


class UnauthorizedUser(Exception):
    pass


class AllscriptsError(Exception):

    def __init__(self, string):
        WARN("Exception invalid response from allscripts: %s", str(string))
        Exception(self, "Exception invalid response from allscripts: %s", str(string))


def check_output(jobj, empty_ok=False):
    exc = None
    if not jobj:
        raise AllscriptsError("Query returned empty string")
    try:
        obj = json.loads(jobj)
        if "Error" in obj[0]:
            exc = AllscriptsError(obj[0]["Error"])
        elif (not empty_ok) and len(list(obj[0].values())[0]) == 0:
            exc = AllscriptsError("Query returned empty list")
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


@lru_cache()
class allscripts_api(http.http_api):

    def __init__(self, configname: str):
        """ initialize this adapter for the allscripts professional API
        :params configname: the name of the configuration section in the MavenConfig map
        it's required parameters are:
          CONFIG_BASEURL, CONFIG_APPNAME, CONFIG_APPUSERNAME, CONFIG_APPPASSWORD
        it's optional parameter is CONFIG_OTHERHEADERS
        """
        http.http_api.__init__(self, configname)
        self.postprocess = (lambda x: list(x[0].values())[0])
        self.appname = self.config[CONFIG_APPNAME]
        self.appusername = self.config[CONFIG_APPUSERNAME]
        self.apppassword = self.config[CONFIG_APPPASSWORD]
        self.unitytoken = None

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

    def _require_token(func: 'function') -> 'function':
        """ decorator for functions which require a security token before executing
        """
        co_func = asyncio.coroutine(func)

        def worker(self, *args, **kwargs):
            if not self.unitytoken:
                f = asyncio.Future()
                self.unitytoken = f
                req = yield from self.post('/json/GetToken',
                                           Username=self.appusername, Password=self.apppassword)
                f.set_result(req)
                self.unitytoken = req
            elif isinstance(self.unitytoken, asyncio.Future):
                yield from self.unitytoken
            ret = yield from co_func(self, *args, **kwargs)
            return ret
        return asyncio.coroutine(wraps(func)(worker))

    @_require_token
    def GetServerInfo(self):
        """ Takes no arguments and returns:
        Returns values for server time zone, server time server datetime offset,
        what type of unity system, the product version, and the start time of this
        unity installation
        """
        ret = yield from self.post('/json/MagicJson',
                                   data=self._build_message('GetServerInfo'))
        return self.postprocess(check_output(ret))[0]

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
    def _append_xml(root: ETree.Element, name: str, value: str=None):
        child = ETree.Element(name)
        if value:
            child.set('value', value)
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
        self._append_xml(XML, 'PatientID', patient)
        self._append_xml(XML, 'UserLoginName', username)
        completionXML = self._append_xml(XML, 'CompletionStatuses')
        if completionstatuses:
            for cs in completionstatuses:
                self._append_xml(completionXML, 'CompletionStatus', cs.value)
        else:
            self._append_xml(completionXML, 'CompletionStatus', COMPLETION_STATUSES.All.value)
        if rulenames:
            rulenameXML = self._append_xml(XML, 'RuleNames',
                                           'Y' if rulenameexactmatch else 'N')
            for rn in rulenames:
                self._append_xml(rulenameXML, 'RuleName', rn)
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
    def GetProviders(self, username):
        """
        :param username:
        :return:
        """
        ret = yield from self.post('/json/MagicJson',
                                   data=self._build_message('GetProviders',
                                                            user=username))
        return self.postprocess(check_output(ret))

    @_require_token
    def GetProvider(self, username):
        """ Searches for and returns provider information based on either Provider ID or Provider user name.

        """
        ret = yield from self.post('/json/MagicJson',
                                   data=self._build_message('GetProvider',
                                                            "68",
                                                            'terry',
                                                            user=username))
        return self.postprocess(check_output(ret))

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
            root = ETree.fromstring(ret)[0][0][0][1][0]  # Magic contains lots of fluff
            return [{elem.tag: elem.text for elem in row} for row in root]
        except ETree.ParseError as e:
            raise AllscriptsError('Error parsing XML ' + e)


if __name__ == '__main__':
    MavenConfig['allscripts_old_demo'] = {
        http.CONFIG_BASEURL: 'http://aws-eehr-11.4.1.unitysandbox.com/Unity/UnityService.svc',
        http.CONFIG_OTHERHEADERS: {
            'Content-Type': 'application/json'
        },
        CONFIG_APPNAME: 'web20',
        CONFIG_APPUSERNAME: 'webtwozero',
        CONFIG_APPPASSWORD: 'www!web20!',
    }

    MavenConfig['allscripts_demo'] = {
        http.CONFIG_BASEURL: 'http://pro14ga.unitysandbox.com/Unity/UnityService.svc',
        http.CONFIG_OTHERHEADERS: {
            'Content-Type': 'application/json'
        },
        CONFIG_APPNAME: 'MavenPathways.TestApp',
        CONFIG_APPUSERNAME: 'MavenPathways',
        CONFIG_APPPASSWORD: 'MavenPathways123!!',
    }

    import traceback

    def wrapexn(coro):
        try:
            print(loop.run_until_complete(coro))

        except:
            traceback.print_exc()

    api = allscripts_api('allscripts_demo')
    loop = asyncio.get_event_loop()
    Ehr_username = 'CliffHux'
    # break
    patient = input('Enter a Patient ID to display (e.g., 22): ')
    if not patient:
        patient = '22'
    if input('GetServerInfo (y/n)? ') == 'y':
        wrapexn(api.GetServerInfo())
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
                                "2014-08-05"))
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
        wrapexn(api.GetProviders(Ehr_username))
    if input('GetProvider (y/n)? ') == 'y':
        wrapexn(api.GetProvider(Ehr_username))
    if input('GetUserID (y/n)? ') == 'y':
        wrapexn(api.GetUserID(Ehr_username))
    if input('GetDocuments (y/n)? '):
        print(loop.run_until_complete(api.GetDocuments(Ehr_username, patient)))
