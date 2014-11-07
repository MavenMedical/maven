-- Name: trees.insertprotocol(json, numeric, character varying, character varying, numeric, numeric, character varying); Type: FUNCTION; Schema: trees; Owner: maven
CREATE OR REPLACE FUNCTION trees.insertprotocol(fullspec json, custid_in integer, userid_in integer, name_in character varying, folder_in character varying DEFAULT ''::character varying, minage_in numeric DEFAULT 0, maxage_in numeric DEFAULT 200, sex_in character varying DEFAULT '%'::character varying) RETURNS integer
     LANGUAGE plpgsql
     AS $$
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
	 return v_pathid;
--exception when others then
--        return -1;
end;
$$;
ALTER FUNCTION trees.insertprotocol(fullspec json, custid_in integer, name_in character varying, desc_in character varying, minage_in numeric, maxage_in numeric, sex_in character varying) OWNER TO maven;



CREATE OR REPLACE FUNCTION trees.updateprotocol(pathid_in integer, fullspec_in json, custid_in integer, userid_in integer, minage_in numeric DEFAULT 0, maxage_in numeric DEFAULT 200, sex_in character varying DEFAULT '%'::character varying) RETURNS integer
       LANGUAGE plpgsql
       AS $$
declare 
	v_pathid int;
	v_canonicalid int;
begin
	SELECT nextval('protocol_id_seq') into v_pathid;
	INSERT INTO trees.protocol(protocol_id, customer_id, creator, minage, maxage, sex, full_spec, canonical_id, parent_id, tags)
	       (SELECT v_pathid, custid_in, userid_in, minage_in, maxage_in, sex_in, fullspec_in, canonical_id, protocol_id, tags FROM trees.protocol AS p WHERE p.protocol_id=pathid_in AND p.customer_id=custid_in)
	       RETURNING canonical_id INTO v_canonicalid;
	UPDATE trees.canonical_protocol SET current_id=v_pathid WHERE customer_id=custid_in AND canonical_id=v_canonicalid;
	return v_pathid;
end;
$$;
ALTER FUNCTION trees.updateprotocol(pathid_in integer, fullspec_in json, custid_in integer, userid_in integer, minage_in numeric, maxage_in numeric, sex_in character varying) OWNER TO maven;
