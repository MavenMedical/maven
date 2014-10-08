create user maven password 'temporary' SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN;

CREATE DATABASE maven
  WITH OWNER = maven
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'en_US.utf8'
       LC_CTYPE = 'en_US.utf8'
       CONNECTION LIMIT = -1;

\c maven

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner:
--
CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;

--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner:
--
COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


-- Schema: public
-- DROP SCHEMA public;
CREATE SCHEMA public
  AUTHORIZATION postgres;
GRANT ALL ON SCHEMA public TO maven;
GRANT ALL ON SCHEMA public TO public;


-- Schema: categories
-- DROP SCHEMA categories;
CREATE SCHEMA categories
  AUTHORIZATION maven;
GRANT ALL ON SCHEMA categories to maven;




-- Table: adt
-- DROP TABLE: adt
CREATE TABLE adt (
  event_id character varying(100),
  customer_id numeric(18,0),
  pat_id character varying(100),
  encounter_id character varying(100),
  prov_id character varying(18),
  event_type character varying(25),
  event_time timestamp,
  dep_id numeric(18,0),
  room_id character varying(25)
)
  WITH (
      OIDS=FALSE
  );
ALTER TABLE public.adt
    OWNER TO maven;

-- Index: ixadtevent
-- DROP INDEX: ixadtevent
CREATE INDEX ixadtevent
  on public.adt
  USING btree
  (event_id, customer_id);

-- Index: ixadtpatient
-- DROP INDEX: ixadtpatient
CREATE INDEX ixadtpatient
  on public.adt
  USING btree
  (pat_id, customer_id);

ALTER TABLE public.adt OWNER TO maven;


-- Table: alert
-- DROP TABLE alert;
CREATE TABLE alert (
  alert_id serial,
  alert_uuid character varying(36),
  customer_id numeric(18,0),
  provider_id character varying(18),
  pat_id character varying(100),
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
  saving numeric(18,2)
)
  WITH (
      OIDS=FALSE
  );
ALTER TABLE public.alert
    OWNER TO maven;


-- Index: "logging".ixencounter
-- DROP INDEX ixencounter;
CREATE INDEX ixencounter
  ON public.alert
  USING btree
  (encounter_id, customer_id);

-- Index: "logging".ixprovider
-- DROP INDEX ixprovider;
CREATE INDEX ixprovider
  ON public.alert
  USING btree
  (provider_id, customer_id);


-- Table: alert_config
-- DROP TABLE alert_config;
CREATE TABLE alert_config (
  customer_id numeric(18,0),
  department numeric(18,0),
  category character varying(36),
  rule_id integer,
  validation_status integer,
  provide_optouts character varying(36)[]
)
  WITH (
      OIDS=FALSE
  );
ALTER TABLE public.alert_config
    OWNER TO maven;


-- Table: categories.cost_type
-- DROP TABLE categories.cost_type;
CREATE TABLE categories.cost_type (
  value integer,
  name character varying(255)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE categories.cost_type
  OWNER TO maven;


-- Table: categories.cost_type
-- DROP TABLE categories.cost_type;
CREATE TABLE categories.validation_status (
  value integer,
  name character varying(255)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE categories.validation_status
  OWNER TO maven;


-- Table: composition
-- DROP TABLE composition;
CREATE TABLE composition (
  comp_id serial NOT NULL,
  patient_id character varying(100),
  customer_id numeric(18,0),
  comp_body json,
  encounter_id character varying(100),
  CONSTRAINT composition_pkey PRIMARY KEY (comp_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.composition
  OWNER TO maven;


-- Table: condition
-- DROP TABLE condition;
CREATE TABLE condition (
    pat_id character varying(100),
    customer_id numeric(18,0),
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

-- Index: ixconditionpatdates
-- DROP INDEX ixconditionpatdates
CREATE INDEX ixconditionpatdates
  ON condition
  USING btree
  (customer_id, pat_id, date_asserted, date_resolved);

--
-- Name: ixconditionpatdatsno; Type: INDEX; Schema: public; Owner: maven; Tablespace:
--
CREATE INDEX ixconditionpatdatsno ON condition USING btree (customer_id, pat_id, date_asserted, snomed_id);

--
-- Name: ixconditionpatstatus; Type: INDEX; Schema: public; Owner: maven; Tablespace:
--
CREATE INDEX ixconditionpatstatus ON condition USING btree (customer_id, pat_id, status);



-- Table: costmap
-- DROP TABLE costmap;
CREATE TABLE costmap (
  customer_id numeric(18,0),
  code character varying(36),
  code_type character varying(36),
  department character varying(255),
  cost_type integer,
  orderable_id character varying(36),
  cost numeric(18,2)
);
ALTER TABLE public.costmap OWNER TO maven;

-- Index: ixcostmap
-- DROP INDEX ixcostmap;
CREATE INDEX ixcostmap
  ON public.costmap
  USING btree
  (code, customer_id, department, code_type, cost_type);



-- Table: costmap
-- DROP TABLE costmap;
CREATE TABLE costmap_historic (
  customer_id numeric(18,0),
  code character varying(36),
  code_type character varying(36),
  department character varying(255),
  cost_type integer,
  orderable_id character varying(36),
  cost numeric(18,2),
  source_info character varying,
  exp_date timestamp without time zone
);
ALTER TABLE public.costmap_historic OWNER TO maven;

-- Index: ixcostmaphx
-- DROP INDEX ixcostmaphx;
CREATE INDEX ixcostmaphx
  ON public.costmap_historic
  USING btree
  (code, customer_id, department, code_type, cost_type);



-- Table: customer
-- DROP TABLE customer;
CREATE TABLE customer (
  customer_id numeric(18,0) PRIMARY KEY,
  name character(255) NOT NULL,
  abbr character varying(22),
  license_type numeric(9,0),
  license_exp date
);
ALTER TABLE public.customer OWNER TO maven;

-- Index: ixcustomer
-- DROP INDEX ixcustomer;
CREATE INDEX ixcustomer
  ON public.customer
  USING btree
  (customer_id);


-- Table: department
-- DROP TABLE department;
CREATE TABLE department (
  department_id numeric(18,0) NOT NULL,
  customer_id numeric(18,0),
  dep_name character varying(100),
  specialty character varying(50),
  location character varying(100)

)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.department
  OWNER TO maven;

-- Index: ixdeppk
-- DROP INDEX ixdeppk;
CREATE INDEX ixdeppk
  ON public.department
  USING btree
  (department_id, customer_id);


-- Table: encounter
-- DROP TABLE encounter;
CREATE TABLE encounter (
  csn character varying(100) NOT NULL,
  customer_id numeric(18,0),
  pat_id character varying(100),
  enc_type character varying(254),
  contact_date date,
  visit_prov_id character varying(18),
  bill_prov_id character varying(18),
  department_id numeric(18,0),
  hosp_admsn_time date,
  hosp_disch_time date
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.encounter
  OWNER TO maven;

-- Index: ixencounterpatid
-- DROP INDEX ixencounterpatid;
CREATE INDEX ixencounterpatid
  ON public.encounter
  USING btree
  (pat_id, customer_id);

-- Index: ixencounterprovid
-- DROP INDEX ixencounterprovid
CREATE INDEX ixencounterprovid
  ON public.encounter
  USING btree
  (visit_prov_id, customer_id);

-- Index: ixencounterbillprovid
-- DROP INDEX ixencounterbillprovid
CREATE INDEX ixencounterbillprovid
  ON public.encounter
  USING btree
  (bill_prov_id, customer_id);


-- Table: logins
-- DROP TABLE logins;
create type authmethod as ENUM('local', 'forward', 'certificate', 'passthrough', 'failed', 'unverified');
CREATE TABLE logins (
	user_name character varying(100),
	method authmethod,
	logintime timestamp,
	ip inet,
	environment text,
	authkey character varying(64)
)
  WITH (
      OIDS=FALSE
  );
ALTER TABLE public.logins
    OWNER TO maven;


-- Table: observable;
-- DROP TABLE observable;
CREATE TABLE observable (
    customer_id numeric(18,0),
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


-- Table: observation
-- DROP TABLE observation;
CREATE TABLE observation (
  customer_id numeric(18,0),
  encounter_id character varying(100),
  order_id character varying(36),
  pat_id character varying(100),
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
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.observation
  OWNER TO maven;

create index ixobsPatLoincDate on observation(customer_id,pat_id,loinc_code,result_time,numeric_result);


-- Table: order_event;
-- DROP TABLE order_event;
CREATE TABLE order_event (
  customer_id numeric(18,0),
  encounter_id character varying(100),
  order_id character varying(36),
  provider_id character varying(100),
  order_event character varying(2),
  event_datetime timestamp without time zone,
  source character varying(255),
  active_orders character varying
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.order_event
  OWNER TO maven;


-- Table: order_ord
-- DROP TABLE order_ord;
CREATE TABLE order_ord (
  customer_id numeric(18,0),
  order_id character varying(36),
  pat_id character varying(100),
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

-- Index: ixorder_ord
-- DROP INDEX ixorder_ord;
CREATE INDEX ixorder_ord ON order_ord USING btree (encounter_id, customer_id);

-- Table: orderable
-- DROP TABLE orderable;
CREATE TABLE orderable (
  customer_id numeric(18,0),
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


-- Table: override_indication
-- DROP TABLE override_indication
CREATE TABLE override_indication (
  override_id serial PRIMARY KEY,
  customer_id numeric(18,0),
  sleuth_rule integer,
  category character varying(255),
  name character varying(25),
  description character varying(255)
)
  WITH (
      OIDS=FALSE
  );
ALTER TABLE public.override_indication
    OWNER TO maven;

-- Table: patient
-- DROP TABLE patient;
CREATE TABLE patient (
  pat_id character varying(100) NOT NULL,
  customer_id numeric(18,0),
  birth_month character varying(6),
  birthdate date,
  sex character varying(254),
  mrn character varying(100),
  patname character varying(100),
  cur_pcp_prov_id character varying(18)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.patient
  OWNER TO maven;

-- Index: ixpatpk
-- DROP INDEX ixpatpk;
CREATE INDEX ixpatpk
  ON public.patient
  USING btree
  (pat_id, customer_id);


-- Table: provider
-- DROP TABLE provider;
CREATE TABLE provider (
  prov_id character varying(18) NOT NULL,
  customer_id numeric(18,0),
  prov_name character varying(100),
  specialty character varying(254),
  specialty2 character varying(254)
  )
WITH (
  OIDS=FALSE
);
ALTER TABLE public.provider
  OWNER TO maven;

-- Index: ixprovpk
-- DROP INDEX ixprovpk;
CREATE INDEX ixprovpk
  ON public.provider
  USING btree
  (prov_id , customer_id);


-- Table: sleuth_evidence
-- DROP TABLE: sleuth_evidence
CREATE TABLE sleuth_evidence (
  evidence_id serial,
  customer_id numeric(18,0),
  sleuth_rule integer,
  short_name character varying(25),
  name character varying(100),
  description character varying,
  source character varying(100),
  source_url character varying(255)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.sleuth_evidence
  OWNER TO maven;


-- Table: ucl
-- DROP TABLE ucl;
CREATE TABLE ucl (
  ucl_id character varying(100),
  customer_id numeric(18,0),
  post_date timestamp,
  svcs_date timestamp,
  pat_id character varying(100),
  encounter_id character varying(100),
  order_id numeric(18,0),
  proc_id numeric(18,0),
  med_id numeric(18,0),
  bill_prov_id character varying(18),
  svcs_prov_id character varying(18),
  charge_amt numeric(12,2),
  cost_amt numeric(12,2),
  quantity numeric(9),
  department_id numeric(18,0),
  billing_code character varying(25),
  code_type character varying(25)
)
WITH (
    OIDS=FALSE
);

-- Index: ixuclpk
-- DROP INDEX: ixuclpk
CREATE INDEX ixuclpk
  on public.ucl
  USING btree
  (ucl_id, customer_id);

-- Index: ixbillcode
-- DROP INDEX: ixbillcode
CREATE INDEX ixbillcode
  on public.ucl
  USING btree
  (billing_code, customer_id);

-- Index: ixprocedure
-- DROP INDEX: ixprocedure
CREATE INDEX ixprocedure
  on public.ucl
  USING btree
  (proc_id, customer_id);

-- Index: ixmedication
-- DROP INDEX: ixmedication
CREATE INDEX ixmedication
  on public.ucl
  USING btree
  (med_id, customer_id);


create type userstate as enum ('active', 'disabled');
CREATE TABLE users (
	user_id serial NOT NULL,
	customer_id numeric(18,0),
	prov_id character varying(18),
	user_name character varying(100),
	official_name character varying(100),
	display_name character varying(100),
	pw bytea,
	pw_expiration timestamp,
	old_passwords bytea[],
	state userstate
)
  WITH (
      OIDS=FALSE
  );
ALTER TABLE public.users
    OWNER TO maven;


--
-- Name: upsert_condition(character varying, numeric, character varying, character varying, character varying, timestamp without time zone, timestamp without time zone, numeric, character varying, character varying, character varying, boolean, boolean, boolean); Type: FUNCTION; Schema: public; Owner: maven
--
CREATE OR REPLACE FUNCTION upsert_condition(v_pat_id character varying, v_customer_id numeric, v_encounter_id character varying, v_dx_category character varying, v_status character varying, v_date_asserted timestamp without time zone, v_date_resolved timestamp without time zone, v_snomed_id numeric, v_dx_code character varying, v_dx_code_system character varying, v_dx_text character varying, v_is_principle boolean, v_is_chronic boolean, v_is_poa boolean) RETURNS void
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
       WHERE encounter_id=v_encounter_id AND customer_id=v_customer_id AND (snomed_id=v_snomed_id OR (dx_code_id=v_dx_code AND dx_code_system=v_dx_code_system)) ;
    IF found THEN
      RETURN;
    END IF;
    BEGIN
      INSERT INTO condition(
            pat_id, customer_id, encounter_id, dx_category, status, date_asserted,
            date_resolved, snomed_id, dx_code_id, dx_code_system, dx_text,
            is_principle, is_chronic, is_poa)
        VALUES (v_pat_id, v_customer_id, v_encounter_id, v_dx_category, v_status, v_date_asserted,
            v_date_resolved, v_snomed_id, v_dx_code, v_dx_code_system, v_dx_text,
            v_is_principle, v_is_chronic, v_is_poa);
      RETURN;
    EXCEPTION WHEN unique_violation THEN
    END;
  END LOOP;
END;
$$;
ALTER FUNCTION public.upsert_condition(v_pat_id character varying, v_customer_id numeric, v_encounter_id character varying, v_dx_category character varying, v_status character varying, v_date_asserted timestamp without time zone, v_date_resolved timestamp without time zone, v_snomed_id numeric, v_dx_code character varying, v_dx_code_system character varying, v_dx_text character varying, v_is_principle boolean, v_is_chronic boolean, v_is_poa boolean) OWNER TO maven;


--
-- Name: upsert_enc_order(numeric, character varying, character varying, character varying, character varying, character varying, character varying, ord_event, ord_source, character varying, character varying, character varying, character varying, numeric, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: maven
--
CREATE OR REPLACE FUNCTION upsert_enc_order(v_customer_id numeric, v_order_id character varying, v_pat_id character varying, v_encounter_id character varying, v_ordering_provider_id character varying, v_auth_provider_id character varying, v_orderable_id character varying, v_status character varying, v_source character varying, v_code_id character varying, v_code_system character varying, v_order_name character varying, v_order_type character varying, v_order_cost numeric, v_order_datetime timestamp without time zone) RETURNS void
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
         VALUES (v_customer_id, v_order_id, v_pat_id, v_status, v_order_datetime,
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
        INSERT INTO order_ord(customer_id, order_id, pat_id, encounter_id, ordering_provider_id,
                              auth_provider_id, orderable_id, status, source, code_id, code_system,
                              order_name, order_type, order_cost, order_datetime)
          VALUES (v_customer_id, v_order_id, v_pat_id, v_encounter_id, v_ordering_provider_id,
                  v_auth_provider_id, v_orderable_id, v_status, v_source, v_code_id, v_code_system,
                  v_order_name, v_order_type, v_order_cost, v_order_datetime);
        INSERT INTO order_event(
              customer_id, order_id, provider_id, order_event, event_datetime,
              source, active_orders)
           VALUES (v_customer_id, v_order_id, v_pat_id, v_status, v_order_datetime,
                  v_source, NULL);
        exit_loop = TRUE;
        RETURN;
        EXCEPTION WHEN unique_violation THEN
          END;
  END LOOP;
END;
$$;
ALTER FUNCTION public.upsert_enc_order(v_customer_id numeric, v_order_id character varying, v_pat_id character varying, v_encounter_id character varying, v_ordering_provider_id character varying, v_auth_provider_id character varying, v_orderable_id character varying, v_status character varying, v_source character varying, v_code_id character varying, v_code_system character varying, v_order_name character varying, v_order_type character varying, v_order_cost numeric, v_order_datetime timestamp without time zone) OWNER TO maven;


--
-- Name: upsert_encounter(character varying, character varying, character varying, date, character varying, character varying, numeric, date, date, numeric); Type: FUNCTION; Schema: public; Owner: maven
--
CREATE OR REPLACE FUNCTION upsert_encounter(v_csn character varying, v_pat_id character varying, v_enc_type character varying, v_contact_date date, v_visit_prov_id character varying, v_bill_prov_id character varying, v_department_id numeric, v_hosp_admsn_time date, v_hosp_disch_time date, v_customer_id numeric) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
  LOOP
    UPDATE encounter SET pat_id = v_pat_id, enc_type = v_enc_type, contact_date = v_contact_date,
      visit_prov_id = v_visit_prov_id, bill_prov_id = v_bill_prov_id, department_id = v_department_id,
      hosp_admsn_time = v_hosp_admsn_time, hosp_disch_time = v_hosp_disch_time WHERE csn = v_csn AND customer_id = v_customer_id;
    IF found THEN
      RETURN;
    END IF;
    BEGIN
      INSERT INTO encounter(csn, pat_id, enc_type, contact_date, visit_prov_id, bill_prov_id, department_id, hosp_admsn_time, hosp_disch_time, customer_id)
        VALUES (v_csn, v_pat_id, v_enc_type, v_contact_date, v_visit_prov_id, v_bill_prov_id, v_department_id, v_hosp_admsn_time, v_hosp_disch_time, v_customer_id);
      RETURN;
    EXCEPTION WHEN unique_violation THEN
    END;
  END LOOP;
END;
$$;
ALTER FUNCTION public.upsert_encounter(v_csn character varying, v_pat_id character varying, v_enc_type character varying, v_contact_date date, v_visit_prov_id character varying, v_bill_prov_id character varying, v_department_id numeric, v_hosp_admsn_time date, v_hosp_disch_time date, v_customer_id numeric) OWNER TO maven;


--
-- Name: upsert_patient(character varying, numeric, character varying, character varying, character varying, character varying, character varying, date); Type: FUNCTION; Schema: public; Owner: maven
--
CREATE OR REPLACE FUNCTION upsert_patient(v_pat_id character varying, v_customer_id numeric, v_birth_month character varying, v_sex character varying, v_mrn character varying, v_patname1 character varying, v_cur_pcp_prov_id character varying, v_birthdate date) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
  LOOP
    UPDATE patient SET birth_month = v_birth_month, sex = v_sex, mrn = v_mrn,
      patname = v_patname1, cur_pcp_prov_id = v_cur_pcp_prov_id, birthdate = v_birthdate WHERE pat_id = v_pat_id AND customer_id = v_customer_id;
    IF found THEN
      RETURN;
    END IF;
    BEGIN
      INSERT INTO patient(pat_id, customer_id, birth_month, sex, mrn, patname, cur_pcp_prov_id, birthdate)
        VALUES (v_pat_id, v_customer_id, v_birth_month, v_sex, v_mrn, v_patname1, v_cur_pcp_prov_id, v_birthdate);
      RETURN;
    EXCEPTION WHEN unique_violation THEN
    END;
  END LOOP;
END;
$$;
ALTER FUNCTION public.upsert_patient(v_pat_id character varying, v_customer_id numeric, v_birth_month character varying, v_sex character varying, v_mrn character varying, v_patname1 character varying, v_cur_pcp_prov_id character varying, v_birthdate date) OWNER TO maven;
