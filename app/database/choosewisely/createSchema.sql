\connect maven;

-- Name: rules; Type: SCHEMA; Schema: -; Owner: postgres
CREATE SCHEMA choosewisely;
ALTER SCHEMA choosewisely OWNER TO maven;

/**
**************
**************
TABLES IN CHOOSING WISELY SCHEMA
**************
**************
*/
-- Name: choosewisely.codelists; Type: TABLE; Schema: choosewisely; Owner: maven; Tablespace:
CREATE TABLE choosewisely.codelists (
    ruleid integer,
    listtype character varying(20),
    isintersect boolean,
    intlist bigint[],
    strlist character varying[],
    framemin integer,
    framemax integer,
    detailid integer,
    term text
);
ALTER TABLE choosewisely.codelists OWNER TO maven;
CREATE INDEX ixrulecodelistsid ON choosewisely.codelists USING btree (ruleid);

-- Name: choosewisely.evirule; Type: TABLE; Schema: choosewisely; Owner: maven; Tablespace:
CREATE TABLE choosewisely.evirule (
    ruleid integer NOT NULL,
    name character varying(200),
    minage numeric(18,2),
    maxage numeric(18,2),
    sex character varying(1),
    codetype character varying(20),
    remainingdetails text,
    fullspec text,
    comments text
);
ALTER TABLE choosewisely.evirule OWNER TO maven;
ALTER TABLE ONLY choosewisely.evirule
    ADD CONSTRAINT evirule_pkey PRIMARY KEY (ruleid);
CREATE INDEX ixrulepk ON choosewisely.evirule USING btree (ruleid);
CREATE INDEX ixruletypeagesex ON choosewisely.evirule USING btree (codetype, minage, maxage, sex);

-- Name: choosewisely.labeval; Type: TABLE; Schema: choosewisely; Owner: postgres; Tablespace:
CREATE TABLE choosewisely.labeval (
    ruleid integer,
    loinc_codes character varying[],
    threshold double precision,
    relation character varying(1),
    framemin integer,
    framemax integer,
    defaultval boolean,
    onlychecklast boolean
);
ALTER TABLE choosewisely.labeval OWNER TO maven;
CREATE INDEX ixlabevalrule ON choosewisely.labeval USING btree (ruleid, loinc_codes);

-- Name: choosewisely.trigcodes; Type: TABLE; Schema: choosewisely; Owner: maven; Tablespace:
CREATE TABLE trigcodes (
    ruleid integer NOT NULL,
    code character varying(50) NOT NULL
);
ALTER TABLE choosewisely.trigcodes OWNER TO maven;
ALTER TABLE ONLY chooosewisely.trigcodes
    ADD CONSTRAINT trigcodes_pkey PRIMARY KEY (ruleid, code);
CREATE INDEX ixtrigcodecode ON choosewisely.trigcodes USING btree (code, ruleid);
CREATE INDEX ixtrigcodepk ON choosewisely.trigcodes USING btree (ruleid, code);

-- Name: sleuth_evidence; Type: TABLE; Schema: choosewisely; Owner: maven; Tablespace:
CREATE TABLE choosewisely.evidence (
    evidence_id serial NOT NULL,
    customer_id numeric(18,0),
    rule_id integer,
    short_name character varying(25),
    name character varying(100),
    description character varying,
    source character varying(100),
    source_url character varying(255)
);
ALTER TABLE choosewisely.evidence OWNER TO maven;
CREATE INDEX ixevidence ON choosewisely.evidence USING btree (rule_id)

-- Name: override_indication; Type: TABLE; Schema: choosewisely; Owner: maven; Tablespace:
CREATE TABLE choosewisely.override_indication (
    override_id serial NOT NULL,
    customer_id integer,
    sleuth_rule integer,
    category character varying(255),
    name character varying(25),
    description character varying(255)
);
ALTER TABLE choosewisely.override_indication OWNER TO maven;
ALTER TABLE ONLY chooosewisely.override_indication
    ADD CONSTRAINT override_indication_pkey PRIMARY KEY (override_id);

/**
**************
**************
FUNCTIONS IN CHOOSING WISELY SCHEMA
**************
**************
*/
-- Name: choosewisely.comparisonintarray(character varying, bigint[], bigint[], character varying, integer, integer, integer); Type: FUNCTION; Schema: rules; Owner: postgres
CREATE FUNCTION choosewisely.comparisonintarray(listtype character varying, encsnomeds bigint[], probsnomeds bigint[], patid character varying, framemin integer, framemax integer, customer integer) RETURNS bigint[]
    LANGUAGE plpgsql
    AS $$
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
$$;
ALTER FUNCTION choosewisely.comparisonintarray(listtype character varying, encsnomeds bigint[], probsnomeds bigint[], patid character varying, framemin integer, framemax integer, customer integer) OWNER TO postgres;

-- Name: choosewisely.comparisonstrarray(character varying, character varying, integer, integer, integer, character varying[]); Type: FUNCTION; Schema: rules; Owner: postgres
CREATE FUNCTION choosewisely.comparisonstrarray(listtype character varying, patid character varying, framemin integer, framemax integer, customer integer, druglist character varying[]) RETURNS character varying[]
    LANGUAGE plpgsql
    AS $$
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
$$;
ALTER FUNCTION choosewisely.comparisonstrarray(listtype character varying, patid character varying, framemin integer, framemax integer, customer integer, druglist character varying[]) OWNER TO postgres;

-- Name: choosewisely.evallabs(integer, character varying, integer, integer, boolean, character varying, double precision, character varying[], boolean); Type: FUNCTION; Schema: rules; Owner: postgres
CREATE FUNCTION choosewisely.evallabs(cust integer, pat character varying, framemin integer, framemax integer, defval boolean, relation character varying, comparison double precision, loincs character varying[], onlylast boolean) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
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
 $$;
ALTER FUNCTION choosewisely.evallabs(cust integer, pat character varying, framemin integer, framemax integer, defval boolean, relation character varying, comparison double precision, loincs character varying[], onlylast boolean) OWNER TO postgres;

-- Name: evalrules(character varying, character varying, numeric, character varying, bigint[], bigint[], character varying, integer, character varying[]); Type: FUNCTION; Schema: rules; Owner: maven
CREATE FUNCTION choosewisely.evalrules(ordercode character varying, ordcodetype character varying, patage numeric, patsex character varying, encsnomeds bigint[], probsnomeds bigint[], patid character varying, customer integer, curmedlist character varying[]) RETURNS TABLE(rule_id integer, name character varying, details text, status integer, fullspec text)
    LANGUAGE plpgsql
    AS $_$
begin
                return query execute
                'select DISTINCT x.rule_id,x.name,x.remainingDetails,d.validation_status,x.fullspec from
                (
                select a.rule_id
                from choosewisely.eviRule a
                  inner join choosewisely.trigCodes b on a.rule_id=b.rule_id and b.code=$1
                  inner join choosewisely.codeLists c on a.rule_id=c.rule_id
                  
                where
                   a.codetype=$2
                   and a.minage<=$3 and a.maxage>=$3
                   and $4 like a.sex
                group by a.rule_id
                having min(case when c.isIntersect=(
                        (intlist is not null and choosewisely.comparisonIntArray(c.listType,$5,$6,$7,c.framemin,c.framemax,$8)&&c.intList)
                        or
                        (strlist is not null and choosewisely.comparisonStrArray(c.listType,$7,c.framemin,c.framemax,$8,$9)&&c.strList)
                      )
                  then 1 else 0 end)=1
                ) sub inner join choosewisely.evirule x on sub.rule_id=x.rule_id
                inner join public.alert_config d on d.rule_id=sub.rule_id and d.customer_id=$8 and d.validation_status>0
                left outer join choosewisely.labEval y on x.rule_id=y.rule_id
                where (y.rule_id is null or choosewisely.evalLabs($8,$7,y.framemin,y.framemax,y.defaultval,y.relation,y.threshold,y.loinc_codes,y.onlychecklast))'
                using orderCode , ordcodeType , patAge , patSex , encSnomeds , probSnomeds ,patid,customer,curMedList
                ;

end;
$_$;
ALTER FUNCTION choosewisely.evalrules(ordercode character varying, ordcodetype character varying, patage numeric, patsex character varying, encsnomeds bigint[], probsnomeds bigint[], patid character varying, customer integer, curmedlist character varying[]) OWNER TO maven;

REVOKE ALL ON SCHEMA choosewisely FROM PUBLIC;
REVOKE ALL ON SCHEMA choosewisely FROM maven;
GRANT ALL ON SCHEMA choosewisely TO maven;