
create table terminology.DrugClass
(
   rxaui varchar(20) primary key
   ,rxcui varchar(20)
   ,str varchar(4000)
   ,snomedid numeric(18,0)
);
create index ixDrugClassaui on terminology.drugClass (rxaui);
create index ixDrugClasscui on terminology.drugClass (rxcui);
create index ixDrugClasssnomed on terminology.drugClass (snomedid);


insert into terminology.drugclass (
	select distinct a.rxaui,a.rxcui,b.str from rxnsat a 
	inner join rxnconso b on a.rxaui=b.rxaui
	where (a.atn='ATC_LEVEL' and a.sab='ATC' and a.atv='4')
);


update drugclass dc set snomedid= (select min(cast(scui as numeric)) from rxnconso a where a.rxcui=dc.rxcui and a.sab ='SNOMEDCT_US' and tty='PT');

create table terminology.drugClassAncestry
(
   classAui varchar(20)
   ,inClassAui varchar(20)
   ,brandname varchar(200)
   ,routename varchar(200)
   ,ndc varchar(200)
   ,primary key (classaui,inclassaui)
);
create index ixDrugClassAncestryPK on terminology.drugClassAncestry (classaui,inclassaui);
create index ixDrugClassAncestryReverse on terminology.drugClassAncestry (inclassaui,classaui);


insert into terminology.drugclassancestry(
select distinct  dc.rxaui ,ndc.rxaui ,max(coalesce(brand.str,member.str||' (generic)')) ,max(route.groupname),max(ndc.atv)
from drugclass dc
inner join rxnrel a on a.rxaui1=dc.rxaui and a.rela='member_of'
inner join rxnconso member on member.rxaui=a.rxaui2 
inner join rxnrel rel2 on rel2.rxcui1=member.rxcui and rel2.rela='has_ingredient'
inner join rxnconso drug on drug.rxcui=rel2.rxcui2 and drug.sab='RXNORM' and drug.tty!='TMSY'
inner join rxnrel rel3 on rel3.rxcui1=drug.rxcui and rel3.rela in ('consists_of','isa')
inner join rxnconso soldas on soldas.rxcui=rel3.rxcui2 and soldas.sab='RXNORM' and soldas.tty='SY'
--check if there's an NDC for the thing
inner join rxnsat ndc on ndc.rxcui=soldas.rxcui and ndc.atn='NDC'  and ndc.sab='RXNORM' 
inner join rxnrel routerel on routerel.rxcui1=ndc.rxcui and routerel.rela='dose_form_of'
inner join doseformgroups route on routerel.rxcui2=route.rxcui
left outer join rxnrel brel on brel.rxcui1=ndc.rxcui and brel.rela='ingredient_of'
left outer join rxnconso brand on brel.rxcui2=brand.rxcui and brand.tty='BN'
group by dc.rxaui ,ndc.rxaui 
);

create or replace function getClassNameFromNDC(ndc varchar(20))
  RETURNS varchar(200) AS
$BODY$
Declare rtn varchar(200);
begin
        select distinct c.str into rtn from rxnsat a
	inner join drugClassAncestry b on a.rxaui=b.inclassaui
	inner join drugclass c on b.classaui=c.rxaui
	 where a.atn='NDC' and a.atv=ndc and a.sab='RXNORM' ;
	 
        return rtn;
end;
$BODY$
  LANGUAGE plpgsql;

create or replace function getClassSnomedFromNDC(ndc varchar(20))
  RETURNS numeric AS
$BODY$
Declare rtn numeric;
begin
        select distinct c.SnomedId into rtn from rxnsat a
	inner join drugClassAncestry b on a.rxaui=b.inclassaui
	inner join drugclass c on b.classaui=c.rxaui
	 where a.atn='NDC' and a.atv=ndc and a.sab='RXNORM' ;
	 
        return rtn;
end;
$BODY$
  LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION isNdcChild(vparentconcept numeric, ndc varchar(20))
  RETURNS boolean AS
$BODY$
Declare rtn Boolean;
Declare Sno numeric;
begin
        select getClassSnomedFromNDC(ndc) into sno;
        return isSnomedChild(vparentconcept,sno);
end;
$BODY$
  LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION terminology.isRxAUIchild(vparentconcept numeric, vrxaui character varying)
  RETURNS boolean AS
$BODY$
Declare rtn Boolean;
Declare Sno numeric;
begin
        select b.snomedid into sno
		from drugclassancestry a 
		inner join drugclass b on a.classaui=b.rxaui
		where inclassaui=vrxaui and snomedid is not null;
        return isSnomedChild(vparentconcept,sno);
end;
$BODY$
  LANGUAGE plpgsql ;

/****************Do not use********************
 CREATE OR REPLACE FUNCTION terminology.isRxCUIchild(vparentconcept numeric, vrxCui character varying)
  RETURNS boolean AS
$BODY$
Declare rtn Boolean;
Declare Sno numeric;
begin
	rtn=false;
        for sno in select distinct b.snomedid 
		from rxnsat sat 
		inner join drugclassancestry a on a.inclassaui=sat.rxaui
		inner join drugclass b on a.classaui=b.rxaui
		where sat.rxcui=vrxcui
	loop 
	   if isSnomedChild(vparentconcept,sno) then rtn=true;
	   end if;
	end loop;
        return rtn;
end;
$BODY$
  LANGUAGE plpgsql ;
******************************************************/

