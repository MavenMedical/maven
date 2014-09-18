-- Function: upsert_user(numeric, character varying, character varying, character varying, character varying, userstate, userstate, integer[], user_role[])

-- DROP FUNCTION upsert_user(numeric, character varying, character varying, character varying, character varying, userstate, userstate, integer[], user_role[]);

CREATE OR REPLACE FUNCTION upsert_user(v_customer_id numeric,
                                       v_prov_id character varying,
                                       v_user_name character varying,
                                       v_official_name character varying,
                                       v_display_name character varying,
                                       v_state userstate,
                                       v_ehr_state userstate,
                                       v_layouts integer[],
                                       v_roles user_role[])
  RETURNS void AS
  $BODY$
  BEGIN
    LOOP
      UPDATE users SET prov_id = v_prov_id, display_name = v_display_name, state = v_state, layouts = v_layouts,
        roles = v_roles, ehr_state = v_ehr_state WHERE user_name = v_user_name AND customer_id = v_customer_id;
      IF found THEN
        RETURN;
      END IF;
      BEGIN
        INSERT INTO users(customer_id, prov_id, user_name, official_name, display_name, state, layouts, roles, ehr_state)
          VALUES (v_customer_id, v_prov_id, v_user_name, v_official_name, v_display_name, v_state, v_layouts, v_roles, v_ehr_state);
        RETURN;
      EXCEPTION WHEN unique_violation THEN
      END;
    END LOOP;
  END;
  $BODY$
    LANGUAGE plpgsql VOLATILE
    COST 100;
  ALTER FUNCTION upsert_user(numeric,
                             character varying,
                             character varying,
                             character varying,
                             character varying,
                             userstate,
                             userstate,
                             integer[],
                             user_role[])
    OWNER TO maven;