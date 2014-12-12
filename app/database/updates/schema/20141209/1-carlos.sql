-- Function: trees.insertprotocol(json, integer, integer, character varying, character varying, numeric, numeric, character varying, integer, integer)
DROP FUNCTION trees.insertprotocol(json, integer, integer, character varying, character varying, numeric, numeric, character varying);
CREATE OR REPLACE FUNCTION trees.insertprotocol(fullspec json, custid_in integer, userid_in integer, name_in character varying, folder_in character varying DEFAULT ''::character varying, minage_in numeric DEFAULT 0, maxage_in numeric DEFAULT 200, sex_in character varying DEFAULT '%'::character varying, parent_canonical integer DEFAULT 0, parent_path integer DEFAULT 0)
  RETURNS integer[] AS
$BODY$
declare
	 v_pathid int;
	 v_canonicalid int;
begin
	 SELECT nextval('protocol_id_seq') INTO v_pathid;
	 SELECT nextval('canonical_protocol_id_seq') INTO v_canonicalid;
	 INSERT INTO trees.protocol (protocol_id, customer_id,creator,minage,maxage,sex,full_spec, canonical_id, parent_id)
		VALUES(v_pathid,custid_in,userid_in,minage_in,maxage_in,sex_in,fullspec,v_canonicalid, parent_path);
	 INSERT INTO trees.canonical_protocol (canonical_id,name,customer_id,current_id, parent_id, folder)
		VALUES(v_canonicalid,name_in,custid_in,v_pathid,parent_canonical,folder_in);
	 return ARRAY[v_pathid, v_canonicalid];
--exception when others then
--        return -1;
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION trees.insertprotocol(json, integer, integer, character varying, character varying, numeric, numeric, character varying, integer, integer)
  OWNER TO maven;