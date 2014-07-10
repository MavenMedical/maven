create schema rules;

create table rules.eviRule
(
  ruleId int primary key,
  name varchar(200) ,
  minAge numeric(18,2),
  maxAge numeric(18,2),
  sex varchar(1),
  codeType varchar(20),
  remainingDetails text,
  fullspec text,
  comments text
);
alter table rules.evirule owner to maven;
create index ixRulePk on rules.eviRule(ruleId);
create index ixRuleTypeAgeSex on rules.eviRule(codeType,minAge,maxAge,sex);

create table rules.trigCodes
(
  ruleId int,
  code varchar(50),
  primary key (ruleId,code)
);
alter table rules.trigCodes owner to maven;
create index ixTrigCodePk on rules.trigCodes(ruleId,code);
create index ixTrigCodeCode on rules.trigCodes(code,ruleId);

create table rules.codeLists
(
  ruleId int
  ,listType varchar(20)
  ,isIntersect boolean
  ,intList bigint[]
  ,strList varchar[]
  ,framemin int
  ,framemax int
);
alter table rules.codeLists owner to maven;
create index ixruleCodeListsId on rules.codelists(ruleid);
--CREATE INDEX rules.ixcodelistgin rules.codelists USING gin(intlist);

create  table rules.labeval(
	ruleid int
	,loinc_codes varchar[]
	,threshold double precision
	,relation varchar(1)
	,framemin int
	,framemax int
	,defaultval boolean
);
create index ixlabevalRule on rules.labeval(ruleid,loinc_codes);

 create or replace function rules.evalLabs(cust int, pat varchar(100),framemin int, framemax int, defval boolean,relation varchar(1),comparison double precision,loincs varchar[])
 returns boolean
 as $$
 declare
	rtn int;
 begin
	if relation='<' then
		select max(case when numeric_result<comparison then 1 else 0 end) into rtn
		from public.observation a
		where a.customer_id=cust and a.pat_id=pat and a.loinc_code=any(loincs)
		  and current_date+framemin<=result_time and current_date+framemax>=result_time;
	elsif relation='>' then
		select max(case when numeric_result>comparison then 1 else 0 end) into rtn
		from public.observation a
		where a.customer_id=cust and a.pat_id=pat and a.loinc_code=any(loincs)
		  and current_date+framemin<=result_time and current_date+framemax>=result_time;
	elsif relation='=' then
		select max(case when numeric_result=comparison then 1 else 0 end) into rtn
		from public.observation a
		where a.customer_id=cust and a.pat_id=pat and a.loinc_code=any(loincs)
		  and current_date+framemin<=result_time and current_date+framemax>=result_time;
	else return defval;
	end if;
	return case when rtn=1 then true when rtn=0 then false else defval end;
 end;
 $$
 language plpgsql;

create or replace function rules.comparisonIntArray(listType varchar(20),encSnomeds bigint[],probsnomeds bigint[],patid varchar(100),framemin int,framemax int,customer int)
returns bigint[] as $$
declare rtn bigint[];
	mn int;
	mx int;
begin
	mn:=coalesce(framemin,-99999);
	mx:=coalesce(framemin,1);
	if listType='PL' then
		return probsnomeds;
	elsif listtype='ENC' then
		return encSnomeds;
	elsif listtype='DXHX' then
		select encsnomeds||probsnomeds||array_agg(snomed_id) into rtn
			from public.condition a
			where a.pat_id=patid and a.customer_id=customer and  current_date+mn<=date_asserted and current_date+mx>=date_asserted
			group by a.pat_id ;
		return rtn;
	else
		return null;
	end if;
end;
$$
language plpgsql;

create index ixordPatCptDt on public.order_ord(customer_id,pat_id,code_id,order_datetime,code_system) where code_system='CPT';

create or replace function rules.comparisonStrArray(listType varchar(20),patid varchar(100),framemin int,framemax int,customer int)
returns varchar[] as $$
declare rtn varchar[];
	mn int;
	mx int;
begin
	mn:=coalesce(framemin,-99999);
	mx:=coalesce(framemin,1);
	if listType='HXPX' then
		select array_agg(proc_code) into rtn
			from public.order_ord a
			where a.pat_id=patid and a.customer_id=customer and code_type='CPT' and current_date+mn<=datetime and current_date+mx>=datetime
			group by a.pat_id ;
		return rtn;
	else
		return null;
	end if;
end;
$$
language plpgsql;

create or replace function rules.evalRules(orderCode varchar, ordcodeType varchar, patAge numeric(18,2), patSex varchar, encSnomeds bigint[], probSnomeds bigint[],patid varchar(100),customer int)
returns table (ruleid int, name varchar,details text) as $$
begin
                return query execute
                'select x.ruleid,x.name,x.remainingDetails from
                (
                select a.ruleid
                from rules.eviRule a
		  inner join rules.trigCodes b on a.ruleId=b.ruleId and b.code=$1
		  inner join rules.codeLists c on a.ruleId=c.ruleId
                where
                   a.codetype=$2
                   and a.minage<=$3 and a.maxage>=$3
                   and $4 like a.sex
                group by a.ruleid
                having min(case when c.isIntersect=(
			(intlist is not null and rules.comparisonIntArray(c.listType,$5,$6,$7,c.framemin,c.framemax,$8)&&c.intList)
			or
			(strlist is not null and rules.comparisonStrArray(c.listType,$7,c.framemin,c.framemax,$8)&&c.strList)
		      )
		  then 1 else 0 end)=1
                ) sub inner join rules.evirule x on sub.ruleid=x.ruleid
                left outer join rules.labEval y on x.ruleid=y.ruleid
                where (y.ruleid is null or rules.evalLabs($8,$7,y.framemin,y.framemax,y.defaultval,y.relation,y.threshold,y.loinc_codes))'
                using orderCode , ordcodeType , patAge , patSex , encSnomeds , probSnomeds ,patid,customer
                ;

end;
$$
language plpgsql;

