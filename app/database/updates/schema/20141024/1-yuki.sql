DROP FUNCTION IF EXISTS trees.comparisonstrarray(listtype character varying, patid character varying, framemin integer, framemax integer, customer integer, druglist character varying[]);
DROP FUNCTION IF EXISTS trees.comparisonintarray(listtype character varying, encsnomeds bigint[], probsnomeds bigint[], patid character varying, framemin integer, framemax integer, customer integer);
DROP FUNCTION IF EXISTS trees.evallabs(cust integer, pat character varying, framemin integer, framemax integer, defval boolean, relation character varying, comparison double precision, loincs character varying[], onlylast boolean);

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
			where a.patient_id=patid and a.customer_id=customer and code_system='HCPCS' and current_date+mn<=order_datetime and current_date+mx>=order_datetime
			group by a.patient_id ;
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
                        where a.patient_id=patid and a.customer_id=customer and  current_date+mn<=date_asserted and current_date+mx>=date_asserted
                        group by a.patient_id ;
                return rtn;
        else
                return null;
        end if;
end;
$$;
ALTER FUNCTION trees.comparisonintarray(listtype character varying, encsnomeds bigint[], probsnomeds bigint[], patid character varying, framemin integer, framemax integer, customer integer) OWNER TO maven;

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
                where a.customer_id=cust and a.patient_id=pat and a.loinc_code=any(loincs)
                  and current_date+framemin<=result_time and current_date+framemax>=result_time
                order by result_time desc limit case when onlylast then 1 else 9999999 end ) a;
        elsif relation='>' then
                select max(case when numeric_result>comparison then 1 else 0 end) into rtn
                from (select numeric_result from public.observation a
                where a.customer_id=cust and a.patient_id=pat and a.loinc_code=any(loincs)
                  and current_date+framemin<=result_time and current_date+framemax>=result_time
                order by result_time desc limit case when onlylast then 1 else 9999999 end ) a;
        elsif relation='=' then
                select max(case when numeric_result=comparison then 1 else 0 end) into rtn
                from (select numeric_result from public.observation a
                where a.customer_id=cust and a.patient_id=pat and a.loinc_code=any(loincs)
                  and current_date+framemin<=result_time and current_date+framemax>=result_time
                order by result_time desc limit case when onlylast then 1 else 9999999 end ) a;
        else return defval;
        end if;
        return case when rtn=1 then true when rtn=0 then false else defval end;
 end;
 $$;
ALTER FUNCTION trees.evallabs(cust integer, pat character varying, framemin integer, framemax integer, defval boolean, relation character varying, comparison double precision, loincs character varying[], onlylast boolean) OWNER TO maven;

