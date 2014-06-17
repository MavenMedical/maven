create user maven password 'temporary' SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN;

CREATE DATABASE maven
  WITH OWNER = maven
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'en_US.UTF-8'
       LC_CTYPE = 'en_US.UTF-8'
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


create schema terminology authorization maven;
-- Table: terminology.codemap

-- DROP TABLE terminology.codemap;

CREATE TABLE terminology.codemap
(
  snomedid numeric(18,0),
  codetype character varying(50),
  code character varying(50)
);
ALTER TABLE terminology.codemap
  OWNER TO maven;



-- Table: terminology.concept

-- DROP TABLE terminology.concept;

CREATE TABLE terminology.concept
(
  id numeric(18,0),
  effectivetime numeric(18,0),
  active integer,
  moduleid numeric(18,0),
  statusid numeric(18,0)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE terminology.concept
  OWNER TO maven;

-- Table: terminology.conceptancestry

-- DROP TABLE terminology.conceptancestry;

CREATE TABLE terminology.conceptancestry
(
  ancestor numeric(18,0) NOT NULL,
  child numeric(18,0) NOT NULL
)
WITH (
  OIDS=FALSE
);
ALTER TABLE terminology.conceptancestry
  OWNER TO maven;
-- Table: terminology.descriptions

-- DROP TABLE terminology.descriptions;

CREATE TABLE terminology.descriptions
(
  id numeric(18,0),
  effectivetime integer,
  active integer,
  moduleid numeric(18,0),
  conceptid numeric(18,0),
  languagecode character varying(2),
  typeid numeric(18,0),
  term character varying(2000),
  casesignificanceid character varying(500)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE terminology.descriptions
  OWNER TO maven;
-- Table: terminology.relationships

-- DROP TABLE terminology.relationships;

CREATE TABLE terminology.relationships
(
  id numeric(18,0),
  effectivetime integer,
  active integer,
  moduleid numeric(18,0),
  sourceid numeric(18,0),
  destinationid numeric(18,0),
  relationshipgroup numeric(18,0),
  typeid numeric(18,0),
  characteristictypeid numeric(18,0),
  modifierid numeric(18,0)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE terminology.relationships
  OWNER TO maven;

create index ixConceptActiveConceptId on terminology.Concept(Id,active);
create index ixCodeMap on terminology.codeMap (SnomedId,code);
create index ixCodeMapCodes on terminology.CodeMap(code,CodeType);
Create Index ixRelationships on terminology.Relationships(SourceId,TypeId,DestinationId);
create index ixRelationshipsDest on terminology.Relationships(destinationId,typeid,SourceId);
Create index ixDescriptionsConcept on terminology.Descriptions(ConceptId,Active);
Create index ixConceptAncestry on terminology.conceptAncestry(ancestor,child);

CREATE or replace FUNCTION isicd10child(vparentconcept numeric, vchildcode character varying) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
Declare rtn Boolean;
begin
        select (count(*)>0) into rtn
        from terminology.conceptAncestry a
        inner join terminology.CodeMap b on a.child=b.snomedid
        where
                b.codeType='ICD-10' and b.code=vChildCode
                and a.Ancestor=vParentConcept ;
        return rtn;
end;
$$;

CREATE or replace FUNCTION isicd9child(vparentconcept numeric, vchildcode character varying) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
Declare rtn Boolean;
begin
        select (count(*)>0) into rtn
        from terminology.conceptAncestry a
        inner join terminology.CodeMap b on a.child=b.snomedid
        where
                b.codeType='ICD-9' and b.code=vChildCode
                and a.Ancestor=vParentConcept ;
        return rtn;
end;
$$;


CREATE or replace FUNCTION issnomedchild(vparentconcept numeric, vchildconcept numeric) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
Declare rtn Boolean;
begin
        select (count(*)>0) into rtn from terminology.conceptAncestry where Ancestor=vParentConcept and Child=vChildConcept;
        return rtn;
end;
$$;

create type userstate as enum ('active', 'disabled');
create table users 
(
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
);
alter table users owner to maven;

create type authmethod as ENUM('local', 'forward', 'certificate', 'passthrough', 'failed', 'unverified');
create table logins
(
	user_name character varying(100),
	method authmethod,
	logintime timestamp,
	ip inet,
	environment text,
	authkey character varying(64)
);
alter table logins owner to maven;

-- Table: adt

-- DROP TABLE: adt

CREATE TABLE adt
(
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
with (
 OIDS=FALSE
);

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

CREATE TABLE alert
(
  alert_id serial PRIMARY KEY,
  customer_id numeric(18,0),
  provider_id character varying(18),
  pat_id character varying(100),
  encounter_id character varying(100),
  category character varying(100),
  status character varying(100),
  order_id character varying(100),
  code_trigger character varying(100),
  code_trigger_type character varying(100),
  cds_rule integer,
  alert_datetime timestamp without time zone,
  short_title character varying(255),
  long_title character varying,
  short_desc character varying(255),
  long_desc character varying,
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



-- Table: composition

-- DROP TABLE composition;

CREATE TABLE composition
(
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

--
-- Name: composition_comp_id_seq; Type: SEQUENCE; Schema: public; Owner: maven
--

CREATE SEQUENCE composition_comp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.composition_comp_id_seq OWNER TO maven;

--
-- Name: composition_comp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: maven
--

ALTER SEQUENCE composition_comp_id_seq OWNED BY composition.comp_id;


-- Table: costmap

-- DROP TABLE costmap;

CREATE TABLE public.costmap
(
  dep_id numeric(18,0),
  customer_id numeric(18,0),
  billing_code character varying(25),
  code_type character varying(25),
  cost_amt numeric(12,2),
  cost_type character varying(25),
  primary key(billing_code,code_type,customer_id,dep_id)
)
with (
OIDS=FALSE
);
ALTER TABLE public.costmap OWNER TO maven;

create index ixpkcostmap on public.costmap(billing_code,code_type,customer_id,dep_id);



-- Table: customer

-- DROP TABLE customer;

CREATE TABLE customer
(
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

CREATE TABLE department
(
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

-- Table: diagnosis

-- DROP TABLE diagnosis;

CREATE TABLE diagnosis
(
  dx_id numeric(18,0),
  customer_id numeric(18,0),
  current_icd9_list character varying(254),
  current_icd10_list character varying(254),
  dx_name character varying(200),
  dx_imo_id character varying(254),
  imo_term_id character varying(30),
  concept_id character varying(254)

)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.diagnosis
  OWNER TO maven;

-- Index: ixdiagnosispk

-- DROP INDEX ixdiagnosispk;

CREATE INDEX ixdiagnosispk
  ON public.diagnosis
  USING btree
  (dx_id, customer_id);


-- Table: encounter

-- DROP TABLE encounter;

CREATE TABLE encounter
(
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

-- Table: encounterdx

-- DROP TABLE encounterdx;

CREATE TABLE encounterdx
(
  encdx serial PRIMARY KEY,
  pat_id character varying(100),
  customer_id numeric(18,0),
  csn character varying(100),
  dx_id character varying(36),
  annotation character varying(200),
  primary_dx_yn character varying(1),
  dx_chronic_yn character varying(1)

)
WITH (
  OIDS=FALSE
);
ALTER TABLE encounterdx
  OWNER TO maven;


--
-- Name: encounterdx_encdx_seq; Type: SEQUENCE; Schema: public; Owner: maven
--

CREATE SEQUENCE encounterdx_encdx_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.encounterdx_encdx_seq OWNER TO maven;

--
-- Name: encounterdx_encdx_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: maven
--

ALTER SEQUENCE encounterdx_encdx_seq OWNED BY encounterdx.encdx;


-- Index: ixencounterdxcsndx

-- DROP INDEX ixencounterdxcsndx;

CREATE INDEX ixencounterdxcsndx
  ON public.encounterdx
  USING btree
  (csn, customer_id);

-- Table: labresult

-- DROP TABLE labresult;

CREATE TABLE labresult
(
  orderid numeric(18,0),
  customer_id numeric(18,0),
  pat_id character varying(100),
  csn character varying(100),
  result_time date,
  component_id numeric(18,0),
  result character varying(254),
  numeric_result double precision,
  reference_low character varying(50),
  reference_high character varying(50),
  reference_unit character varying(100),
  name character varying(75),
  external_name character varying(75),
  base_name character varying(75),
  common_name character varying(254),
  loinc_code character varying(254)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.labresult
  OWNER TO maven;

-- Index: ixlabcomponentid

-- DROP INDEX ixlabcomponentid;

CREATE INDEX ixlabcomponentid
  ON public.labresult
  USING btree
  (component_id, customer_id);

-- Index: ixlabcsn

-- DROP INDEX ixlabcsn;

CREATE INDEX ixlabcsn
  ON public.labresult
  USING btree
  (csn, customer_id);

-- Index: ixlabpatid

-- DROP INDEX ixlabpatid;

CREATE INDEX ixlabpatid
  ON public.labresult
  USING btree
  (pat_id, customer_id);


-- Table: mavenorder

-- DROP TABLE mavenorder;

CREATE TABLE mavenorder
(
  orderid serial NOT NULL,
  pat_id character varying(100),
  customer_id numeric(18,0),
  encounter_id character varying(100),
  order_name character varying(255),
  order_type character varying(36),
  proc_code character varying(36),
  code_type character varying(36),
  order_cost numeric(13,2),
  datetime timestamp without time zone,
  active boolean,
  CONSTRAINT mavenorder_pkey PRIMARY KEY (orderid)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE mavenorder
  OWNER TO maven;

-- Index: ixmavenorder

-- DROP INDEX ixmavenorder;

CREATE INDEX ixmavenorder
  ON public.mavenorder
  USING btree
  (encounter_id, customer_id);



CREATE TYPE ord_event as ENUM('created', 'signed', 'modified', 'canceled');

-- Table: order_event;

-- DROP TABLE order_event;

CREATE TABLE order_event
(
  customer_id numeric(18,0),
  order_id integer,
  provider_id character varying(100),
  order_event ord_event,
  event_datetime timestamp without time zone,
  source character varying(25),
  active_orders character varying
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.order_event
  OWNER TO maven;


-- Table: medicalprocedure

-- DROP TABLE medicalprocedure;

CREATE TABLE medicalprocedure
(
  proc_id numeric(18,0) NOT NULL,
  customer_id numeric(18,0),
  proc_name character varying(100),
  cpt_code character varying(20),
  base_charge character varying(254),
  rvu_work_compon numeric(12,2),
  rvu_overhd_compon numeric(12,2),
  rvu_malprac_compon numeric(12,2),
  rvu_total_no_mod numeric(12,2)
  )
WITH (
  OIDS=FALSE
);
ALTER TABLE public.medicalprocedure
  OWNER TO maven;

-- Index: ixprocpk

-- DROP INDEX ixprocpk;

CREATE INDEX ixprocpk
  ON public.medicalprocedure
  USING btree
  (proc_id, customer_id);

-- Table: medication

 -- DROP TABLE medication;

CREATE TABLE medication
(
  medication_id numeric(18,0) NOT NULL,
  customer_id numeric(18,0),
  name character varying(255),
  generic_name character varying(200),
  cost character varying(254),
  gpi character varying(192),
  strength character varying(254),
  form character varying(50),
  route character varying(50),
  thera_class character varying(254),
  pharm_class character varying(254),
  pharm_subclass character varying(254),
  simple_generic character varying(254)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.medication
  OWNER TO maven;

-- Index: ixmedpk

--  DROP INDEX ixmedpk;

CREATE INDEX ixmedpk
  ON public.medication
  USING btree
  (medication_id, customer_id);

-- Table: medorder

-- DROP TABLE medorder;

CREATE TABLE medorder
(
  orderid numeric(18,0),
  pat_id character varying(100),
  csn character varying(100),
  customer_id numeric(18,0),
  ordering_date date,
  ordering_time date,
  order_type character varying(10),
  medication_id numeric(18,0),
  description character varying(255),
  order_class character varying(254),
  authrzing_prov_id character varying(18)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.medorder
  OWNER TO maven;

-- Index: ixmedordercsn

--  DROP INDEX ixmedordercsn;

CREATE INDEX ixmedordercsn
  ON public.medorder
  USING btree
  (csn, customer_id);

-- Index: ixmedorderordid

--  DROP INDEX ixmedorderordid;

CREATE INDEX ixmedorderordid
  ON public.medorder
  USING btree
  (orderid, customer_id);

-- Index: ixmedorderpatid

--  DROP INDEX ixmedorderpatid;

CREATE INDEX ixmedorderpatid
  ON public.medorder
  USING btree
  (pat_id COLLATE pg_catalog."default");


-- Table: observation

-- DROP TABLE observation;

CREATE TABLE observation
(
  customer_id numeric(18,0),
  encounter_id character varying(100),
  order_id numeric(18,0),
  pat_id character varying(100),
  status character varying (254),
  result_time timestamp without time zone,
  comments character varying(254),
  numeric_result double precision,
  units character varying (254),
  reference_low double precision,
  reference_high double precision,
  reference_unit character varying(100),
  method character varying (265),
  loinc_code character varying(254),
  snomed_id bigint,
  code_id character varying (254),
  code_system character varying (254),
  name character varying(254),
  component_id numeric(18,0),
  external_name character varying(75),
  base_name character varying(75),
  common_name character varying(254)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE observation
  OWNER TO maven;


-- Table: override_indication

-- DROP TABLE override_indication

CREATE TABLE override_indication
(
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

CREATE TABLE patient
(
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

-- Table: problemlist

--  DROP TABLE problemlist;

CREATE TABLE problemlist
(
  pat_id character varying(100),
  dx_id numeric(18,0),
  customer_id numeric(18,0),
  noted_date date,
  resolved_date date,
  date_of_entry date,
  chronic_yn character varying(1),
  status character varying(254)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.problemlist
  OWNER TO maven;

-- Index: isproblostpatdx

-- DROP INDEX isproblostpatdx;

CREATE INDEX isproblostpatdx
  ON public.problemlist
  USING btree
  (pat_id, dx_id, customer_id);

-- Table: procedureorder

-- DROP TABLE procedureorder;

CREATE TABLE procedureorder
(
  orderid numeric(18,0),
  pat_id character varying(100),
  csn character varying(100),
  customer_id numeric(18,0),
  ordering_date date,
  ordering_time date,
  order_type character varying(254),
  cpt_code character varying(20),
  description character varying(254),
  order_class character varying(254),
  authrzing_prov_id character varying(18)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.procedureorder
  OWNER TO maven;

-- Index: ixprocordercsn

--  DROP INDEX ixprocordercsn;

CREATE INDEX ixprocordercsn
  ON public.procedureorder
  USING btree
  (csn, customer_id);

-- Index: ixprocorderordid

-- DROP INDEX ixprocorderordid;

CREATE INDEX ixprocorderordid
  ON public.procedureorder
  USING btree
  (orderid, customer_id);

-- Index: ixprocorderpatid

-- DROP INDEX ixprocorderpatid;

CREATE INDEX ixprocorderpatid
  ON public.procedureorder
  USING btree
  (pat_id, customer_id);


-- Table: provider

-- DROP TABLE provider;

CREATE TABLE provider
(
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


CREATE TABLE sleuth_evidence
(
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


-- Table: sleuth_rule

-- DROP TABLE sleuth_rule

CREATE TABLE sleuth_rule
(
  rule_id serial,
  customer_id numeric(18,0),
  dep_id numeric(18,0),
  code_trigger character varying(100),
  code_trigger_type character varying(100),
  name character varying(100),
  tag_line character varying(100),
  description character varying(255),
  rule_details json
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.sleuth_rule
  OWNER TO maven;

-- Index: idxsleuthrule

-- DROP INDEX: ixsleuthrule


-- Table: ucl

-- DROP TABLE ucl;

CREATE TABLE ucl
(
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



CREATE OR REPLACE FUNCTION upsert_patient(pat_id1 character varying(100), customer_id1 numeric(18,0),
  birth_month1 character varying(6), sex1 character varying(254),
  mrn1 character varying(100), patname1 character varying(100),
  cur_pcp_prov_id1 character varying(18), birthdate1 date)
  RETURNS VOID AS
$$
BEGIN
  LOOP
    UPDATE patient SET birth_month = birth_month1, sex = sex1, mrn = mrn1,
      patname = patname1, cur_pcp_prov_id = cur_pcp_prov_id1, birthdate = birthdate1 WHERE pat_id = pat_id1 AND customer_id = customer_id1;
    IF found THEN
      RETURN;
    END IF;
    BEGIN
      INSERT INTO patient(pat_id, customer_id, birth_month, sex, mrn, patname, cur_pcp_prov_id, birthdate)
        VALUES (pat_id1, customer_id1, birth_month1, sex1, mrn1, patname1, cur_pcp_prov_id1, birthdate1);
      RETURN;
    EXCEPTION WHEN unique_violation THEN
    END;
  END LOOP;
END;
$$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION upsert_patient(character varying(100), numeric(18,0), character varying(6),
character varying(254), character varying(100), character varying(100), character varying(18), date)
  OWNER TO maven;

CREATE OR REPLACE FUNCTION upsert_enc_order(pat_id1 character varying(100),
  customer_id1 numeric(18,0),
  encounter_id1 character varying(100),
  order_name1 character varying(255),
  order_type1 character varying(36),
  proc_code1 character varying(36),
  code_type1 character varying(36),
  order_cost1 numeric(13,2),
  datetime1 timestamp without time zone,
  active1 boolean)
  RETURNS VOID AS
$$
BEGIN
  LOOP
    UPDATE mavenorder SET pat_id =pat_id1,
    customer_id = customer_id1,
    encounter_id = encounter_id1,
    order_name = order_name1,
    order_type = order_type1,
    proc_code = proc_code1,
    code_type = code_type1,
    order_cost = order_cost1,
    active = active1
    WHERE encounter_id = encounter_id1 and customer_id = customer_id1 and proc_code = proc_code1;
    IF found THEN
      RETURN;
    END IF;
    BEGIN
      INSERT INTO mavenorder(pat_id, customer_id, encounter_id, order_name, order_type, proc_code, code_type, order_cost, datetime, active)
        VALUES (pat_id1, customer_id1, encounter_id1, order_name1, order_type1, proc_code1, code_type1, order_cost1, datetime1, active1);
      RETURN;
    EXCEPTION WHEN unique_violation THEN
    END;
  END LOOP;
END;
$$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION upsert_enc_order(pat_id character varying(100),
  customer_id numeric(18,0),
  encounter_id character varying(100),
  order_name character varying(255),
  order_type character varying(36),
  proc_code character varying(36),
  code_type character varying(36),
  order_cost numeric(13,2),
  datetime timestamp without time zone,
  active boolean)
  OWNER TO maven;


CREATE OR REPLACE FUNCTION upsert_encounter(csn1 character varying(100), pat_id1 character varying(100),
  enc_type1 character varying(254), contact_date1 date,
  visit_prov_id1 character varying(18), bill_prov_id1 character varying(18), department_id1 numeric(18,0),
  hosp_admsn_time1 date, hosp_disch_time1 date, customer_id1 numeric(18,0))
  RETURNS VOID AS
$$
BEGIN
  LOOP
    UPDATE encounter SET pat_id = pat_id1, enc_type = enc_type1, contact_date = contact_date1,
      visit_prov_id = visit_prov_id1, bill_prov_id = bill_prov_id1, department_id = department_id1,
      hosp_admsn_time = hosp_admsn_time1, hosp_disch_time = hosp_disch_time1 WHERE csn = csn1 AND customer_id = customer_id1;
    IF found THEN
      RETURN;
    END IF;
    BEGIN
      INSERT INTO encounter(csn, pat_id, enc_type, contact_date, visit_prov_id, bill_prov_id, department_id, hosp_admsn_time, hosp_disch_time, customer_id)
        VALUES (csn1, pat_id1, enc_type1, contact_date1, visit_prov_id1, bill_prov_id1, department_id1, hosp_admsn_time1, hosp_disch_time1, customer_id1);
      RETURN;
    EXCEPTION WHEN unique_violation THEN
    END;
  END LOOP;
END;
$$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION upsert_encounter(character varying(100), character varying(100), character varying(254),
date, character varying(18), character varying(18), numeric(18,0), date, date, numeric(18,0))
  OWNER TO maven;


CREATE OR REPLACE FUNCTION upsert_condition(pat_id1 character varying(100),
  customer_id1 numeric(18,0),
  encounter_id1 character varying(100),
  dx_category1 character varying(25),
  status1 character varying(25),
  date_asserted1 timestamp without time zone,
  date_resolved1 timestamp without time zone,
  snomed_id1 bigint,
  dx_code_id1 character varying(25),
  dx_code_system1 character varying(255),
  dx_text1 character varying,
  is_principle1 boolean,
  is_chronic1 boolean,
  is_poa1 boolean
)
  RETURNS VOID AS
$$
BEGIN
  LOOP
    UPDATE condition
    SET dx_category=dx_category1,
      status=status1,
      date_asserted=date_asserted1,
      date_resolved=date_resolved1,
      dx_text=dx_text1,
      is_principle=is_principle1,
      is_chronic=is_chronic1,
      is_poa=is_poa1
       WHERE encounter_id=encounter_id1 AND customer_id=customer_id1 AND (snomed_id=snomed_id1 OR (dx_code_id=dx_code_id1 AND dx_code_system=dx_code_system1)) ;
    IF found THEN
      RETURN;
    END IF;
    BEGIN
      INSERT INTO condition(
            pat_id, customer_id, encounter_id, dx_category, status, date_asserted,
            date_resolved, snomed_id, dx_code_id, dx_code_system, dx_text,
            is_principle, is_chronic, is_poa)
        VALUES (pat_id1, customer_id1, encounter_id1, dx_category1, status1, date_asserted1,
            date_resolved1, snomed_id1, dx_code_id1, dx_code_system1, dx_text1,
            is_principle1, is_chronic1, is_poa1);
      RETURN;
    EXCEPTION WHEN unique_violation THEN
    END;
  END LOOP;
END;
$$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION upsert_condition(character varying(100),
  numeric(18,0),
  character varying(100),
  character varying(25),
  character varying(25),
  timestamp without time zone,
  timestamp without time zone,
  bigint,
  character varying(25),
  character varying(255),
  character varying,
  boolean,
  boolean,
  boolean)
  OWNER TO maven;




CREATE TABLE condition
(
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
  is_poa boolean -- True-False is the Diagnosis record Present on Arrival
)
WITH (
  OIDS=FALSE
);
ALTER TABLE condition
  OWNER TO maven;
COMMENT ON COLUMN condition.is_poa IS 'True-False is the Diagnosis record Present on Arrival';

create index ixconditionpatdatsno on condition(customer_id,pat_id,date_asserted,snomed_id);
create index ixconditionpatdates on condition(customer_id,pat_id,date_asserted,date_resolved);
create index ixconditionpatstatus on condition(customer_id,pat_id,status);

CREATE TABLE observation
(
  customer_id numeric(18,0),
  encounter_id character varying(100),
  order_id numeric(18,0),
  pat_id character varying(100),
  status character varying (254),
  result_time timestamp without time zone,
  comments character varying(254),
  numeric_result double precision,
  units character varying (254),
  reference_low character varying(50),
  reference_high character varying(50),
  reference_unit character varying(100),
  method character varying (254),
  loinc_code character varying(254),
  snomed_id bigint,
  code_id character varying (254),
  code_system character varying (254),
  name character varying(254),
  component_id numeric(18,0),
  external_name character varying(75),
  base_name character varying(75),
  common_name character varying(254)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE observation
  OWNER TO maven;

 create index ixobsPatLoincDate on observation(customer_id,pat_id,loinc_code,result_time,numeric_result);

create schema rules ;

create table rules.eviRule
(
  ruleId int primary key,
  name varchar(200) ,
  minAge numeric(18,2),
  maxAge numeric(18,2),
  sex varchar(1),
  codeType varchar(20),
  remainingDetails text,
  fullspec text,
  comments text
);
alter table rules.evirule owner to maven;
create index ixRulePk on rules.eviRule(ruleId);
create index ixRuleTypeAgeSex on rules.eviRule(codeType,minAge,maxAge,sex);

create table rules.trigCodes
(
  ruleId int,
  code varchar(50),
  primary key (ruleId,code)
);
alter table rules.trigCodes owner to maven;
create index ixTrigCodePk on rules.trigCodes(ruleId,code);
create index ixTrigCodeCode on rules.trigCodes(code,ruleId);

create table rules.codeLists
(
  ruleId int
  ,listType varchar(20)
  ,isIntersect boolean
  ,intList bigint[]
  ,strList varchar[]
  ,framemin int
  ,framemax int
);
alter table rules.codeLists owner to maven;
create index ixruleCodeListsId on rules.codelists(ruleid);
--CREATE INDEX rules.ixcodelistgin rules.codelists USING gin(intlist);

create  table rules.labeval(
	ruleid int
	,loinc_codes varchar[]
	,threshold double precision
	,relation varchar(1)
	,framemin int
	,framemax int
	,defaultval boolean
);
create  index ixlabevalRule on rules.labeval(ruleid,loinc_codes);

 create or replace function rules.evalLabs(cust int, pat varchar(100),framemin int, framemax int, defval boolean,relation varchar(1),comparison double precision,loincs varchar[])
 returns boolean
 as $$
 declare 
	rtn int;
 begin
	if relation='<' then
		select max(case when numeric_result<comparison then 1 else 0 end) into rtn
		from public.observation a
		where a.customer_id=cust and a.pat_id=pat and a.loinc_code=any(loincs) 
		  and current_date+framemin<=result_time and current_date+framemax>=result_time;
	elsif relation='>' then
		select max(case when numeric_result>comparison then 1 else 0 end) into rtn
		from public.observation a
		where a.customer_id=cust and a.pat_id=pat and a.loinc_code=any(loincs) 
		  and current_date+framemin<=result_time and current_date+framemax>=result_time;
	elsif relation='=' then
		select max(case when numeric_result=comparison then 1 else 0 end) into rtn
		from public.observation a
		where a.customer_id=cust and a.pat_id=pat and a.loinc_code=any(loincs) 
		  and current_date+framemin<=result_time and current_date+framemax>=result_time;
	else return defval;
	end if;
	return case when rtn=1 then true when rtn=0 then false else defval end;
 end;
 $$
 language plpgsql;

create or replace function rules.comparisonIntArray(listType varchar(20),encSnomeds bigint[],probsnomeds bigint[],patid varchar(100),framemin int,framemax int,customer int)
returns bigint[] as $$
declare rtn bigint[];
	mn int;
	mx int;
begin
	mn:=coalesce(framemin,-99999);
	mx:=coalesce(framemin,1);
	if listType='PL' then
		return probsnomeds;
	elsif listtype='ENC' then
		return encSnomeds;
	elsif listtype='DXHX' then
		select encsnomeds||probsnomeds||array_agg(snomed_id) into rtn  
			from public.condition a 
			where a.pat_id=patid and a.customer_id=customer and  current_date+mn<=date_asserted and current_date+mx>=date_asserted
			group by a.pat_id ;
		return rtn;
	else 
		return null;
	end if;
end;
$$
language plpgsql;

create index ixordPatCptDt on public.mavenorder(customer_id,pat_id,proc_code,datetime,code_type) where code_type='CPT';

create or replace function rules.comparisonStrArray(listType varchar(20),patid varchar(100),framemin int,framemax int,customer int)
returns varchar[] as $$
declare rtn varchar[];
	mn int;
	mx int;
begin
	mn:=coalesce(framemin,-99999);
	mx:=coalesce(framemin,1);
	if listType='HXPX' then
		select array_agg(proc_code) into rtn  
			from public.mavenorder a 
			where a.pat_id=patid and a.customer_id=customer and code_type='CPT'and  current_date+mn<=datetime and current_date+mx>=datetime
			group by a.pat_id ;
		return rtn;
	else 
		return null;
	end if;
end;
$$
language plpgsql;

create or replace function rules.evalRules(orderCode varchar, ordcodeType varchar, patAge numeric(18,2), patSex varchar, encSnomeds bigint[], probSnomeds bigint[],patid varchar(100),customer int)
returns table (ruleid int, name varchar,details text) as $$
begin
                return query execute
                'select x.ruleid,x.name,x.remainingDetails from 
                (
                select a.ruleid
                from rules.eviRule a
		  inner join rules.trigCodes b on a.ruleId=b.ruleId and b.code=$1
		  inner join rules.codeLists c on a.ruleId=c.ruleId
                where 
                   a.codetype=$2
                   and a.minage<=$3 and a.maxage>=$3
                   and $4 like a.sex
                group by a.ruleid
                having min(case when c.isIntersect=(
			(intlist is not null and rules.comparisonIntArray(c.listType,$5,$6,$7,c.framemin,c.framemax,$8)&&c.intList)
			or 
			(strlist is not null and rules.comparisonStrArray(c.listType,$7,c.framemin,c.framemax,$8)&&c.strList)
		      ) 
		  then 1 else 0 end)=1 
                ) sub inner join rules.evirule x on sub.ruleid=x.ruleid
                left outer join rules.labEval y on x.ruleid=y.ruleid
                where (y.ruleid is null or rules.evalLabs($8,$7,y.framemin,y.framemax,y.defaultval,y.relation,y.threshold,y.loinc_codes))'
                using orderCode , ordcodeType , patAge , patSex , encSnomeds , probSnomeds ,patid,customer
                ;
                   
end;
$$
language plpgsql;

