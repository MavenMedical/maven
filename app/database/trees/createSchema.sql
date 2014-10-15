\connect maven;

-- Name: trees; Type: SCHEMA; Schema: -; Owner: maven
CREATE SCHEMA trees;
ALTER SCHEMA trees OWNER TO maven;

/**
**************
**************
TABLES IN TREES SCHEMA
**************
**************
*/
-- Name: trees.activity; Type: TABLE; Schema: trees; Owner: maven; Tablespace:
CREATE TABLE trees.activity (
    activity_id serial NOT NULL,
    customer_id integer,
    user_id integer,
    patient_id character varying(100),
    protocol_id integer,
    node_id integer,
    datetime timestamp without time zone,
    action character varying(32)
);
ALTER TABLE trees.activity OWNER TO maven;
ALTER TABLE ONLY trees.activity
    ADD CONSTRAINT activity_pkey PRIMARY KEY (activity_id);
CREATE INDEX ixactivity ON trees.activity USING btree (protocol_id);
CREATE INDEX ixuseractivity ON trees.activity USING btree (protocol_id, user_id);


-- Name: trees.codelist; Type: TABLE; Schema: trees; Owner: maven; Tablespace:
CREATE TABLE trees.codelist (
    protocol_id integer NOT NULL,
    node_id integer,
    listtype character varying(20),
    isintersect boolean,
    intlist bigint[],
    strlist character varying[],
    framemin integer,
    framemax integer
);
ALTER TABLE trees.codelist OWNER TO maven;
CREATE INDEX ixprotocolid ON trees.codelists USING btree (protocol_id);

-- Name: trees.labeval; Type: TABLE; Schema: trees; Owner: maven; Tablespace:
CREATE TABLE trees.labeval (
    protocol_id numeric(18,0),
    loinc_codes character varying[],
    threshold double precision,
    relation character varying(1),
    framemin integer,
    framemax integer,
    defaultval boolean,
    onlychecklast boolean
);
ALTER TABLE trees.labeval OWNER TO maven;
CREATE INDEX ixprotolabeval ON trees.labeval USING btree (protocol_id, loinc_codes);

-- Name: trees.protocol; Type: TABLE; Schema: trees; Owner: maven; Tablespace:
CREATE TABLE trees.protocol (
    protocol_id integer NOT NULL,
    customer_id integer,
    name character varying(100),
    description character varying,
    minage numeric(18,2),
    maxage numeric(18,2),
    sex character varying(1),
    full_spec json
);
ALTER TABLE trees.protocol OWNER TO maven;
ALTER TABLE ONLY trees.protocol
    ADD CONSTRAINT protocol_pkey PRIMARY KEY (protocol_id);
CREATE INDEX ixprotocolpk ON trees.protocol USING btree (protocol_id);

/**
**************
**************
FUNCTIONS IN TREES SCHEMA
**************
**************
*/
-- Name: trees.comparisonstrarray(character varying, character varying, integer, integer, integer, character varying[]); Type: FUNCTION; Schema: trees; Owner: maven
CREATE OR REPLACE FUNCTION trees.comparisonstrarray(listtype character varying, patid character varying, framemin integer, framemax integer, customer integer, druglist character varying[]) RETURNS character varying[]
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
ALTER FUNCTION trees.comparisonstrarray(listtype character varying, patid character varying, framemin integer, framemax integer, customer integer, druglist character varying[]) OWNER TO maven;

-- Name: trees.comparisonintarray(character varying, bigint[], bigint[], character varying, integer, integer, integer); Type: FUNCTION; Schema: trees; Owner: maven
CREATE OR REPLACE FUNCTION trees.comparisonintarray(listtype character varying, encsnomeds bigint[], probsnomeds bigint[], patid character varying, framemin integer, framemax integer, customer integer) RETURNS bigint[]
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
ALTER FUNCTION trees.comparisonintarray(listtype character varying, encsnomeds bigint[], probsnomeds bigint[], patid character varying, framemin integer, framemax integer, customer integer) OWNER TO maven;

-- Name: trees.upsert_codelist(integer, integer, character varying, boolean, integer[], character varying[], integer, integer); Type: FUNCTION; Schema: trees; Owner: maven
CREATE OR REPLACE FUNCTION trees.upsert_codelist(v_protocol_id integer, v_node_id integer, v_listtype character varying, v_isintersect boolean, v_intlist integer[], v_strlist character varying[], v_framemin integer, v_framemax integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
  BEGIN
    LOOP
      UPDATE trees.codelist SET intlist = (select (select array_agg(child) from terminology.conceptancestry where ancestor = ANY(v_intlist)) as bigint), strlist = v_strlist, framemin = v_framemin, framemax = v_framemax, isintersect = v_isintersect
      WHERE protocol_id = v_protocol_id AND node_id = v_node_id AND listtype = v_listtype;
      IF found THEN
        RETURN;
      END IF;
      BEGIN
        INSERT INTO trees.codelist(protocol_id, node_id, listtype, isintersect, intlist, strlist, framemin, framemax)
          VALUES (v_protocol_id, v_node_id, v_listtype, v_isintersect, (select (select array_agg(child) from terminology.conceptancestry where ancestor = ANY(v_intlist)) as bigint), v_strlist, v_framemin, v_framemax);
        RETURN;
      EXCEPTION WHEN unique_violation THEN
      END;
    END LOOP;
  END;
$$;
ALTER FUNCTION trees.upsert_codelist(v_protocol_id integer, v_node_id integer, v_listtype character varying, v_isintersect boolean, v_intlist integer[], v_strlist character varying[], v_framemin integer, v_framemax integer) OWNER TO maven;

-- Name: trees.insertprotocol(json, numeric, character varying, character varying, numeric, numeric, character varying); Type: FUNCTION; Schema: trees; Owner: maven
CREATE OR REPLACE FUNCTION trees.insertprotocol(fullspec json, custid_in integer, name_in character varying, desc_in character varying DEFAULT ''::character varying, minage_in numeric DEFAULT 0, maxage_in numeric DEFAULT 200, sex_in character varying DEFAULT '%'::character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
declare
	v_pathid int;
begin
	select coalesce(max(protocol_id)+1,1) into v_pathid from trees.protocol;
	insert into trees.protocol (protocol_id,customer_id,name,description,minage,maxage,sex,full_spec)
		values(v_pathid,custid_in,name_in,desc_in,minage_in,maxage_in,sex_in,fullspec);
	return v_pathid;
exception when others then
	return -1;
end;
$$;
ALTER FUNCTION trees.insertprotocol(fullspec json, custid_in integer, name_in character varying, desc_in character varying, minage_in numeric, maxage_in numeric, sex_in character varying) OWNER TO maven;

-- Name: trees.evallabs(integer, character varying, integer, integer, boolean, character varying, double precision, character varying[], boolean); Type: FUNCTION; Schema: trees; Owner: maven
CREATE OR REPLACE FUNCTION trees.evallabs(cust integer, pat character varying, framemin integer, framemax integer, defval boolean, relation character varying, comparison double precision, loincs character varying[], onlylast boolean) RETURNS boolean
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
ALTER FUNCTION trees.evallabs(cust integer, pat character varying, framemin integer, framemax integer, defval boolean, relation character varying, comparison double precision, loincs character varying[], onlylast boolean) OWNER TO maven;

-- Name: trees.evalnode(integer, numeric, character varying, bigint[], bigint[], character varying, integer, character varying[]); Type: FUNCTION; Schema: trees; Owner: maven
CREATE OR REPLACE FUNCTION trees.evalnode(node_id integer, patage numeric, patsex character varying, encsnomeds bigint[], probsnomeds bigint[], patid character varying, customer integer, curmedlist character varying[]) RETURNS TABLE(id integer, name character varying, description character varying, full_spec json)
    LANGUAGE plpgsql
    AS $_$
begin
return query execute
    'select x.protocol_id,x.name,x.description,x.full_spec from
    (
    select a.protocol_id
    from trees.protocol a
    inner join trees.codelist c on a.protocol_id=c.protocol_id
    where
    a.minage<=$1 and a.maxage>=$1
    and $2 like a.sex
    and c.node_id=node_id
    group by a.protocol_id
    having min(case when c.isIntersect=(
    (intlist is not null and trees.comparisonIntArray(c.listType,$3,$4,$5,c.framemin,c.framemax,$6)&&c.intList)
    or
    (strlist is not null and trees.comparisonStrArray(c.listType,$5,c.framemin,c.framemax,$6,$7)&&c.strList)
    )
    then 1 else 0 end)=1
    ) sub inner join trees.protocol x on sub.protocol_id=x.protocol_id
    inner join public.alert_config d on d.rule_id=sub.protocol_id and d.customer_id=$6 and d.validation_status>0
    left outer join trees.labEval y on x.protocol_id=y.protocol_id
    where (y.protocol_id is null or trees.evalLabs($6,$5,y.framemin,y.framemax,y.defaultval,y.relation,y.threshold,y.loinc_codes,y.onlychecklast))'
    using patAge , patSex , encSnomeds , probSnomeds ,patid,customer,curMedList;
end;
$_$;
ALTER FUNCTION trees.evalnode(node_id integer, patage numeric, patsex character varying, encsnomeds bigint[], probsnomeds bigint[], patid character varying, customer integer, curmedlist character varying[]) OWNER TO maven;

REVOKE ALL ON SCHEMA trees FROM PUBLIC;
REVOKE ALL ON SCHEMA trees FROM maven;
GRANT ALL ON SCHEMA trees TO maven;