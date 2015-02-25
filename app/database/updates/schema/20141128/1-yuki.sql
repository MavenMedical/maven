-- Function: get_log_tags(character varying[])
-- DROP FUNCTION get_log_tags(character varying[]);
CREATE OR REPLACE FUNCTION get_log_tags(v_tags character varying[])
  RETURNS integer[] AS
$BODY$
    declare rtnids integer[];
            rtnid integer;
            tag_str character varying;
BEGIN
  FOREACH tag_str in ARRAY v_tags
    LOOP
      LOOP
        SELECT value into rtnid from categories.log_tag
          WHERE name=tag_str;
        IF found THEN
          exit;
        END IF;
        BEGIN
          INSERT INTO categories.log_tag(name)
            VALUES (tag_str) returning value into rtnid;
        EXCEPTION WHEN unique_violation THEN
        END;
      END LOOP;
      select array_append(rtnids, rtnid) into rtnids;
    END LOOP;
    return rtnids;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION get_log_tags(character varying[])
  OWNER TO maven;