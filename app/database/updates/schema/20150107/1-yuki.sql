DROP FUNCTION IF EXISTS trees.comparisonstrarray(character varying, character varying, integer, integer, integer, character varying[]);

-- Function: trees.comparisonstrarray(character varying, character varying, integer, integer, integer, character varying[])
-- DROP FUNCTION trees.comparisonstrarray(character varying, character varying, integer, integer, integer, character varying[]);
CREATE OR REPLACE FUNCTION trees.comparisonstrarray(listtype character varying, patid character varying, framemin integer, framemax integer, customer integer, druglist character varying[], prochist CHARACTER VARYING[])
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
			where a.patient_id=patid and a.customer_id=customer and code_system='HCPCS' and current_date+mn<=order_datetime and current_date+mx>=order_datetime
			group by a.patient_id ;
		return rtn||prochist;
	elsif listType='drug_list' then
		return druglist;
	else
		return null;
	end if;
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION trees.comparisonstrarray(character varying, character varying, integer, integer, integer, character varying[], CHARACTER VARYING[])
  OWNER TO maven;



DROP FUNCTION IF EXISTS trees.evalnode(integer, numeric, character varying, bigint[], bigint[], bigint[], character varying, integer, character varying[], character varying, character varying);
-- Function: trees.evalnode(integer, numeric, character varying, bigint[], bigint[], bigint[], character varying, integer, character varying[], character varying, character varying)
-- DROP FUNCTION trees.evalnode(integer, numeric, character varying, bigint[], bigint[], bigint[], character varying, integer, character varying[], character varying, character varying);
CREATE OR REPLACE FUNCTION trees.evalnode(IN node_id integer, IN patage numeric, IN patsex character varying, IN encsnomeds bigint[], IN probsnomeds bigint[], IN histsnomeds bigint[], IN patid character varying, IN customer integer, IN curmedlist character varying[], IN prov_id character varying, IN enc_id character varying, IN prochistry CHARACTER VARYING[])
  RETURNS TABLE(id integer, name character varying, description character varying, full_spec json, priority integer) AS
$BODY$
begin
return query execute
    'select x.protocol_id, sub.name, x.description, x.full_spec, d.priority from
    (
    select cp.current_id, cp.canonical_id, cp.name
    from trees.canonical_protocol cp
    inner join trees.protocol a on cp.current_id=a.protocol_id
    inner join trees.codelist c on a.canonical_id=c.canonical_id
    left outer join public.alert l on a.customer_id=l.customer_id and a.protocol_id=l.cds_rule and l.provider_id=$8 and l.patient_id=$5 and l.encounter_id=$9
    where
    cp.enabled and
    a.minage<=$1 and a.maxage>=$1
    and $2 like a.sex
    and c.node_id=node_id
    and l.alert_id is null
    and not cp.deleted
    group by cp.current_id, cp.canonical_id, cp.name
    having min(case when c.isIntersect=(
    (intlist is not null and trees.comparisonIntArray(c.listType,$3,$4,$10,$5,c.framemin,c.framemax,$6)&&c.intList)
    or
    (strlist is not null and trees.comparisonStrArray(c.listType,$5,c.framemin,c.framemax,$6,$7,$11)&&c.strList)
    )
    then 1 else 0 end)=1
    ) sub inner join trees.protocol x on sub.current_id=x.protocol_id
    inner join public.alert_config d on d.rule_id=sub.canonical_id and d.customer_id=$6 and d.validation_status>0
    left outer join trees.labEval y on x.protocol_id=y.protocol_id
    where (y.protocol_id is null or trees.evalLabs($6,$5,y.framemin,y.framemax,y.defaultval,y.relation,y.threshold,y.loinc_codes,y.onlychecklast))'

    using patAge, patSex, encSnomeds, probSnomeds, patid, customer, curMedList, prov_id, enc_id, histsnomeds, prochistry;
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION trees.evalnode(integer, numeric, character varying, bigint[], bigint[], bigint[], character varying, integer, character varying[], character varying, character varying, CHARACTER VARYING[])
  OWNER TO maven;