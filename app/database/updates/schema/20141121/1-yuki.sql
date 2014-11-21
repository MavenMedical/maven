ALTER TABLE composition ADD COLUMN datetime_inserted timestamp without time zone;

ALTER TABLE encounter ADD COLUMN last_modified timestamp without time zone;

DROP FUNCTION upsert_encounter(character varying, character varying, character varying, date, character varying, character varying, numeric, date, date, integer);
-- Function: upsert_encounter(character varying, character varying, character varying, date, character varying, character varying, numeric, date, date, integer, timestamp without time zone)
-- DROP FUNCTION upsert_encounter(character varying, character varying, character varying, date, character varying, character varying, numeric, date, date, integer, timestamp without time zone);
CREATE OR REPLACE FUNCTION upsert_encounter(v_csn character varying, v_patient_id character varying, v_enc_type character varying, v_contact_date date, v_visit_prov_id character varying, v_bill_prov_id character varying, v_department_id numeric, v_hosp_admsn_time date, v_hosp_disch_time date, v_customer_id integer, v_last_modified timestamp without time zone)
  RETURNS void AS
$BODY$
BEGIN
  LOOP
    UPDATE encounter SET patient_id = v_patient_id, enc_type = v_enc_type, contact_date = v_contact_date,
      visit_prov_id = v_visit_prov_id, bill_prov_id = v_bill_prov_id, department_id = v_department_id, last_modified = v_last_modified,
      hosp_admsn_time = v_hosp_admsn_time, hosp_disch_time = v_hosp_disch_time WHERE csn = v_csn AND customer_id = v_customer_id;
    IF found THEN
      RETURN;
    END IF;
    BEGIN
      INSERT INTO encounter(csn, patient_id, enc_type, contact_date, visit_prov_id, bill_prov_id, department_id, hosp_admsn_time, hosp_disch_time, customer_id, last_modified)
        VALUES (v_csn, v_patient_id, v_enc_type, v_contact_date, v_visit_prov_id, v_bill_prov_id, v_department_id, v_hosp_admsn_time, v_hosp_disch_time, v_customer_id, v_last_modified);
      RETURN;
    EXCEPTION WHEN unique_violation THEN
    END;
  END LOOP;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION upsert_encounter(character varying, character varying, character varying, date, character varying, character varying, numeric, date, date, integer, timestamp without time zone)
  OWNER TO maven;
