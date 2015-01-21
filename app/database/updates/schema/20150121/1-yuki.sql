-- Function: upsert_historic_order(integer, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, numeric, timestamp without time zone)
-- DROP FUNCTION upsert_historic_order(integer, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, numeric, timestamp without time zone);
CREATE OR REPLACE FUNCTION upsert_historic_order(v_customer_id integer, v_order_id character varying, v_patient_id character varying, v_encounter_id character varying, v_ordering_provider_id character varying, v_auth_provider_id character varying, v_orderable_id character varying, v_status character varying, v_source character varying, v_code_id character varying, v_code_system character varying, v_order_name character varying, v_order_type character varying, v_order_cost numeric, v_order_datetime timestamp without time zone)
  RETURNS void AS
$BODY$
    DECLARE exit_loop Boolean:=FALSE;
BEGIN
  LOOP
    IF exit_loop = TRUE THEN
      EXIT;
    END IF;
    UPDATE order_ord
    SET
      status = v_status
    WHERE customer_id = v_customer_id AND patient_id = v_patient_id AND code_id = v_code_id AND code_system = v_code_system AND order_datetime = v_order_datetime AND NOT (status = v_status);
     IF found THEN
       INSERT INTO order_event(
            customer_id, order_id, provider_id, order_event, event_datetime,
            source, active_orders)
         VALUES (v_customer_id, v_order_id, v_patient_id, v_status, v_order_datetime,
                v_source, NULL);
       exit_loop = TRUE;
       EXIT;
     END IF;

    UPDATE order_ord
      SET
        status = v_status
    WHERE patient_id = v_patient_id AND customer_id = v_customer_id AND code_id = v_code_id AND code_system = v_code_system AND order_datetime = v_order_datetime AND status = v_status;
    IF found THEN
      exit_loop = TRUE;
      EXIT;
    END IF;

    BEGIN
        INSERT INTO order_ord(customer_id, order_id, patient_id, encounter_id, ordering_provider_id,
                              auth_provider_id, orderable_id, status, source, code_id, code_system,
                              order_name, order_type, order_cost, order_datetime)
          VALUES (v_customer_id, v_order_id, v_patient_id, v_encounter_id, v_ordering_provider_id,
                  v_auth_provider_id, v_orderable_id, v_status, v_source, v_code_id, v_code_system,
                  v_order_name, v_order_type, v_order_cost, v_order_datetime);
        INSERT INTO order_event(
              customer_id, order_id, provider_id, order_event, event_datetime,
              source, active_orders)
           VALUES (v_customer_id, v_order_id, v_auth_provider_id, v_status, v_order_datetime,
                  v_source, NULL);
        exit_loop = TRUE;
        RETURN;
        EXCEPTION WHEN unique_violation THEN
          END;
  END LOOP;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION upsert_historic_order(integer, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, numeric, timestamp without time zone)
  OWNER TO maven;