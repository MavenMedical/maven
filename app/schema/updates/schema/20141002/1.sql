ALTER TABLE trees.protocol
  ADD COLUMN minage numeric(18,2), ADD COLUMN maxage numeric(18,2), ADD COLUMN sex character varying(1);

DROP FUNCTION trees.evalnode(character varying, character varying, numeric, character varying, bigint[], bigint[], character varying, integer, character varying[]);

CREATE OR REPLACE FUNCTION trees.evalnode(IN patage numeric, IN patsex character varying, IN encsnomeds bigint[], IN probsnomeds bigint[], IN patid character varying, IN customer integer, IN curmedlist character varying[])
  RETURNS TABLE(id numeric, name character varying, description character varying, full_spec json) AS
$BODY$
begin
                return query execute
                'select x.id,x.name,x.description,x.full_spec from
                (
                select a.id
                from trees.protocol a
                  inner join trees.codelist c on a.id=c.protocol_id
                where
                   a.minage<=$1 and a.maxage>=$1
                   and $2 like a.sex
                group by a.id
                having min(case when c.isIntersect=(
                        (intlist is not null and trees.comparisonIntArray(c.listType,$3,$4,$5,c.framemin,c.framemax,$6)&&c.intList)
                        or
                        (strlist is not null and trees.comparisonStrArray(c.listType,$5,c.framemin,c.framemax,$6,$7)&&c.strList)
                      )
                  then 1 else 0 end)=1
                ) sub inner join trees.protocol x on sub.id=x.id
                inner join public.alert_config d on d.rule_id=sub.id and d.customer_id=$6 and d.validation_status>0
                left outer join trees.labEval y on x.id=y.protocol_id
                where (y.protocol_id is null or trees.evalLabs($6,$5,y.framemin,y.framemax,y.defaultval,y.relation,y.threshold,y.loinc_codes,y.onlychecklast))'
                using patAge , patSex , encSnomeds , probSnomeds ,patid,customer,curMedList;

end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION trees.evalnode(numeric, character varying, bigint[], bigint[], character varying, integer, character varying[])
  OWNER TO maven;


