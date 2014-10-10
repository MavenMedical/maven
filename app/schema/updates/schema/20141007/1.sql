-- Function: trees.upsert_codelist(integer, integer, character varying, boolean, integer[], character varying[], integer, integer)
-- DROP FUNCTION trees.upsert_codelist(integer, integer, character varying, boolean, integer[], character varying[], integer, integer);
CREATE OR REPLACE FUNCTION trees.upsert_codelist(v_protocol_id integer, v_node_id integer, v_listtype character varying, v_isintersect boolean, v_intlist integer[], v_strlist character varying[], v_framemin integer, v_framemax integer)
  RETURNS void AS
$BODY$
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
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION trees.upsert_codelist(integer, integer, character varying, boolean, integer[], character varying[], integer, integer)
  OWNER TO maven;



DROP FUNCTION IF EXISTS trees.evalnode(numeric, character varying, bigint[], bigint[], character varying, integer, character varying[]);
-- Function: trees.evalnode(integer, numeric, character varying, bigint[], bigint[], character varying, integer, character varying[])
-- DROP FUNCTION trees.evalnode(integer, numeric, character varying, bigint[], bigint[], character varying, integer, character varying[]);
CREATE OR REPLACE FUNCTION trees.evalnode(IN node_id integer, IN patage numeric, IN patsex character varying, IN encsnomeds bigint[], IN probsnomeds bigint[], IN patid character varying, IN customer integer, IN curmedlist character varying[])
    RETURNS TABLE(id integer, name character varying, description character varying, full_spec json) AS
$BODY$
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
$BODY$
LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION trees.evalnode(integer, numeric, character varying, bigint[], bigint[], character varying, integer, character varying[])
  OWNER TO maven;


DROP FUNCTION IF EXISTS trees.insertprotocol(json, numeric, character varying, character varying, numeric, numeric, character varying);
create or replace function trees.insertProtocol(fullspec json,custid_in numeric(18,0),name_in varchar(100),desc_in varchar(1000) default ''
    ,minage_in numeric(18,2) default 0,maxage_in numeric(18,2) default 200, sex_in varchar(1) default '%')
returns integer
as
$$
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
$$ language plpgsql;