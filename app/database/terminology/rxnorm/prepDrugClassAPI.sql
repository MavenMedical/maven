\connect maven

create table terminology.drugclass
(
   rxaui varchar(20) primary key
   ,rxcui varchar(20)
   ,str varchar(4000)
   ,snomedid numeric(18,0)
);
create index ixDrugClassaui on terminology.drugclass (rxaui);
create index ixDrugClasscui on terminology.drugclass (rxcui);
create index ixDrugClasssnomed on terminology.drugclass (snomedid);


insert into terminology.drugclass (
	select distinct a.rxaui,a.rxcui,b.str from terminology.rxnsat a 
	inner join terminology.rxnconso b on a.rxaui=b.rxaui
	where (a.atn='ATC_LEVEL' and a.sab='ATC' and a.atv='4')
);


update terminology.drugclass dc set snomedid= (select min(cast(scui as numeric)) from terminology.rxnconso a where a.rxcui=dc.rxcui and a.sab ='SNOMEDCT_US' and tty='PT');

create table terminology.doseformgroups (rxcui varchar(20) primary key, groupname varchar(200));
create index ixdoseformgrouppk on terminology.doseformgroups (rxcui);
insert into terminology.doseformgroups
(
	select rxcui,max(grp) from (
	select distinct a.rxcui,case when lower(str) like '%oral%' or lower(str) like '%extend%tab%' or lower(str) like '%pill%' or lower(str) like '%chewable%' or lower(str) like ('%tab%extend%') 
	or lower(str) like '%extend%cap%' or lower(str) like '%cap%extend%' then 'Oral' 
	when lower(str) like '%inject%' or lower(str) like '%syringe%' then 'Injection'
	when lower(str) like '%topical%' then 'Topical'
	else lower(str) end grp from terminology.rxnconso a inner join terminology.rxnrel b on a.rxcui=b.rxcui2 where tty='DF')
	a group by rxcui
);


create table terminology.drugclassancestry
(
   classAui varchar(20)
   ,inClassAui varchar(20)
   ,brandname varchar(200)
   ,routename varchar(200)
   ,ndc varchar(200)
   ,classname varchar(200)
   ,drug varchar(200)
   ,primary key (classaui,inclassaui,ndc)
);
create index ixDrugClassAncestryPK on terminology.drugclassancestry (classaui,inclassaui,ndc);
create index ixDrugClassAncestryReverse on terminology.drugclassancestry (inclassaui,classaui,ndc);
create index ixDrugClassAncestryNDC on terminology.drugclassancestry(ndc,classaui,inclassaui);

-- Table: terminology.rxsnomeds

-- DROP TABLE terminology.rxsnomeds;

CREATE TABLE terminology.rxsnomeds
(
  rxcui character varying(8),
  snomed bigint,
  term character varying(3000),
  ndc character varying(4000),
  drugname character varying(3000)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE terminology.rxsnomeds
  OWNER TO maven;

-- Index: terminology.rxsnocui

-- DROP INDEX terminology.rxsnocui;

CREATE INDEX rxsnocui
  ON terminology.rxsnomeds
  USING btree
  (rxcui);

-- Index: terminology.rxsnondc

-- DROP INDEX terminology.rxsnondc;

CREATE INDEX rxsnondc
  ON terminology.rxsnomeds
  USING btree
  (ndc);

-- Index: terminology.rxsnosno

-- DROP INDEX terminology.rxsnosno;

CREATE INDEX rxsnosno
  ON terminology.rxsnomeds
  USING btree
  (snomed);

/*
drop table test.rxsnomeds;
create table test.rxSnomeds tablespace disk2 as(
select distinct a.rxcui,cast(a.code as bigint) snomed,a.str term, b.atv ndc,c.str drugname 
from terminology.rxnconso  a
inner join  terminology.rxnsat b on a.rxcui=b.rxcui and b.atn='NDC'
inner join terminology.rxnconso c on c.rxaui=b.rxaui
where a.sab like 'SNOMED%CT%'  and a.tty='PT' ) ;
create index rxsnocui on test.rxsnomeds(rxcui);
create index rxsnondc on test.rxsnomeds(ndc);
create index rxsnosno on test.rxsnomeds(snomed);


insert into test.rxsnomeds(
select a.rxcui1,snomed,term,d.atv,e.str from terminology.rxnrel a 
inner join terminology.rxnrel b on a.rxcui2=b.rxcui1 and a.rela='constitutes'
inner join test.rxsnomeds c on b.rxcui2=c.rxcui and b.rela='ingredient_of'
inner join terminology.rxnsat d on d.atn ='NDC' and a.rxcui1=d.rxcui
inner join terminology.rxnconso e on d.rxaui=e.rxaui
inner join (select distinct a.rxcui
from terminology.rxnsat a
left outer join test.rxsnomeds b on a.rxcui=b.rxcui
where a.atn='NDC' and b.rxcui is null 
) x on a.rxcui1=x.rxcui
);
create table terminology.rxSnomeds as select distinct * from test.rxsnomeds;
create index rxsnocui on terminology.rxsnomeds(rxcui);
create index rxsnondc on terminology.rxsnomeds(ndc);
create index rxsnosno on terminology.rxsnomeds(snomed);
*/

truncate table terminology.rxsnomeds;
\COPY terminology.rxsnomeds from 'rxsnomeds.csv' DELIMITER ',' CSV

/*insert into terminology.drugclassancestry(
select distinct  dc.rxaui ,ndc.rxaui ,max(coalesce(brand.str,member.str||' (generic)')) ,max(route.groupname),ndc.atv,max(dc.str),max(member.str)
from terminology.drugclass dc
inner join terminology.rxnrel a on a.rxaui1=dc.rxaui and a.rela='member_of'
inner join terminology.rxnconso member on member.rxaui=a.rxaui2 
inner join terminology.rxnrel rel2 on rel2.rxcui1=member.rxcui and rel2.rela='has_ingredient'
inner join terminology.rxnconso drug on drug.rxcui=rel2.rxcui2 and drug.sab='RXNORM' and drug.tty!='TMSY'
inner join terminology.rxnrel rel3 on rel3.rxcui1=drug.rxcui and rel3.rela in ('consists_of','isa')
inner join terminology.rxnconso soldas on soldas.rxcui=rel3.rxcui2 and soldas.sab='RXNORM' and soldas.tty='SY'
--check if there's an NDC for the thing
inner join terminology.rxnsat ndc on ndc.rxcui=soldas.rxcui and ndc.atn='NDC'  and ndc.sab='RXNORM' 
inner join terminology.rxnrel routerel on routerel.rxcui1=ndc.rxcui and routerel.rela='dose_form_of'
inner join terminology.doseformgroups route on routerel.rxcui2=route.rxcui
left outer join terminology.rxnrel brel on brel.rxcui1=ndc.rxcui and brel.rela='ingredient_of'
left outer join terminology.rxnconso brand on brel.rxcui2=brand.rxcui and brand.tty='BN'
group by dc.rxaui ,ndc.rxaui,ndc.atv
);*/

\COPY terminology.drugclassancestry from 'drugclassancestry.csv' DELIMITER ',' CSV

-- Starting from the granular NDC code, go up the hierarchy to the class, and get THAT Snomed ID
create or replace function getClassSnomedFromNDC(v_ndc varchar(20))
  RETURNS numeric AS
$BODY$
Declare rtn numeric;
begin
        select max(c.SnomedId) into rtn 
        from terminology.drugclassancestry b
        inner join terminology.drugclass c on b.classaui=c.rxaui
         where b.ndc=v_ndc ;

        return rtn;
end;
$BODY$
  LANGUAGE plpgsql;


create or replace function getClassNameFromNDC(v_ndc varchar(20))
  RETURNS varchar(200) AS
$BODY$
Declare rtn varchar(200);
begin
        select classname into rtn from terminology.drugclassancestry a
	inner join terminology.drugclass b on a.classaui=b.rxaui
        where ndc=v_ndc
        order by snomedid limit 1;
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
		from terminology.drugclassancestry a 
		inner join terminology.drugclass b on a.classaui=b.rxaui
		where inclassaui=vrxaui and snomedid is not null;
        return isSnomedChild(vparentconcept,sno);
end;
$BODY$
  LANGUAGE plpgsql ;

create or replace function getNadacFromNDC(v_ndc varchar(20)) 
returns numeric(18,2) as
$BODY$
declare nadacCost numeric(18,2);
begin
 select unitcost into nadacCost from public.nadac where ndc=v_ndc limit 1;
 return nadaccost;
end;
$BODY$
   language plpgsql;
   
create or replace function GetAlternativeTable(v_ndc varchar(20))
returns table(brandname varchar(200),relCost numeric(18,2)) as
$BODY$
declare nadacCost numeric(18,2);
begin
      --select getNadacFromNDC(v_ndc) into nadacCost;
      return query select x.brandname,avg(nadac.unitcost)--,avg(nadac.unitcost)*nadacCost
         from terminology.drugclassancestry b
                inner join terminology.drugclassancestry x on x.classaui=b.classaui
                inner join public.nadac nadac on nadac.ndc=x.ndc
                 where b.ndc=v_ndc
                 and x.routename=b.routename
        group by x.brandname;

end;
$BODY$
   language plpgsql;
--select * from getalternativetable('00002323130')

alter table terminology.rxnconso owner to maven;
alter table terminology.rxnrel owner to maven;
alter table terminology.rxnsat owner to maven;

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
