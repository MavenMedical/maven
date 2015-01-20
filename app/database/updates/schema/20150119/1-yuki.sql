ALTER TABLE trees.codelist ADD COLUMN disjunctiveGroupID INTEGER;

DROP FUNCTION trees.upsert_codelist(integer, integer, character varying, boolean, integer[], character varying[], integer, integer);
-- Function: trees.upsert_codelist(integer, integer, character varying, boolean, integer[], character varying[], integer, integer, integer)
-- DROP FUNCTION trees.upsert_codelist(integer, integer, character varying, boolean, integer[], character varying[], integer, integer, integer);
CREATE OR REPLACE FUNCTION trees.upsert_codelist(v_canonical_id integer, v_node_id integer, v_listtype character varying, v_isintersect boolean, v_intlist integer[], v_strlist character varying[], v_framemin integer, v_framemax integer, v_disgroupid integer)
  RETURNS void AS
$BODY$
  BEGIN
    LOOP
      if v_listtype='membership' THEN
         UPDATE trees.codelist SET intlist = v_intlist::bigint[], strlist = v_strlist, framemin = v_framemin, framemax = v_framemax, isintersect = v_isintersect, disjunctivegroupid = v_disgroupid
         WHERE canonical_id = v_canonical_id AND node_id = v_node_id AND listtype = v_listtype;
         IF found THEN
           RETURN;
         END IF;
         BEGIN
           INSERT INTO trees.codelist(canonical_id, node_id, listtype, isintersect, intlist, strlist, framemin, framemax, disjunctivegroupid)
             VALUES (v_canonical_id, v_node_id, v_listtype, v_isintersect, v_intlist::bigint[], v_strlist, v_framemin, v_framemax, v_disgroupid);
           RETURN;
         EXCEPTION WHEN unique_violation THEN
         END;
      ELSE
        UPDATE trees.codelist SET intlist = (select (select array_agg(child) from terminology.conceptancestry where ancestor = ANY(v_intlist)) as bigint), strlist = v_strlist, framemin = v_framemin, framemax = v_framemax, isintersect = v_isintersect, disjunctivegroupid = v_disgroupid
        WHERE canonical_id = v_canonical_id AND node_id = v_node_id AND listtype = v_listtype;
        IF found THEN
          RETURN;
        END IF;
        BEGIN
          INSERT INTO trees.codelist(canonical_id, node_id, listtype, isintersect, intlist, strlist, framemin, framemax, disjunctivegroupid)
            VALUES (v_canonical_id, v_node_id, v_listtype, v_isintersect, (select (select array_agg(child) from terminology.conceptancestry where ancestor = ANY(v_intlist)) as bigint), v_strlist, v_framemin, v_framemax, v_disgroupid);
          RETURN;
        EXCEPTION WHEN unique_violation THEN
        END;
      END IF;
    END LOOP;
  END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION trees.upsert_codelist(integer, integer, character varying, boolean, integer[], character varying[], integer, integer, integer)
  OWNER TO maven;


DROP FUNCTION trees.evalnode(integer, numeric, character varying, bigint[], bigint[], bigint[], character varying, integer, character varying[], character varying, character varying, character varying[]);

-- Function: trees.evalnode(integer, numeric, character varying, bigint[], bigint[], bigint[], character varying, integer, character varying[], character varying, character varying, character varying[])
-- DROP FUNCTION trees.evalnode(integer, numeric, character varying, bigint[], bigint[], bigint[], character varying, integer, character varying[], character varying, character varying, character varying[]);
CREATE OR REPLACE FUNCTION trees.evalnode(IN node_id integer, IN patage numeric, IN patsex character varying, IN encsnomeds bigint[], IN probsnomeds bigint[], IN histsnomeds bigint[], IN patid character varying, IN customer integer, IN curmedlist character varying[], IN prov_id character varying, IN enc_id character varying, IN prochistry character varying[])
  RETURNS TABLE(id integer, name character varying, description character varying, full_spec CHARACTER varying, priority integer, listtype CHARACTER VARYING, nodeid INTEGER, disjuncgrpid INTEGER, isintersect BOOLEAN, intlist BIGINT[], strlist CHARACTER VARYING[], intintersect BOOLEAN, strintersect BOOLEAN) AS
$BODY$
begin
return query execute
'SELECT
  x.protocol_id,
  sub.name,
  x.description,
  x.full_spec::CHARACTER VARYING,
  d.priority,
  sub.listtype,
  sub.node_id,
  sub.disjunctivegroupid,
  sub.isintersect,
  sub.intlist,
  sub.strlist,
  trees.comparisonIntArray(sub.listType,$3,$4,$10,$5,sub.framemin,sub.framemax,$6)&&sub.intList,
  trees.comparisonStrArray(sub.listType,$5,sub.framemin,sub.framemax,$6,$7,$11)&&sub.strList
FROM (
       SELECT
         cp.current_id,
         cp.canonical_id,
         cp.name,
         c.listtype,
         c.node_id,
         c.disjunctivegroupid,
         c.isintersect,
         c.intlist,
         c.strlist,
         c.framemin,
         c.framemax
       FROM trees.canonical_protocol cp
         INNER JOIN trees.protocol a ON cp.current_id = a.protocol_id
         LEFT OUTER JOIN trees.codelist c ON a.canonical_id = c.canonical_id
         LEFT OUTER JOIN public.alert l ON a.customer_id = l.customer_id AND a.protocol_id = l.cds_rule AND
                                           l.provider_id= $8 AND l.patient_id = $5 AND
                                           l.encounter_id = $9
       WHERE cp.enabled
        and a.minage<=$1 and a.maxage>=$1
        and $2 like a.sex
        and c.node_id=node_id
        and l.alert_id is null
        and not cp.deleted
       GROUP BY c.disjunctivegroupid, cp.current_id, cp.canonical_id, cp.name, c.listtype, c.node_id, c.isintersect,
         c.intlist, c.strlist, c.framemin, c.framemax
       ORDER BY cp.canonical_id DESC, c.disjunctivegroupid ASC
     )
     sub INNER JOIN trees.protocol x ON sub.current_id = x.protocol_id
     INNER JOIN public.alert_config d ON d.rule_id=sub.canonical_id AND d.customer_id=$6 AND d.validation_status>0
     GROUP BY x.protocol_id, sub.name, x.description, d.priority, sub.canonical_id, sub.current_id, sub.listtype, sub.node_id, sub.disjunctivegroupid, sub.isintersect,
       sub.intlist, sub.strlist, sub.framemin, sub.framemax, x.full_spec::CHARACTER VARYING,
       trees.comparisonIntArray(sub.listType,$3,$4,$10,$5,sub.framemin,sub.framemax,$6)&&sub.intList,
       trees.comparisonStrArray(sub.listType,$5,sub.framemin,sub.framemax,$6,$7,$11)&&sub.strList
  ORDER BY sub.canonical_id DESC, sub.disjunctivegroupid ASC;'
  using patAge, patSex, encSnomeds, probSnomeds, patid, customer, curMedList, prov_id, enc_id, histsnomeds, prochistry;
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION trees.evalnode(integer, numeric, character varying, bigint[], bigint[], bigint[], character varying, integer, character varying[], character varying, character varying, character varying[])
  OWNER TO maven;