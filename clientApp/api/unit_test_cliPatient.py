import cliConfig
import cliPatient

__author__ = 'dave'

config=cliConfig.CliConfig()

patstring="<GetPatientDemographicsResult><Address><City>Madison</City><Country>United States</Country><County>Dane</County><State>Wisconsin</State><Street xmlns:a=\"http://schemas.microsoft.com/2003/10/Serialization/Arrays\"><a:string>134 Memory Ln.</a:string></Street><Zip>53714</Zip></Address><DateOfBirth>1956-06-04T00:00:00</DateOfBirth><Email></Email><Gender>Male</Gender><MaritalStatus>Married</MaritalStatus><Name><FirstName>Adam</FirstName><LastName>Aardvark</LastName><MaidenName></MaidenName><MiddleName></MiddleName><Nickname></Nickname><Suffix></Suffix><Title></Title></Name><NationalIdentifier>999-42-0089</NationalIdentifier><Phones><Phone><Number>999-555-0088</Number><Type>Home Phone</Type></Phone></Phones><Race></Race><Religion></Religion></GetPatientDemographicsResult>"
probstring="<GetActiveProblemsResult><ErrorCode></ErrorCode><Problems><Problem><Comment>Severe Asthma</Comment><Description></Description><DiagnosisIDs><IDType><ID>120910</ID><Type>Internal</Type></IDType></DiagnosisIDs><EntryPerson><ID>8941</ID><Name>SEWAK, MIHIR S</Name></EntryPerson><IsChronic>false</IsChronic><IsHospitalProblem>false</IsHospitalProblem><IsPresentOnAdmission></IsPresentOnAdmission><IsPrincipal>false</IsPrincipal><IsVisibleToPatient>true</IsVisibleToPatient><NotedDate>2011-01-01T00:00:00</NotedDate><Priority>1</Priority><ProblemClass>1</ProblemClass><ProblemIDs><IDType><ID>2610049</ID><Type>Internal</Type></IDType></ProblemIDs></Problem></Problems></GetActiveProblemsResult>"
encstring="<Contact><DateTime>2009-04-20T07:54:48</DateTime><DepartmentAbbreviation>WI HBN ED</DepartmentAbbreviation><DepartmentIDs><IDType><ID>1231</ID><Type>Internal</Type></IDType></DepartmentIDs><DepartmentName>WI HARBOR BLUFF ED</DepartmentName><IDs><IDType><ID>257549</ID><Type>Contact Serial Number</Type></IDType><IDType><ID>15844</ID><Type>External Visit ID</Type></IDType></IDs><PatientClass>E</PatientClass><Type>Hospital Encounter</Type></Contact>"
ordstring="<Orders>    <Order>          <ProcedureCode>85025</ProcedureCode>          <CodeType>CPT</CodeType>          <ExpectedDate>2011-01-01T00:00:00</ExpectedDate>          <ExpiredDate></ExpiredDate>          <Name>CBC with Automated Diff</Name>          <Type>Lab</Type>   </Order></Orders>"

pat = cliPatient.cliPatient(patstring, probstring, encstring, ordstring, config)
print pat.gender
print pat.problemList[0].dateNoted
print pat.problemList[0].diagnosis.snomedConcepts
print pat.birthMonth
print pat.Encounter.depName
print pat.Encounter.orders[0].procName
