OrdTrig(ordid,job,del)
    n ip,hostname,program,patid,patname,problist,ordstatus,host,port,tmp,ptid
    n ordstring,patstring,sendstring,prov,dt,encid
    d IXORD(ordid) ;first index the order
    ;w "Starting",!
    s host="localhost",port="9090"
    s tmp=^XUSEC(0,^xMAVEN(job),0)
    s ip=$p(tmp,"^",11)
    i 1
    q:$l(ip)<7 ;close out if there is no ip address to deal with
    s hostname=$p(tmp,"^",10),program=$p(tmp,"^",12)
    s ordstring=$$ALLORD(ordid)
    s ptid=$o(^xMAVEN("ORIX","OPPD",ordid,""))
    w ordstring
    ;;;;;;;;;;;;;;;;;;The next lines are only a placeholder for the encounter id
    s prov=$o(^xMAVEN("ORIX","OPPD",ordid,ptid,"")),dt=$o(^xMAVEN("ORIX","OPPD",ordid,ptid,prov,""))
    s encid=ptid_"|"_prov_"|"_dt
    ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
    d:del CleanDeleted(ordid,ptid,prov,dt)
    s patstring=$$PAT(ptid)
    s sendstring="<Encounter><EncID>"_encid_"</EncID>"_patstring_" "_ordstring_" "_$$PROBS(ptid)_"</Encounter>"
    ;w patstring,!
    ;w ordstring,!
    ;w "Sendstring: "_sendstring
    ;w sendstring
    d SocketMsg(sendstring,program,port)
    q
ORD(ordid)
    n rtn,code,codetyp,dt,nm,ordtype
    n ordble,ptid
    s ptid=$p($$GET1^DIQ(100,ordid,.02,"I"),";",1)
    q:ptid="" ""
    s ordble=^OR(100,ordid,4.5,1,1)
    s code=$$GET1^DIQ(101.43,ordble,3),codetyp=$$GET1^DIQ(101.43,ordble,4)
    s dt=$$GET1^DIQ(100,ordid,4),nm=$$GET1^DIQ(101.43,ordble,.01)
    s ordtype="PROC"
    s:codetyp["CPT" ordtype="PROC"
    s rtn="<Order><ProcedureCode>{CODE}</ProcedureCode><CodeType>{CodeType}</CodeType><ExpectedDate>{EXPECTDATE}</ExpectedDate><OrderingDate>{EXPECTDATE}</OrderingDate><ExpiredDate></ExpiredDate><Name>{NAME}</Name><Type>{ORDTYPE}</Type></Order>"
    s rtn=$$replace(rtn,"{CODE}",$$encode(code))
    s rtn=$$replace(rtn,"{CodeType}",$$encode(codetyp))
	;note, currently the ordering date and the expected date are the same (ordering date)
    s rtn=$$replace(rtn,"{EXPECTDATE}",dt)
    s rtn=$$replace(rtn,"{NAME}",$$encode(nm))
    s rtn=$$replace(rtn,"{ORDTYPE}",$$encode(ordtype))
    q rtn
ALLORD(ordid)
    ;assumes we don't have a "visit" record to tie to
    ;simply considers the encounter all orders for the patient/provider/day
    n curid,ptid,prov,dt,rtn
    s curid="",rtn=""
    s ptid=$o(^xMAVEN("ORIX","OPPD",ordid,"")),prov=$o(^xMAVEN("ORIX","OPPD",ordid,ptid,"")),dt=$o(^xMAVEN("ORIX","OPPD",ordid,ptid,prov,""))
    ;loop over the orders in the same pat/prov/day package
    f  s curid=$o(^xMAVEN("ORIX","PPD",ptid,prov,dt,curid)) q:curid=""  d
    . q:$$GET1^DIQ(100,curid,5)["DISCON" ;quit if it's been discontinued
    . s rtn=rtn_$$ORD(curid) ;add the order string to the return package
    q "<Orders>"_rtn_"</Orders>"
OrdKillTrig(ordid,job)
    h .5
    d OrdTrig(ordid,job,1)
    q
CleanDeleted(ordid,ptid,prov,dt)
        k ^xMAVEN("ORIX","OPPD",ordid)
        k ^xMAVEN("ORIX","PPD",ptid,prov,dt,ordid)
        q
IXORD(ordid)
    n ptid,prov,dt
    ;index the order so we can come back to it later with a prov/pat/day combo
    s ptid=$p($$GET1^DIQ(100,ordid,.02,"I"),";",1)
    q:ptid=""
    s prov=$$GET1^DIQ(100,ordid,1,"I")
    s dt=$$GET1^DIQ(100,ordid,4,"I")\1 ;get the date-only portion of the entry date
    s ^xMAVEN("ORIX","PPD",ptid,prov,dt,ordid)=""
    s ^xMAVEN("ORIX","OPPD",ordid,ptid,prov,dt)=""
    q
replace(a,str1,str2) ;
    n fnd
    s fnd=0 f  s fnd=$f(a,str1,fnd) q:'fnd  s $e(a,fnd-$l(str1),fnd-1)=str2
    q a
encode(str)
        q $$replace($$replace($$replace($$replace($$replace(str,"&","&amp;"),"<","&lt;"),">","&gt;"),"""","&qot;"),"'","&apos;")
SocketMsg(msg,host,port) ;;;
    n %ZNTimeS
    s %ZNTimeS=5 ;timeout seconds
    s %ZNDev="SCK$"_$J
    o %ZNDev:(connect=host_":"_port_":TCP":delim=$c(13):attach="client"):%ZNTimeS:"SOCKET"
    u %ZNDev
    w msg,!
    CLOSE %ZNDev
    q
PAT(ptid)
    n street,city,state,zip,county,country,dob,sex,marital,fname,lname,nm
    n ssn,resphone,cellphone,workphone,phones,primrace
    s phones="",primrace=""
    s street=$$GET1^DIQ(2,ptid,.111),city=$$GET1^DIQ(2,ptid,.114),state=$$GET1^DIQ(2,ptid,.115),zip=$$GET1^DIQ(2,ptid,.116)
    s county=$$GET1^DIQ(2,ptid,.117),country="",dob=$$GET1^DIQ(2,ptid,.03),sex=$$GET1^DIQ(2,ptid,.02)
    s marital=$$GET1^DIQ(2,ptid,.05),nm=$$GET1^DIQ(2,ptid,.01),lname=$p(nm,",",1),fname=$p(nm,",",2)
    s ssn=$$GET1^DIQ(2,ptid,.09),cellphone=$$GET1^DIQ(2,ptid,.134),resphone=$$GET1^DIQ(2,ptid,.132),workphone=$$GET1^DIQ(2,ptid,.132)
    s:cellphone phones=phones_"<Phone><Number>"_cellphone_"</Number><Type>Cell Phone</Type></Phone>"
    s:resphone phones=phones_"<Phone><Number>"_resphone_"</Number><Type>Home Phone</Type></Phone>"
    s:workphone phones=phones_"<Phone><Number>"_workphone_"</Number><Type>Work Phone</Type></Phone>"
    s:$d(^DPT(ptid,.02,0)) primracce=$p(^DIC(10,$p(^DPT(ptid,.02,0),"^",3),0),"^",1)
    s rtn="<GetPatientDemographicsResult><PatientID>"_ptid_"</PatientID><PatientIDType>internal</PatientIDType><Address><City>{CITY}</City><Country>{COUNTRY}</Country><County>{COUNTY}</County><State>{STATE}</State><Street>{STREET}</Street><Zip>{ZIP}</Zip></Address><DateOfBirth>{DOB}</DateOfBirth><Gender>{SEX}</Gender><MaritalStatus>{MARITAL}</MaritalStatus><Name><FirstName>{FNAME}</FirstName><LastName>{LNAME}</LastName><MaidenName></MaidenName><MiddleName></MiddleName><Nickname></Nickname><Suffix></Suffix><Title></Title></Name><NationalIdentifier>{SSN}</NationalIdentifier><Phones>{PHONES}</Phones><Race>{RACE}</Race><Religion></Religion></GetPatientDemographicsResult>"
    s rtn=$$replace(rtn,"{CITY}",$$encode(city))
    s rtn=$$replace(rtn,"{COUNTRY}",$$encode(country))
    s rtn=$$replace(rtn,"{COUNTY}",$$encode(county))
    s rtn=$$replace(rtn,"{STATE}",state)
    s rtn=$$replace(rtn,"{ZIP}",zip)
    s rtn=$$replace(rtn,"{STREET}",$$encode(street))
    s rtn=$$replace(rtn,"{DOB}",dob)
    s rtn=$$replace(rtn,"{MARITAL}",marital)
    s rtn=$$replace(rtn,"{FNAME}",$$encode(fname))
    s rtn=$$replace(rtn,"{LNAME}",$$encode(lname))
    s rtn=$$replace(rtn,"{SSN}",ssn)
    s rtn=$$replace(rtn,"{PHONES}",phones)
    s rtn=$$replace(rtn,"{RACE}",$$encode(primrace))
    s rtn=$$replace(rtn,"{SEX}",sex)
    q rtn
PROBS(ptid)
    n PROBSOUT,IHSOUT,ihsid,probid,dxid,ln,DXOUT,rtn,probstring,curstring
    ; first just double check that you have the correct IHS Patient ID
    d FIND^DIC(9000001,"",.01,"Q",ptid,"","B","","","IHSOUT")
    s ihsid=IHSOUT("DILIST",2,1)
    ;now you're ready to get the patient's problem list from a lookup on the IHS index
    D FIND^DIC(9000011,"",.02,"Q",ihsid,"","AC","","","PROBSOUT")
    s probid="",ln="",probstring=""
    f  s ln=$o(PROBSOUT("DILIST",2,ln)) q:ln=""  d
    . s dxid=PROBSOUT("DILIST",1,ln),probid=PROBSOUT("DILIST",2,ln)
    . d GETS^DIQ(9000011,probid,"**","","DXOUT")
    . d GETS^DIQ(9000011,probid,"1.03","I","DXOUT") ; get the internal id of the documentation prov
    . n comment,dxcode,enterby,enterbyid,chron,notedate
    . s comment=""
    . s:$d(DXOUT(9000011.1111,"1,1,"_probid_",",.03)) comment=DXOUT(9000011.1111,"1,1,"_probid_",",.03)
    . s dxcode=$$GET1^DIQ(80,dxid,.01),enterby=DXOUT(9000011,probid_",",1.03),enterbyid=DXOUT(9000011,probid_",",1.03,"I")
    . s chron=DXOUT(9000011,probid_",",1.14)
    . s:chron="CHRONIC" chron="true"
    . s:chron="ACUTE" chron="false"
    . s notedate=DXOUT(9000011,probid_",",.13)
    . s:notedate="" notedate=DXOUT(9000011,probid_",",.08)
    . s curstring="<Problem><Comment>{COMMENT}</Comment><Description></Description><DiagnosisIDs><IDType><ID>{DXCODE}</ID><Type>ICD</Type></IDType></DiagnosisIDs><EntryPerson><ID>{PROVID}</ID><Name>{PROVNAME}</Name></EntryPerson><IsChronic>{CHRON}</IsChronic><IsHospitalProblem></IsHospitalProblem><IsPresentOnAdmission></IsPresentOnAdmission><IsPrincipal></IsPrincipal><IsVisibleToPatient>true</IsVisibleToPatient><NotedDate>{NOTEDATE}</NotedDate><Priority></Priority><ProblemClass></ProblemClass><ProblemIDs><IDType><ID>{PROBID}</ID><Type>Internal</Type></IDType></ProblemIDs></Problem>"
    . s curstring=$$replace(curstring,"{COMMENT}",$$encode(comment))
    . s curstring=$$replace(curstring,"{DXCODE}",$$encode(dxcode))
    . s curstring=$$replace(curstring,"{PROVID}",enterbyid)
    . s curstring=$$replace(curstring,"{PROVNAME}",$$encode(enterby))
    . s curstring=$$replace(curstring,"{CHRON}",chron)
    . s curstring=$$replace(curstring,"{NOTEDATE}",notedate)
    . s curstring=$$replace(curstring,"{PROBID}",probid)
    . s probstring=probstring_curstring
    . n DXOUT
    s rtn="<GetActiveProblemsResult><ErrorCode></ErrorCode><Problems>"_probstring_"</Problems></GetActiveProblemsResult>"
    q rtn

