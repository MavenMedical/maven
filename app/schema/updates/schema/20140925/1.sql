-- Function: upsert_alert_config(numeric, numeric, character varying, integer, integer, character varying[])

-- DROP FUNCTION upsert_alert_config(numeric, numeric, character varying, integer, integer, character varying[])

CREATE OR REPLACE FUNCTION upsert_alert_config(v_customer_id numeric,
                                               v_department numeric,
                                               v_category character varying,
                                               v_rule_id integer,
                                               v_validation_status integer,
                                               v_provide_optouts character varying[])
  RETURNS void AS
$BODY$
  BEGIN
    LOOP
      UPDATE alert_config SET validation_status = v_validation_status WHERE category = v_category AND customer_id = v_customer_id;
      IF found THEN
        RETURN;
      END IF;
      BEGIN
        INSERT INTO alert_config(customer_id, department, category, rule_id, validation_status, provide_optouts)
          VALUES (v_customer_id, v_department, v_category, v_rule_id, v_validation_status, v_provide_optouts);
        RETURN;
      EXCEPTION WHEN unique_violation THEN
      END;
    END LOOP;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION upsert_alert_config(numeric, numeric, character varying, integer, integer, character varying[])
  OWNER TO maven;