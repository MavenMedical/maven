ALTER TABLE trees.codelist RENAME protocol_id TO canonical_id;

-- Function: trees.insertprotocol(json, integer, integer, character varying, character varying, numeric, numeric, character varying)
DROP FUNCTION trees.insertprotocol(json, integer, integer, character varying, character varying, numeric, numeric, character varying);
CREATE OR REPLACE FUNCTION trees.insertprotocol(fullspec json, custid_in integer, userid_in integer, name_in character varying, folder_in character varying DEFAULT ''::character varying, minage_in numeric DEFAULT 0, maxage_in numeric DEFAULT 200, sex_in character varying DEFAULT '%'::character varying)
  RETURNS integer[] AS
$BODY$
declare
	 v_pathid int;
	 v_canonicalid int;
begin
	 SELECT nextval('protocol_id_seq') INTO v_pathid;
	 SELECT nextval('canonical_protocol_id_seq') INTO v_canonicalid;
	 INSERT INTO trees.protocol (protocol_id, customer_id,creator,minage,maxage,sex,full_spec, canonical_id)
		VALUES(v_pathid,custid_in,userid_in,minage_in,maxage_in,sex_in,fullspec,v_canonicalid);
	 INSERT INTO trees.canonical_protocol (canonical_id,name,customer_id,current_id,folder)
		VALUES(v_canonicalid,name_in,custid_in,v_pathid,folder_in);
	 return ARRAY[v_pathid, v_canonicalid];
--exception when others then
--        return -1;
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION trees.insertprotocol(json, integer, integer, character varying, character varying, numeric, numeric, character varying)
  OWNER TO maven;


-- Function: trees.updateprotocol(integer, json, integer, integer, numeric, numeric, character varying)
DROP FUNCTION trees.updateprotocol(integer, json, integer, integer, numeric, numeric, character varying);
CREATE OR REPLACE FUNCTION trees.updateprotocol(pathid_in integer, fullspec_in json, custid_in integer, userid_in integer, minage_in numeric DEFAULT 0, maxage_in numeric DEFAULT 200, sex_in character varying DEFAULT '%'::character varying)
  RETURNS integer[] AS
$BODY$
declare
	v_pathid int;
	v_canonicalid int;
begin
	SELECT nextval('protocol_id_seq') into v_pathid;
	INSERT INTO trees.protocol(protocol_id, customer_id, creator, minage, maxage, sex, full_spec, canonical_id, parent_id, tags)
	       (SELECT v_pathid, custid_in, userid_in, minage_in, maxage_in, sex_in, fullspec_in, canonical_id, protocol_id, tags FROM trees.protocol AS p WHERE p.protocol_id=pathid_in AND p.customer_id=custid_in)
	       RETURNING canonical_id INTO v_canonicalid;
	-- UPDATE trees.canonical_protocol SET current_id=v_pathid WHERE customer_id=custid_in AND canonical_id=v_canonicalid;
	return ARRAY[v_pathid, v_canonicalid];
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION trees.updateprotocol(integer, json, integer, integer, numeric, numeric, character varying)
  OWNER TO maven;

-- Function: trees.upsert_codelist(integer, integer, character varying, boolean, integer[], character varying[], integer, integer)
DROP FUNCTION trees.upsert_codelist(integer, integer, character varying, boolean, integer[], character varying[], integer, integer);
CREATE OR REPLACE FUNCTION trees.upsert_codelist(v_canonical_id integer, v_node_id integer, v_listtype character varying, v_isintersect boolean, v_intlist integer[], v_strlist character varying[], v_framemin integer, v_framemax integer)
  RETURNS void AS
$BODY$
  BEGIN
    LOOP
      UPDATE trees.codelist SET intlist = (select (select array_agg(child) from terminology.conceptancestry where ancestor = ANY(v_intlist)) as bigint), strlist = v_strlist, framemin = v_framemin, framemax = v_framemax, isintersect = v_isintersect
      WHERE canonical_id = v_canonical_id AND node_id = v_node_id AND listtype = v_listtype;
      IF found THEN
        RETURN;
      END IF;
      BEGIN
        INSERT INTO trees.codelist(canonical_id, node_id, listtype, isintersect, intlist, strlist, framemin, framemax)
          VALUES (v_canonical_id, v_node_id, v_listtype, v_isintersect, (select (select array_agg(child) from terminology.conceptancestry where ancestor = ANY(v_intlist)) as bigint), v_strlist, v_framemin, v_framemax);
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