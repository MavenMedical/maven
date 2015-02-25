DROP FUNCTION IF EXISTS trees.comparisonintarray(character varying, bigint[], bigint[], character varying, integer, integer, integer);
DROP FUNCTION IF EXISTS trees.evalnode(integer, numeric, character varying, bigint[], bigint[], character varying, integer, character varying[], character varying, character varying);

-- Function: trees.comparisonintarray(character varying, bigint[], bigint[], bigint[], character varying, integer, integer, integer)
-- DROP FUNCTION trees.comparisonintarray(character varying, bigint[], bigint[], bigint[], character varying, integer, integer, integer);
CREATE OR REPLACE FUNCTION trees.comparisonintarray(listtype character varying, encsnomeds bigint[], probsnomeds bigint[], histsnomeds bigint[], patid character varying, framemin integer, framemax integer, customer integer)
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
        elsif listtype='hist_dx' then
                return histsnomeds;
        elsif listtype='enc_pl_dx' then
                return encSnomeds||probsnomeds;
        elsif listtype='all_dx' then
                rtn:=(SELECT array_agg(DISTINCT(snomed_id))
                      FROM public.condition a
                      WHERE a.patient_id=patid and a.customer_id=customer and current_date+mn<=date_asserted and current_date+mx>=date_asserted
                      GROUP BY a.patient_id);
                return encsnomeds||probsnomeds||histsnomeds||rtn;
        else
                return null;
        end if;
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION trees.comparisonintarray(character varying, bigint[], bigint[], bigint[], character varying, integer, integer, integer)
  OWNER TO maven;

-- Function: trees.evalnode(integer, numeric, character varying, bigint[], bigint[], character varying, integer, character varying[], character varying, character varying)
-- DROP FUNCTION trees.evalnode(integer, numeric, character varying, bigint[], bigint[], character varying, integer, character varying[], character varying, character varying);
CREATE OR REPLACE FUNCTION trees.evalnode(IN node_id integer, IN patage numeric, IN patsex character varying, IN encsnomeds bigint[], IN probsnomeds bigint[], IN histsnomeds bigint[], IN patid character varying, IN customer integer, IN curmedlist character varying[], IN prov_id character varying, IN enc_id character varying)
  RETURNS TABLE(id integer, name character varying, description character varying, full_spec json) AS
$BODY$
begin
return query execute
    'select x.protocol_id,x.name,x.description, x.full_spec from
    (
    select a.protocol_id
    from trees.protocol a
    inner join trees.codelist c on a.protocol_id=c.protocol_id
    left outer join public.alert l on a.customer_id=l.customer_id and a.protocol_id=l.cds_rule and l.provider_id=$8 and l.patient_id=$5 and l.encounter_id=$9
    where
    a.minage<=$1 and a.maxage>=$1
    and $2 like a.sex
    and c.node_id=node_id
    and l.alert_id is null
    group by a.protocol_id
    having min(case when c.isIntersect=(
    (intlist is not null and trees.comparisonIntArray(c.listType,$3,$4,$10,$5,c.framemin,c.framemax,$6)&&c.intList)
    or
    (strlist is not null and trees.comparisonStrArray(c.listType,$5,c.framemin,c.framemax,$6,$7)&&c.strList)
    )
    then 1 else 0 end)=1
    ) sub inner join trees.protocol x on sub.protocol_id=x.protocol_id
    inner join public.alert_config d on d.rule_id=sub.protocol_id and d.customer_id=$6 and d.validation_status>0
    left outer join trees.labEval y on x.protocol_id=y.protocol_id
    where (y.protocol_id is null or trees.evalLabs($6,$5,y.framemin,y.framemax,y.defaultval,y.relation,y.threshold,y.loinc_codes,y.onlychecklast))'

    using patAge, patSex, encSnomeds, probSnomeds, patid, customer, curMedList, prov_id, enc_id, histsnomeds;
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION trees.evalnode(integer, numeric, character varying, bigint[], bigint[], bigint[], character varying, integer, character varying[], character varying, character varying)
  OWNER TO maven;