-- Schema: trees
-- DROP SCHEMA trees;
CREATE SCHEMA trees
  AUTHORIZATION maven;
GRANT ALL ON SCHEMA trees TO maven;

-- Table: trees.protocol
-- DROP TABLE: trees.protocol
CREATE TABLE trees.protocol (
  id numeric(18,0) NOT NULL,
  customer_id numeric(18,0),
  name character varying(100),
  description character varying,
  full_spec json
) WITH (OIDS=FALSE);
ALTER TABLE trees.protocol
    OWNER TO maven;


-- Table: trees.codelist
-- DROP TABLE: trees.codelist
CREATE TABLE trees.codelist (
  protocol_id numeric(18,0) NOT NULL,
  node_id character varying(36),
  listtype character varying(20),
  isintersect boolean,
  intlist bigint[],
  strlist character varying[],
  framemin integer,
  framemax integer
) WITH (OIDS=FALSE);
ALTER TABLE trees.codelist
    OWNER TO maven;
    
    
-- Table: trees.labeval
-- DROP TABLE trees.labeval;
CREATE TABLE trees.labeval
(
  protocol_id numeric(18,0),
  loinc_codes character varying[],
  threshold double precision,
  relation character varying(1),
  framemin integer,
  framemax integer,
  defaultval boolean,
  onlychecklast boolean
) WITH (OIDS=FALSE);
ALTER TABLE trees.labeval
  OWNER TO maven;

-- Index: trees.ixlabevalrule
-- DROP INDEX trees.ixlabevalrule;
CREATE INDEX ixlabevalrule
  ON trees.labeval
  USING btree
  (protocol_id, loinc_codes COLLATE pg_catalog."default");


-- Function: trees.comparisonintarray(character varying, bigint[], bigint[], character varying, integer, integer, integer)
-- DROP FUNCTION trees.comparisonintarray(character varying, bigint[], bigint[], character varying, integer, integer, integer);
CREATE OR REPLACE FUNCTION trees.comparisonintarray(listtype character varying, encsnomeds bigint[], probsnomeds bigint[], patid character varying, framemin integer, framemax integer, customer integer)
  RETURNS bigint[] AS
$BODY$
declare rtn bigint[];
        mn int;
        mx int;
begin
        mn:=coalesce(framemin,-99999);
        mx:=coalesce(framemin,1);
        if listType='pl_dx' then
                return probsnomeds;
        elsif listtype='enc_dx' then
                return encSnomeds;
        elsif listtype='enc_pl_dx' then
                return encSnomeds||probsnomeds;
        elsif listtype='hist_dx' then
                select encsnomeds||probsnomeds||array_agg(snomed_id) into rtn
                        from public.condition a
                        where a.pat_id=patid and a.customer_id=customer and  current_date+mn<=date_asserted and current_date+mx>=date_asserted
                        group by a.pat_id ;
                return rtn;
        else
                return null;
        end if;
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION trees.comparisonintarray(character varying, bigint[], bigint[], character varying, integer, integer, integer)
  OWNER TO maven;


-- Function: trees.comparisonstrarray(character varying, character varying, integer, integer, integer, character varying[])
-- DROP FUNCTION trees.comparisonstrarray(character varying, character varying, integer, integer, integer, character varying[]);
CREATE OR REPLACE FUNCTION trees.comparisonstrarray(listtype character varying, patid character varying, framemin integer, framemax integer, customer integer, druglist character varying[])
  RETURNS character varying[] AS
$BODY$
declare rtn varchar[];
	mn int;
	mx int;
begin
	mn:=coalesce(framemin,-99999);
	mx:=coalesce(framemin,1);
	if listType='hist_proc' then
		select array_agg(code_id) into rtn
			from public.order_ord a
			where a.pat_id=patid and a.customer_id=customer and code_system='HCPCS' and current_date+mn<=order_datetime and current_date+mx>=order_datetime
			group by a.pat_id ;
		return rtn;
	elsif listType='drug_list' then 
		return druglist;
	else
		return null;
	end if;
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION trees.comparisonstrarray(character varying, character varying, integer, integer, integer, character varying[])
  OWNER TO maven;


-- Function: trees.evallabs(integer, character varying, integer, integer, boolean, character varying, double precision, character varying[], boolean)
-- DROP FUNCTION trees.evallabs(integer, character varying, integer, integer, boolean, character varying, double precision, character varying[], boolean);
CREATE OR REPLACE FUNCTION trees.evallabs(cust integer, pat character varying, framemin integer, framemax integer, defval boolean, relation character varying, comparison double precision, loincs character varying[], onlylast boolean)
  RETURNS boolean AS
$BODY$
 declare
        rtn int;
 begin
        if relation='<' then
                select max(case when numeric_result<comparison then 1 else 0 end) into rtn
                from (select numeric_result from public.observation a
                where a.customer_id=cust and a.pat_id=pat and a.loinc_code=any(loincs)
                  and current_date+framemin<=result_time and current_date+framemax>=result_time
                order by result_time desc limit case when onlylast then 1 else 9999999 end ) a;
        elsif relation='>' then
                select max(case when numeric_result>comparison then 1 else 0 end) into rtn
                from (select numeric_result from public.observation a
                where a.customer_id=cust and a.pat_id=pat and a.loinc_code=any(loincs)
                  and current_date+framemin<=result_time and current_date+framemax>=result_time
                order by result_time desc limit case when onlylast then 1 else 9999999 end ) a;
        elsif relation='=' then
                select max(case when numeric_result=comparison then 1 else 0 end) into rtn
                from (select numeric_result from public.observation a
                where a.customer_id=cust and a.pat_id=pat and a.loinc_code=any(loincs)
                  and current_date+framemin<=result_time and current_date+framemax>=result_time
                order by result_time desc limit case when onlylast then 1 else 9999999 end ) a;
        else return defval;
        end if;
        return case when rtn=1 then true when rtn=0 then false else defval end;
 end;
 $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION trees.evallabs(integer, character varying, integer, integer, boolean, character varying, double precision, character varying[], boolean)
  OWNER TO maven;


-- Function: trees.evalnode(character varying, character varying, numeric, character varying, bigint[], bigint[], character varying, integer, character varying[])
-- DROP FUNCTION trees.evalnode(character varying, character varying, numeric, character varying, bigint[], bigint[], character varying, integer, character varying[]);
CREATE OR REPLACE FUNCTION trees.evalnode(IN ordercode character varying, IN ordcodetype character varying, IN patage numeric, IN patsex character varying, IN encsnomeds bigint[], IN probsnomeds bigint[], IN patid character varying, IN customer integer, IN curmedlist character varying[])
  RETURNS TABLE(ruleid integer, name character varying, details text, status integer, fullspec text) AS
$BODY$
begin
                return query execute
                'select DISTINCT x.ruleid,x.name,x.remainingDetails,d.validation_status,x.fullspec from
                (
                select a.ruleid
                from trees.eviRule a
                  inner join trees.trigCodes b on a.ruleId=b.ruleId and b.code=$1
                  inner join trees.codeLists c on a.ruleId=c.ruleId

                where
                   a.codetype=$2
                   and a.minage<=$3 and a.maxage>=$3
                   and $4 like a.sex
                group by a.ruleid
                having min(case when c.isIntersect=(
                        (intlist is not null and trees.comparisonIntArray(c.listType,$5,$6,$7,c.framemin,c.framemax,$8)&&c.intList)
                        or
                        (strlist is not null and trees.comparisonStrArray(c.listType,$7,c.framemin,c.framemax,$8,$9)&&c.strList)
                      )
                  then 1 else 0 end)=1
                ) sub inner join trees.evirule x on sub.ruleid=x.ruleid
                inner join public.alert_config d on d.rule_id=sub.ruleId and d.customer_id=$8 and d.validation_status>0
                left outer join trees.labEval y on x.ruleid=y.ruleid
                where (y.ruleid is null or trees.evalLabs($8,$7,y.framemin,y.framemax,y.defaultval,y.relation,y.threshold,y.loinc_codes,y.onlychecklast))'
                using orderCode , ordcodeType , patAge , patSex , encSnomeds , probSnomeds ,patid,customer,curMedList;

end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION trees.evalnode(character varying, character varying, numeric, character varying, bigint[], bigint[], character varying, integer, character varying[])
  OWNER TO maven;