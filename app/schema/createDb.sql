create user maven password 'temporary' SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN;

CREATE DATABASE maven
  WITH OWNER = maven
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'en_US.UTF-8'
       LC_CTYPE = 'en_US.UTF-8'
       CONNECTION LIMIT = -1;

\c maven

create language plpgsql;

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

-- Schema: logging

-- DROP SCHEMA "logging";

CREATE SCHEMA "logging"
  AUTHORIZATION maven;

COMMENT ON SCHEMA "logging"
  IS 'This schema is to track/log every time an alert is fired and the content in which it was fired';


-- Table: "logging".alerts

--DROP TABLE "logging".alerts;

CREATE TABLE "logging".alert
(
  encounter_id character varying(20) NOT NULL,
  pat_id character varying(20) NOT NULL,
  userid character varying(20) NOT NULL,
  provider character varying(50),
  dep character varying(50),
  encounter_date timestamp without time zone NOT NULL,
  alert_date timestamp without time zone NOT NULL,
  orderable character varying(50),encounter_id character varying(20) NOT NULL,
  outcome character varying(50)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE "logging".alerts
  OWNER TO maven;

-- Index: "logging".ixdepartment

-- DROP INDEX ixdepartment;

CREATE INDEX ixdepartment
  ON "logging".alerts
  USING btree
  (dep COLLATE pg_catalog."default");

-- Index: "logging".ixencounter_date

-- DROP INDEX "logging".ixencounter_date;

CREATE INDEX ixencounter_date
  ON "logging".alerts
  USING btree
  (encounter_date);

-- Index: "logging".ixpatient

-- DROP INDEX ixpatient;

CREATE INDEX ixpatient
  ON "logging".alerts
  USING btree
  (pid COLLATE pg_catalog."default");

-- Index: "logging".ixuser

-- DROP INDEX ixuser;

CREATE INDEX ixuser
  ON "logging".alerts
  USING btree
  (userid COLLATE pg_catalog."default");

-- Table: department

-- DROP TABLE department;

CREATE TABLE "logging".department
(
  department_id numeric(18,0) NOT NULL,
  dep_name character varying(100),
  specialty character varying(50),
  location character varying(100),
  CONSTRAINT department_pkey PRIMARY KEY (department_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE "logging".department
  OWNER TO maven;

-- Index: ixdeppk

-- DROP INDEX ixdeppk;

CREATE INDEX ixdeppk
  ON "logging".department
  USING btree
  (department_id);

-- Table: diagnosis

-- DROP TABLE diagnosis;

CREATE TABLE "logging".diagnosis
(
  dx_id numeric(18,0),
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
ALTER TABLE "logging".diagnosis
  OWNER TO maven;

-- Index: ixdiagnosispk

-- DROP INDEX ixdiagnosispk;

CREATE INDEX ixdiagnosispk
  ON "logging".diagnosis
  USING btree
  (dx_id);

-- Table: encounter

-- DROP TABLE encounter;

CREATE TABLE "logging".encounter
(
  pat_id character varying(100),
  csn character varying(100) NOT NULL,
  enc_type character varying(254),
  contact_date date,
  visit_prov_id character varying(18),
  department_id numeric(18,0),
  hosp_admsn_time date,
  hosp_disch_time date,
  CONSTRAINT encounter_pkey PRIMARY KEY (csn)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE "logging".encounter
  OWNER TO maven;

-- Index: ixencounterpatid

-- DROP INDEX ixencounterpatid;

CREATE INDEX ixencounterpatid
  ON "logging".encounter
  USING btree
  (pat_id COLLATE pg_catalog."default");

-- Table: encounterdx

-- DROP TABLE encounterdx;

CREATE TABLE "logging".encounterdx
(
  pat_id character varying(100),
  csn character varying(100),
  dx_id numeric(18,0),
  annotation character varying(200),
  primary_dx_yn character varying(1),
  dx_chronic_yn character varying(1)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE "logging".encounterdx
  OWNER TO maven;

-- Index: ixencounterdxcsndx

-- DROP INDEX ixencounterdxcsndx;

CREATE INDEX ixencounterdxcsndx
  ON "logging".encounterdx
  USING btree
  (csn COLLATE pg_catalog."default", dx_id);

-- Table: labresult

-- DROP TABLE labresult;

CREATE TABLE "logging".labresult
(
  orderid numeric(18,0),
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
ALTER TABLE "logging".labresult
  OWNER TO maven;

-- Index: ixlabcomponentid

-- DROP INDEX ixlabcomponentid;

CREATE INDEX ixlabcomponentid
  ON "logging".labresult
  USING btree
  (component_id);

-- Index: ixlabcsn

-- DROP INDEX ixlabcsn;

CREATE INDEX ixlabcsn
  ON labresult
  USING btree
  (csn COLLATE pg_catalog."default");

-- Index: ixlabpatid

-- DROP INDEX ixlabpatid;

CREATE INDEX ixlabpatid
  ON "logging".labresult
  USING btree
  (pat_id COLLATE pg_catalog."default");

-- Table: medicalprocedure

-- DROP TABLE medicalprocedure;

CREATE TABLE "logging".medicalprocedure
(
  proc_id numeric(18,0) NOT NULL,
  proc_name character varying(100),
  cpt_code character varying(20),
  base_charge character varying(254),
  rvu_work_compon numeric(12,2),
  rvu_overhd_compon numeric(12,2),
  rvu_malprac_compon numeric(12,2),
  rvu_total_no_mod numeric(12,2),
  CONSTRAINT medicalprocedure_pkey PRIMARY KEY (proc_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE "logging".medicalprocedure
  OWNER TO maven;

-- Index: ixprocpk

-- DROP INDEX ixprocpk;

CREATE INDEX ixprocpk
  ON "logging".medicalprocedure
  USING btree
  (proc_id);

-- Table: medication

 -- DROP TABLE medication;

CREATE TABLE "logging".medication
(
  medication_id numeric(18,0) NOT NULL,
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
  simple_generic character varying(254),
  CONSTRAINT medication_pkey PRIMARY KEY (medication_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE "logging".medication
  OWNER TO maven;

-- Index: ixmedpk

--  DROP INDEX ixmedpk;

CREATE INDEX ixmedpk
  ON "logging".medication
  USING btree
  (medication_id);

-- Table: medorder

-- DROP TABLE medorder;

CREATE TABLE "logging".medorder
(
  orderid numeric(18,0),
  pat_id character varying(100),
  csn character varying(100),
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
ALTER TABLE "logging".medorder
  OWNER TO maven;

-- Index: ixmedordercsn

--  DROP INDEX ixmedordercsn;

CREATE INDEX ixmedordercsn
  ON "logging".medorder
  USING btree
  (csn COLLATE pg_catalog."default");

-- Index: ixmedorderordid

--  DROP INDEX ixmedorderordid;

CREATE INDEX ixmedorderordid
  ON "logging".medorder
  USING btree
  (orderid);

-- Index: ixmedorderpatid

--  DROP INDEX ixmedorderpatid;

CREATE INDEX ixmedorderpatid
  ON "logging".medorder
  USING btree
  (pat_id COLLATE pg_catalog."default");

-- Table: patient

-- DROP TABLE patient;

CREATE TABLE "logging".patient
(
  pat_id character varying(100) NOT NULL,
  birth_month character varying(6),
  sex character varying(254),
  mrn character varying(100),
  patname character varying(100),
  cur_pcp_prov_id character varying(18),
  CONSTRAINT patient_pkey PRIMARY KEY (pat_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE "logging".patient
  OWNER TO maven;

-- Index: ixpatpk

-- DROP INDEX ixpatpk;

CREATE INDEX ixpatpk
  ON "logging".patient
  USING btree
  (pat_id COLLATE pg_catalog."default");

-- Table: problemlist

--  DROP TABLE problemlist;

CREATE TABLE "logging".problemlist
(
  pat_id character varying(100),
  dx_id numeric(18,0),
  noted_date date,
  resolved_date date,
  date_of_entry date,
  chronic_yn character varying(1),
  status character varying(254)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE "logging".problemlist
  OWNER TO maven;

-- Index: isproblostpatdx

-- DROP INDEX isproblostpatdx;

CREATE INDEX isproblostpatdx
  ON "logging".problemlist
  USING btree
  (pat_id COLLATE pg_catalog."default", dx_id);

-- Table: procedureorder

-- DROP TABLE procedureorder;

CREATE TABLE "logging".procedureorder
(
  orderid numeric(18,0),
  pat_id character varying(100),
  csn character varying(100),
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
ALTER TABLE "logging".procedureorder
  OWNER TO maven;

-- Index: ixprocordercsn

--  DROP INDEX ixprocordercsn;

CREATE INDEX ixprocordercsn
  ON "logging".procedureorder
  USING btree
  (csn COLLATE pg_catalog."default");

-- Index: ixprocorderordid

-- DROP INDEX ixprocorderordid;

CREATE INDEX ixprocorderordid
  ON "logging".procedureorder
  USING btree
  (orderid);

-- Index: ixprocorderpatid

-- DROP INDEX ixprocorderpatid;

CREATE INDEX ixprocorderpatid
  ON "logging".procedureorder
  USING btree
  (pat_id COLLATE pg_catalog."default");

-- Table: provider

-- DROP TABLE provider;

CREATE TABLE "logging".provider
(
  prov_id character varying(18) NOT NULL,
  prov_name character varying(100),
  specialty character varying(254),
  specialty2 character varying(254),
  CONSTRAINT provider_pkey PRIMARY KEY (prov_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE "logging".provider
  OWNER TO maven;

-- Index: ixprovpk

-- DROP INDEX ixprovpk;

CREATE INDEX ixprovpk
  ON "logging".provider
  USING btree
  (prov_id COLLATE pg_catalog."default");



create schema ruleTest authorization maven;
-- Table: ruleTest.rules

-- DROP TABLE ruleTest.rules;

CREATE TABLE ruleTest.rules
(
  ruleName character varying(50),
  ruleDescription character varying(500),
  orderType character varying(4), --Med or Proc
  orderedCPT numeric(5), --CPT code
  minAge numeric(3),
  maxAge numeric(3),
  withDx character varying(500), --snomedids separated by commas
  withoutDx character varying(500), 
  details character varying(500),
  onlyInDept character varying(50),
  notInDept character varying(50)
);
ALTER TABLE ruleTest.rules
  OWNER TO maven;

INSERT INTO ruleTest.rules VALUES ('Test rule name','This is the test rule description','proc',12345,0,200,'12345678,9012345,67890123,1222222,56789876','90324023984,43987523,309753492785,53425243235','These are the details for the test rule','test only in department','test not in department'); 
INSERT INTO ruleTest.rules VALUES ('Test rule name 1','This is the test rule description 1','proc',12345,0,200,'22345678,0012345,77890123,2222222,66789876','00324023984,33987523,009753492785,33425243235','These are the details for the test rule1','test only in department1','test not in department1');
