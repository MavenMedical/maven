
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
	where (a.atn='DRUG_CLASS_TYPE' and a.sab='VANDF' and a.atv='2')
              or (a.atn='ATC_LEVEL' and a.sab='ATC' and a.atv='4')
);


update drugclass dc set snomedid= (select min(cast(scui as numeric)) from rxnconso a where a.rxcui=dc.rxcui and a.sab ='SNOMEDCT_US' and tty='PT');


create table terminology.drugClassAncestry
(
   classAui varchar(20) 
   ,inClassAui varchar(20)
   ,primary key (classaui,inclassaui)
);
create index ixDrugClassAncestryPK on terminology.drugClassAncestry (classaui,inclassaui);
create index ixDrugClassAncestryReverse on terminology.drugClassAncestry (inclassaui,classaui);

create or replace function  populateDrugAncestry() returns void as
$BODY$
declare aui varchar(20);

begin
	for aui in select rxaui from drugclass where rxaui not in (select distinct classaui from terminology.drugclassAncestry)
	loop
		
		insert into terminology.drugClassAncestry
		(
			select distinct dclass,sat.rxaui from 
			(
				select dc.rxaui dclass, a.rela,b.str first_concept,b.rxcui first_cui,dc.str dclassstr
				from rxnrel a
				inner join drugclass dc on a.rxaui1=dc.rxaui
				inner join rxnconso b on a.rxaui2=b.rxaui and a.rela='member_of'
			) first
			inner join 
			(
				select a.rxcui1 first_cui,b.str second_concept,b.rxcui second_cui
				from rxnrel a
				inner join rxnconso b on a.rxcui2=b.rxcui and a.rela='tradename_of'
			) second on first.first_cui=second.first_cui
			inner join 
			(
				select a.rxcui1 second_cui,b.str second_concept,b.rxcui third_cui,a.rela
				from rxnrel a
				inner join rxnconso b on a.rxcui2=b.rxcui and a.rela='has_ingredient'
			) third on third.second_cui=second.second_cui
			inner join rxnsat sat on sat.rxcui=third.third_cui
			where dclass=aui
		);
	end loop;
end;
$BODY$
LANGUAGE plpgsql;

select populateDrugAncestry();

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


CREATE OR REPLACE FUNCTION terminology.isRxCUIchild(vparentconcept numeric, vrxaui character varying)
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
