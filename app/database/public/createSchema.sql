\connect maven;
/**
**************
**************
TABLES IN PUBLIC SCHEMA
**************
**************
*/
-- Name: adt; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE adt (
    event_id character varying(100),
    customer_id integer,
    patient_id character varying(100),
    encounter_id character varying(100),
    prov_id character varying(18),
    event_type character varying(25),
    event_time timestamp without time zone,
    dep_id numeric(18,0),
    room_id character varying(25)
);
ALTER TABLE public.adt OWNER TO maven;

-- Name: alert; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE alert (
    alert_id serial NOT NULL,
    alert_uuid character varying(36),
    customer_id integer,
    provider_id character varying(18),
    patient_id character varying(100),
    encounter_id character varying(100),
    category character varying(255),
    status character varying(255),
    order_id character varying(36),
    order_base_cost numeric(18,2),
    code_trigger character varying(36),
    code_trigger_type character varying(255),
    cds_rule integer,
    alert_datetime timestamp without time zone,
    short_title character varying(255),
    long_title character varying,
    short_description character varying(255),
    long_description character varying,
    outcome character varying(255),
    saving numeric(18,2),
    validation_status integer
);
ALTER TABLE public.alert OWNER TO maven;

-- Name: alert_config; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE alert_config (
    customer_id integer,
    department numeric(18,0),
    category character varying(36),
    rule_id integer,
    validation_status integer,
    provide_optouts character varying(36)[]
);
ALTER TABLE public.alert_config OWNER TO maven;

-- Name: alert_setting_hist; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE alert_setting_hist (
    alert_id numeric(18,0),
    user_id integer NOT NULL,
    customer_id integer,
    datetime timestamp without time zone,
    category character varying(36),
    subcategory character varying(36),
    rule_id integer,
    scope character varying(36),
    action character varying(36),
    action_comment character varying(255)
);
ALTER TABLE public.alert_setting_hist OWNER TO maven;

-- Name: audit; Type: TABLE; Schema: public; Owner: postgres; Tablespace:
CREATE TABLE audit (
    audit_id serial NOT NULL,
    datetime timestamp without time zone NOT NULL,
    username character varying NOT NULL,
    customer_id integer NOT NULL,
    patient character varying,
    action character varying NOT NULL,
    device character varying,
    details character varying,
    rows integer,
    target_user character varying
);
ALTER TABLE public.audit OWNER TO maven;

-- Name: composition; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE composition (
    comp_id serial NOT NULL,
    patient_id character varying(100),
    customer_id integer,
    comp_body json,
    encounter_id character varying(100)
);
ALTER TABLE public.composition OWNER TO maven;

-- Name: condition; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE condition (
    customer_id integer,
    patient_id character varying(100),
    encounter_id character varying(100),
    dx_category character varying(25),
    status character varying(25),
    date_asserted timestamp without time zone,
    date_resolved timestamp without time zone,
    snomed_id bigint,
    dx_code_id character varying(25),
    dx_code_system character varying(255),
    dx_text character varying,
    is_principle boolean,
    is_chronic boolean,
    is_poa boolean
);
ALTER TABLE public.condition OWNER TO maven;

-- Name: customer; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE customer (
    customer_id serial NOT NULL,
    name character(255) NOT NULL,
    abbr character varying(22),
    license_type numeric(9,0),
    license_exp date,
    clientapp_config character varying,
    clientapp_settings character varying
);
ALTER TABLE public.customer OWNER TO maven;

--Add the default Maven Customer so that the support user can be activated

INSERT INTO CUSTOMER (customer_id, name) VALUES (0, 'Maven');

-- Name: department; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE department (
    department_id numeric(18,0) NOT NULL,
    customer_id integer,
    dep_name character varying(100),
    specialty character varying(50),
    location character varying(100)
);
ALTER TABLE public.department OWNER TO maven;

-- Name: encounter; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE encounter (
    csn character varying(100) NOT NULL,
    customer_id integer,
    patient_id character varying(100),
    enc_type character varying(254),
    contact_date date,
    visit_prov_id character varying(18),
    bill_prov_id character varying(18),
    department_id numeric(18,0),
    hosp_admsn_time date,
    hosp_disch_time date
);
ALTER TABLE public.encounter OWNER TO maven;

-- Name: layouts; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE layouts (
    id serial NOT NULL,
    layout_id integer,
    widget character varying(36),
    template character varying(36),
    element character varying(36),
    priority integer
);
ALTER TABLE public.layouts OWNER TO maven;

-- Name: logins; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE logins (
    user_name character varying(100),
    method character varying(36),
    logintime timestamp without time zone,
    ip inet,
    environment text,
    authkey character varying(64),
    customer_id integer NOT NULL
);
ALTER TABLE public.logins OWNER TO maven;

-- Name: observable; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE observable (
    customer_id integer,
    name character varying(255),
    status character varying(255),
    orderable_id character varying(36),
    cpt_code character varying(20),
    loinc_code character varying(254),
    snomed_id bigint,
    code_id character varying(254),
    code_system character varying(254),
    epic_comp_id numeric(18,0),
    epic_ext_name character varying(75),
    epic_base_name character varying(75),
    epic_common_name character varying(254)
);
ALTER TABLE public.observable OWNER TO maven;

-- Name: observation; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE observation (
    customer_id integer,
    encounter_id character varying(100),
    order_id character varying(36),
    patient_id character varying(100),
    status character varying(254),
    result_time timestamp without time zone,
    comments character varying(254),
    numeric_result double precision,
    units character varying(254),
    reference_low double precision,
    reference_high double precision,
    reference_unit character varying(100),
    method character varying(265),
    loinc_code character varying(254),
    snomed_id bigint,
    code_id character varying(254),
    code_system character varying(254),
    name character varying(254),
    component_id numeric(18,0),
    external_name character varying(75),
    base_name character varying(75),
    common_name character varying(254)
);
ALTER TABLE public.observation OWNER TO maven;

-- Name: order_event; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE order_event (
    customer_id integer,
    encounter_id character varying(100),
    order_id character varying(36),
    provider_id character varying(100),
    order_event character varying(2),
    event_datetime timestamp without time zone,
    source character varying(255),
    active_orders character varying
);
ALTER TABLE public.order_event OWNER TO maven;

-- Name: order_ord; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE order_ord (
    customer_id integer,
    order_id character varying(36),
    patient_id character varying(100),
    encounter_id character varying(100),
    ordering_provider_id character varying(18),
    auth_provider_id character varying(18),
    orderable_id character varying(36),
    status character varying(255),
    source character varying(255),
    code_id character varying(36),
    code_system character varying(255),
    order_name character varying(255),
    order_type character varying(255),
    order_cost numeric(18,2),
    order_cost_type character varying(255),
    order_datetime timestamp without time zone
);
ALTER TABLE public.order_ord OWNER TO maven;

-- Name: orderable; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE orderable (
    customer_id integer,
    orderable_id character varying(36),
    ord_type character varying(36),
    system character varying(255),
    name character varying(255),
    description character varying,
    status character varying(255),
    source character varying(255),
    cpt_code character varying(20),
    cpt_version character varying(20),
    proc_rvu_work_comp numeric(18,2),
    proc_rvu_overhd_comp numeric(18,2),
    proc_rvu_malprac_comp numeric(18,2),
    proc_rvu_total_no_mod numeric(18,2),
    rx_rxnorm_id character varying(20),
    rx_generic_name character varying(255),
    rx_strength character varying(20),
    rx_form character varying(20),
    rx_route character varying(20),
    rx_thera_class character varying(20),
    rx_pharm_class character varying(20),
    rx_pharm_subclass character varying(20),
    rx_simple_generic character varying(255)
);
ALTER TABLE public.orderable OWNER TO maven;

-- Name: override_indication; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE override_indication (
    override_id serial NOT NULL,
    customer_id integer,
    sleuth_rule integer,
    category character varying(255),
    name character varying(25),
    description character varying(255)
);
ALTER TABLE public.override_indication OWNER TO maven;

-- Name: patient; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE patient (
    patient_id character varying(100) NOT NULL,
    customer_id integer,
    birth_month character varying(6),
    birthdate date,
    sex character varying(254),
    mrn character varying(100),
    patname character varying(100),
    cur_pcp_prov_id character varying(18)
);
ALTER TABLE public.patient OWNER TO maven;

-- Name: provider; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE provider (
    prov_id character varying(18) NOT NULL,
    customer_id integer,
    prov_name character varying(100),
    specialty character varying(254),
    specialty2 character varying(254)
);
ALTER TABLE public.provider OWNER TO maven;

-- Name: shared_bytes; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE shared_bytes (
    shared bytea,
    created_on time without time zone
);
ALTER TABLE public.shared_bytes OWNER TO maven;

-- Name: user_pref; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE user_pref (
    customer_id integer NOT NULL,
    user_name character varying(100),
    notify_primary character varying(32),
    notify_secondary character varying(32)
);
ALTER TABLE public.user_pref OWNER TO maven;

-- Name: users; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE users (
    user_id serial NOT NULL,
    customer_id integer,
    prov_id character varying(18),
    user_name character varying(100),
    official_name character varying(100),
    display_name character varying(100),
    pw bytea,
    pw_expiration timestamp without time zone,
    old_passwords bytea[],
    state character varying(36),
    layouts integer[],
    roles character varying(36)[],
    ehr_state character varying(36),
    profession character varying(255)
);
ALTER TABLE public.users OWNER TO maven;

/**
**************
**************
TEXT SEARCH
**************
**************
*/
-- Name: maven; Type: TEXT SEARCH DICTIONARY; Schema: public; Owner: postgres
CREATE TEXT SEARCH DICTIONARY maven (
    TEMPLATE = pg_catalog.simple,
    stopwords = 'english' );
ALTER TEXT SEARCH DICTIONARY public.maven OWNER TO postgres;

-- Name: maven; Type: TEXT SEARCH CONFIGURATION; Schema: public; Owner: postgres
CREATE TEXT SEARCH CONFIGURATION maven (
    PARSER = pg_catalog."default" );
ALTER TEXT SEARCH CONFIGURATION maven
    ADD MAPPING FOR asciiword WITH maven;
ALTER TEXT SEARCH CONFIGURATION maven
    ADD MAPPING FOR word WITH english_stem;
ALTER TEXT SEARCH CONFIGURATION maven
    ADD MAPPING FOR numword WITH simple;
ALTER TEXT SEARCH CONFIGURATION maven
    ADD MAPPING FOR email WITH simple;
ALTER TEXT SEARCH CONFIGURATION maven
    ADD MAPPING FOR url WITH simple;
ALTER TEXT SEARCH CONFIGURATION maven
    ADD MAPPING FOR host WITH simple;
ALTER TEXT SEARCH CONFIGURATION maven
    ADD MAPPING FOR sfloat WITH simple;
ALTER TEXT SEARCH CONFIGURATION maven
    ADD MAPPING FOR version WITH simple;
ALTER TEXT SEARCH CONFIGURATION maven
    ADD MAPPING FOR hword_numpart WITH simple;
ALTER TEXT SEARCH CONFIGURATION maven
    ADD MAPPING FOR hword_part WITH english_stem;
ALTER TEXT SEARCH CONFIGURATION maven
    ADD MAPPING FOR hword_asciipart WITH english_stem;
ALTER TEXT SEARCH CONFIGURATION maven
    ADD MAPPING FOR numhword WITH simple;
ALTER TEXT SEARCH CONFIGURATION maven
    ADD MAPPING FOR asciihword WITH english_stem;
ALTER TEXT SEARCH CONFIGURATION maven
    ADD MAPPING FOR hword WITH english_stem;
ALTER TEXT SEARCH CONFIGURATION maven
    ADD MAPPING FOR url_path WITH simple;
ALTER TEXT SEARCH CONFIGURATION maven
    ADD MAPPING FOR file WITH simple;
ALTER TEXT SEARCH CONFIGURATION maven
    ADD MAPPING FOR "float" WITH simple;
ALTER TEXT SEARCH CONFIGURATION maven
    ADD MAPPING FOR "int" WITH simple;
ALTER TEXT SEARCH CONFIGURATION maven
    ADD MAPPING FOR uint WITH simple;
ALTER TEXT SEARCH CONFIGURATION public.maven OWNER TO postgres;

SET search_path = categories, pg_catalog;
SET default_tablespace = '';
SET default_with_oids = false;

/**
**************
**************
FUNCTIONS IN PUBLIC SCHEMA
**************
**************
*/
-- Name: upsert_alert_config(numeric, numeric, character varying, integer, integer, character varying[]); Type: FUNCTION; Schema: public; Owner: maven
CREATE OR REPLACE FUNCTION public.upsert_alert_config(v_customer_id integer, v_department numeric, v_category character varying, v_rule_id integer, v_validation_status integer, v_provide_optouts character varying[]) RETURNS void
    LANGUAGE plpgsql
    AS $$
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
  $$;
ALTER FUNCTION public.upsert_alert_config(v_customer_id integer, v_department numeric, v_category character varying, v_rule_id integer, v_validation_status integer, v_provide_optouts character varying[]) OWNER TO maven;

-- Name: upsert_condition(character varying, numeric, character varying, character varying, character varying, timestamp without time zone, timestamp without time zone, numeric, character varying, character varying, character varying, boolean, boolean, boolean); Type: FUNCTION; Schema: public; Owner: maven
CREATE OR REPLACE FUNCTION public.upsert_condition(v_patient_id character varying, v_customer_id integer, v_encounter_id character varying, v_dx_category character varying, v_status character varying, v_date_asserted timestamp without time zone, v_date_resolved timestamp without time zone, v_snomed_id numeric, v_dx_code character varying, v_dx_code_system character varying, v_dx_text character varying, v_is_principle boolean, v_is_chronic boolean, v_is_poa boolean) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
  LOOP
    UPDATE condition
    SET dx_category=v_dx_category,
      status=v_status,
      date_asserted=v_date_asserted,
      date_resolved=v_date_resolved,
      dx_text=v_dx_text,
      is_principle=v_is_principle,
      is_chronic=v_is_chronic,
      is_poa=v_is_poa
       WHERE encounter_id=v_encounter_id AND customer_id=v_customer_id AND (snomed_id=v_snomed_id OR (dx_code_id=v_dx_code AND dx_code_system=v_dx_code_system));
    IF found THEN
      RETURN;
    END IF;
    BEGIN
      INSERT INTO condition(
            patient_id, customer_id, encounter_id, dx_category, status, date_asserted,
            date_resolved, snomed_id, dx_code_id, dx_code_system, dx_text,
            is_principle, is_chronic, is_poa)
        VALUES (v_patient_id, v_customer_id, v_encounter_id, v_dx_category, v_status, v_date_asserted,
            v_date_resolved, v_snomed_id, v_dx_code, v_dx_code_system, v_dx_text,
            v_is_principle, v_is_chronic, v_is_poa);
      RETURN;
    EXCEPTION WHEN unique_violation THEN
    END;
  END LOOP;
END;
$$;
ALTER FUNCTION public.upsert_condition(v_patient_id character varying, v_customer_id integer, v_encounter_id character varying, v_dx_category character varying, v_status character varying, v_date_asserted timestamp without time zone, v_date_resolved timestamp without time zone, v_snomed_id numeric, v_dx_code character varying, v_dx_code_system character varying, v_dx_text character varying, v_is_principle boolean, v_is_chronic boolean, v_is_poa boolean) OWNER TO maven;

-- Name: upsert_enc_order(numeric, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, numeric, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: maven
CREATE OR REPLACE FUNCTION public.upsert_enc_order(v_customer_id integer, v_order_id character varying, v_patient_id character varying, v_encounter_id character varying, v_ordering_provider_id character varying, v_auth_provider_id character varying, v_orderable_id character varying, v_status character varying, v_source character varying, v_code_id character varying, v_code_system character varying, v_order_name character varying, v_order_type character varying, v_order_cost numeric, v_order_datetime timestamp without time zone) RETURNS void
    LANGUAGE plpgsql
    AS $$
    DECLARE exit_loop Boolean:=FALSE;
BEGIN
  LOOP
    IF exit_loop = TRUE THEN
      EXIT;
    END IF;
    UPDATE order_ord
    SET
      status = v_status,
      order_datetime = v_order_datetime
    WHERE encounter_id = v_encounter_id AND customer_id = v_customer_id AND order_id = v_order_id AND NOT (status = v_status);
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
    WHERE encounter_id = v_encounter_id AND customer_id = v_customer_id AND order_id = v_order_id AND status = v_status;
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
           VALUES (v_customer_id, v_order_id, v_patient_id, v_status, v_order_datetime,
                  v_source, NULL);
        exit_loop = TRUE;
        RETURN;
        EXCEPTION WHEN unique_violation THEN
          END;
  END LOOP;
END;
$$;
ALTER FUNCTION public.upsert_enc_order(v_customer_id integer, v_order_id character varying, v_patient_id character varying, v_encounter_id character varying, v_ordering_provider_id character varying, v_auth_provider_id character varying, v_orderable_id character varying, v_status character varying, v_source character varying, v_code_id character varying, v_code_system character varying, v_order_name character varying, v_order_type character varying, v_order_cost numeric, v_order_datetime timestamp without time zone) OWNER TO maven;

-- Name: upsert_encounter(character varying, character varying, character varying, date, character varying, character varying, numeric, date, date, numeric); Type: FUNCTION; Schema: public; Owner: maven
CREATE OR REPLACE FUNCTION public.upsert_encounter(v_csn character varying, v_patient_id character varying, v_enc_type character varying, v_contact_date date, v_visit_prov_id character varying, v_bill_prov_id character varying, v_department_id numeric, v_hosp_admsn_time date, v_hosp_disch_time date, v_customer_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
  LOOP
    UPDATE encounter SET patient_id = v_patient_id, enc_type = v_enc_type, contact_date = v_contact_date,
      visit_prov_id = v_visit_prov_id, bill_prov_id = v_bill_prov_id, department_id = v_department_id,
      hosp_admsn_time = v_hosp_admsn_time, hosp_disch_time = v_hosp_disch_time WHERE csn = v_csn AND customer_id = v_customer_id;
    IF found THEN
      RETURN;
    END IF;
    BEGIN
      INSERT INTO encounter(csn, patient_id, enc_type, contact_date, visit_prov_id, bill_prov_id, department_id, hosp_admsn_time, hosp_disch_time, customer_id)
        VALUES (v_csn, v_patient_id, v_enc_type, v_contact_date, v_visit_prov_id, v_bill_prov_id, v_department_id, v_hosp_admsn_time, v_hosp_disch_time, v_customer_id);
      RETURN;
    EXCEPTION WHEN unique_violation THEN
    END;
  END LOOP;
END;
$$;
ALTER FUNCTION public.upsert_encounter(v_csn character varying, v_patient_id character varying, v_enc_type character varying, v_contact_date date, v_visit_prov_id character varying, v_bill_prov_id character varying, v_department_id numeric, v_hosp_admsn_time date, v_hosp_disch_time date, v_customer_id integer) OWNER TO maven;

-- Name: upsert_patient(character varying, numeric, character varying, character varying, character varying, character varying, character varying, date); Type: FUNCTION; Schema: public; Owner: maven
CREATE OR REPLACE FUNCTION public.upsert_patient(v_patient_id character varying, v_customer_id integer, v_birth_month character varying, v_sex character varying, v_mrn character varying, v_patname1 character varying, v_cur_pcp_prov_id character varying, v_birthdate date) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
  LOOP
    UPDATE patient SET birth_month = v_birth_month, sex = v_sex, mrn = v_mrn,
      patname = v_patname1, cur_pcp_prov_id = v_cur_pcp_prov_id, birthdate = v_birthdate WHERE patient_id = v_patient_id AND customer_id = v_customer_id;
    IF found THEN
      RETURN;
    END IF;
    BEGIN
      INSERT INTO patient(patient_id, customer_id, birth_month, sex, mrn, patname, cur_pcp_prov_id, birthdate)
        VALUES (v_patient_id, v_customer_id, v_birth_month, v_sex, v_mrn, v_patname1, v_cur_pcp_prov_id, v_birthdate);
      RETURN;
    EXCEPTION WHEN unique_violation THEN
    END;
  END LOOP;
END;
$$;
ALTER FUNCTION public.upsert_patient(v_patient_id character varying, v_customer_id integer, v_birth_month character varying, v_sex character varying, v_mrn character varying, v_patname1 character varying, v_cur_pcp_prov_id character varying, v_birthdate date) OWNER TO maven;

-- Name: upsert_user(numeric, character varying, character varying, character varying, character varying, character varying(36), character varying(36), integer[], character varying(36)[]); Type: FUNCTION; Schema: public; Owner: maven
CREATE OR REPLACE FUNCTION public.upsert_user(v_customer_id integer, v_prov_id character varying, v_user_name character varying, v_official_name character varying, v_display_name character varying, v_state character varying(36), v_ehr_state character varying(36), v_layouts integer[], v_roles character varying(36)[]) RETURNS void
    LANGUAGE plpgsql
    AS $$
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
  $$;
ALTER FUNCTION public.upsert_user(v_customer_id integer, v_prov_id character varying, v_user_name character varying, v_official_name character varying, v_display_name character varying, v_state character varying(36), v_ehr_state character varying(36), v_layouts integer[], v_roles character varying(36)[]) OWNER TO maven;