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
	return ARRAY[v_pathid, v_canonicalid];
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION trees.updateprotocol(integer, json, integer, integer, numeric, numeric, character varying)
  OWNER TO maven;
