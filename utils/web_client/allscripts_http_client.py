import utils.web_client.http_client as http
import asyncio
import json
from xml.etree import ElementTree as ETree
from enum import Enum
from functools import wraps

ALLSCRIPTS_NUM_PARAMETERS = 6
Ehr_username = 'terry'


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


# BASEURL = 'http://aws-eehr-11.4.1.unitysandbox.com/Unity/UnityService.svc/json'
BASEURL = 'http://pro14ga.unitysandbox.com/Unity/UnityService.svc/json'
# APPNAME = 'web20'
APPNAME = 'MavenPathways.TestApp'
# APPUSERNAME = 'webtwozero'
APPUSERNAME = 'MavenPathways'
# APPPASSWORD = 'www!web20!'
APPPASSWORD = 'MavenPathways123!!'


class UnauthorizedUser(Exception):
    pass


class allscripts_api(http.http_api):

    def __init__(self,
                 baseurl=BASEURL,
                 appname=APPNAME,
                 appuser=APPUSERNAME,
                 apppassword=APPPASSWORD):

        http.http_api.__init__(self, baseurl,
                               {'Content-Type': 'application/json'})
        self.postprocess = (lambda x: list(json.loads(x)[0].values())[0])
        self.appname = appname
        self.appusername = APPUSERNAME
        self.apppassword = APPPASSWORD
        self.unitytoken = None

    def _build_message(self, action, *args, user=None, patient=None, data='null'):
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

    def _require_token(func):
        co_func = asyncio.coroutine(func)

        def worker(self, *args, **kwargs):
            if not self.unitytoken:
                req = yield from self.post('/GetToken',
                                           Username=self.appusername, Password=self.apppassword)

                self.unitytoken = req
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
        ret = yield from self.post('/MagicJson',
                                   data=self._build_message('GetServerInfo'))
        return self.postprocess(ret)[0]

    @_require_token
    def GetPatient(self, username, patient):
        """ Gets (demographic and contact mostly) information about a patient
        :param user: the allscripts EHR user ID
        :param patient: the allscripts internal patient ID (from GetPatientByMRN,
                        SearchPatients, or other)
        Returns phone/address/email/employer/ssn/etc (all not needed)
        also, name/dob/gender (needed) and much more
        """
        ret = yield from self.post('/MagicJson',
                                   data=self._build_message('GetPatient', user=username,
                                                            patient=patient))
        return self.postprocess(ret)[0]

    @_require_token
    def GetChangedPatients(self, username, since):
        """ Gets a list of patientIDs for patients whose information has changed recently
        :param username: the allscripts ehr username
        :param since: a timestamp - only get patients who changed after this time
                      can be a date/datetime object, or a string "YYYY-MM-DDTHH:MM:SS"
        returns a list of patient ids
        """
        if type(since) is not str:
            since = since.isoformat()
        ret = yield from self.post('/MagicJson',
                                   data=self._build_message('GetChangedPatients', since,
                                                            user=username))
        return [x['patientid'] for x in self.postprocess(ret)]

    @_require_token
    def GetSchedule(self, username, startdate, changedsince=None, soughtuser=None):
        """ Gets a list of scheduled appointments for a provider.
        Each element in the list includes (among others):
        Status (i.e. pending), patiendID, Duration, Patient (full name), TimeIn, ProviderID,
        :param username: the user whose schedule to check
        :param startdate: appears to not really be a start date, but the date to lookup
                          can be a date/datetime object, or a string as "YYYY-MM-DDTHH:MM:SS"
        :param changedsince: a timestamp filter like in GetChangedPatients
        :param soughtuser: get the schedule for a different allscripts user (provider)
        """
        if type(startdate) is not str:
            startdate = startdate.isoformat()
        if changedsince and type(changedsince) is not str:
            changedsince = changedsince.isoformat()
        message = self._build_message('GetSchedule',
                                      startdate,
                                      changedsince or '',
                                      'N',  # includepicture
                                      soughtuser or '',
                                      user=username)

        ret = yield from self.post('/MagicJson', data=message)
        print(ret)
        return self.postprocess(ret)

    @staticmethod
    def _append_xml(root, name, value=None):
        child = ETree.Element(name)
        if value:
            child.set('value', value)
        root.append(child)
        return child

    @_require_token
    def GetProcedures(self, username, patient, completionstatuses=None,
                      rulenames=None, rulenameexactmatch=False):
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
        ret = yield from self.post('/MagicJson', data=message)
        # allscripts returns this as a json, containing an xml string
        # step 1, check if the string is empty
        ret = self.postprocess(ret)
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
    def GetClinicalSummary(self, username, patient, sections=None):
        """ Gets lots of clinical data about a patient
        :param username: the allscripts user
        :param patient: the patient to search for
        :param sections: a filter, taken from the CLINICAL_SUMMARY enum to filter results
                         the default None does not filter
        """
        ret = yield from self.post('/MagicJson',
                                   data=self._build_message('GetClinicalSummary',
                                                            sections.value if sections else 'list',
                                                            user=username,
                                                            patient=patient))
        return self.postprocess(ret)

    @_require_token
    def GetPatientSections(self, username, patient, months):
        """
        """
        ret = yield from self.post('/MagicJson',
                                   data=self._build_message('GetPatientSections',
                                                            str(months),
                                                            user=username, patient=patient))
        return self.postprocess(ret)

if __name__ == '__main__':
    api = allscripts_api()
    loop = asyncio.get_event_loop()
    patient = input('Enter a Patient ID to display (e.g., 22): ')
    if not patient:
        patient = '22'
    if input('GetServerInfo (y/n)? ') == 'y':
        print(loop.run_until_complete(api.GetServerInfo()))
    if input('GetPatients (y/n)? ') == 'y':
        print(loop.run_until_complete(api.GetPatient(Ehr_username, patient)))
    if input('GetChangedPatients (y/n)? ') == 'y':
        print(loop.run_until_complete(api.GetChangedPatients(Ehr_username,
                                                             "2014-08-04T12:00:00")))
    if input('GetScheduleChanged (y/n)? ') == 'y':
        print(loop.run_until_complete(api.GetSchedule(Ehr_username,
                                                      "2014-08-05")))
    if input('GetProcedures (y/n)? ') == 'y':
        print(loop.run_until_complete(api.GetProcedures(Ehr_username, patient,
                                                        completionstatuses=[COMPLETION_STATUSES.Ordered])))
    if input('GetClinicalSummary (y/n)? ') == 'y':
        print(loop.run_until_complete(api.GetClinicalSummary(Ehr_username, patient,
                                                             CLINICAL_SUMMARY.Medications)))
    if input('GetPatientSections (y/n)? ') == 'y':
        print(loop.run_until_complete(api.GetPatientSections(Ehr_username, patient, 1)))
