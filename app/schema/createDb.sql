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


-- Table: costmap

-- DROP TABLE costmap;

CREATE TABLE costmap
(
  costmap_id serial PRIMARY KEY,
  dep_id numeric(18,0),
  customer_id numeric(18,0),
  billing_code character varying(25),
  code_type character varying(25),
  cost_amt numeric(12,2),
  cost_type character varying(25)
)
with (
OIDS=FALSE
);

-- Index: ixcostmap

-- DROP INDEX: ixcostmap

CREATE INDEX ixcostmap
  on public.costmap
  USING btree
  (costmap_id);

-- Index: ixcostmapbillcode

-- DROP INDEX: ixcostmapbillcode

CREATE INDEX ixcostmapbillcode
  on public.costmap
  USING btree
  (billing_code, customer_id);


CREATE TABLE alerts
(
  alert_id serial PRIMARY KEY,
  customer_id numeric(18,0),
  encounter_id character varying(100) NOT NULL,
  pat_id character varying(100) NOT NULL,
  prov_id character varying(18) NOT NULL,
  prov_name character varying(100),
  dep numeric(18,0),
  encounter_date timestamp without time zone NOT NULL,
  alert_date timestamp without time zone NOT NULL,
  orderable character varying(128),
  outcome character varying(128),
  alert_title character varying(128),
  alert_msg character varying(300),
  action character varying(128),
  saving integer
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.alerts
  OWNER TO maven;

-- Index: public.ixalert

-- DROP INDEX ixalert;

CREATE INDEX ixalert
  ON public.alerts
  USING btree
  (alert_id);


-- Index: public.ixdepartment

-- DROP INDEX ixdepartment;

CREATE INDEX ixdepartment
  ON public.alerts
  USING btree
  (dep, customer_id);

-- Index: public.ixencounter_date

-- DROP INDEX public.ixencounter_date;

CREATE INDEX ixencounter_date
  ON public.alerts
  USING btree
  (encounter_date);

-- Index: "logging".ixpatient

-- DROP INDEX ixpatient;

CREATE INDEX ixpatient
  ON public.alerts
  USING btree
  (pat_id, customer_id);

-- Index: "logging".ixuser

-- DROP INDEX ixuser;

CREATE INDEX ixprovider
  ON public.alertsn
  USING btree
  (prov_id, customer_id);


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
ALTER TABLE composition
  OWNER TO maven;


-- Table: department

-- DROP TABLE department;

CREATE TABLE department
(
  department_id numeric(18,0) NOT NULL,
  dep_name character varying(100),
  specialty character varying(50),
  location character varying(100),
  customer_id numeric(18,0)

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
  current_icd9_list character varying(254),
  current_icd10_list character varying(254),
  dx_name character varying(200),
  dx_imo_id character varying(254),
  imo_term_id character varying(30),
  concept_id character varying(254),
  customer_id numeric(18,0)
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
  pat_id character varying(100),
  enc_type character varying(254),
  contact_date date,
  visit_prov_id character varying(18),
  bill_prov_id character varying(18),
  department_id numeric(18,0),
  hosp_admsn_time date,
  hosp_disch_time date,
  customer_id numeric(18,0)
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
  pat_id character varying(100),
  csn character varying(100),
  dx_id numeric(18,0),
  annotation character varying(200),
  primary_dx_yn character varying(1),
  dx_chronic_yn character varying(1),
  customer_id numeric(18,0)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.encounterdx
  OWNER TO maven;

-- Index: ixencounterdxcsndx

-- DROP INDEX ixencounterdxcsndx;

CREATE INDEX ixencounterdxcsndx
  ON public.encounterdx
  USING btree
  (csn, dx_id, customer_id);

-- Table: labresult

-- DROP TABLE labresult;

CREATE TABLE labresult
(
  orderid numeric(18,0),
  pat_id character varying(100),
  csn character varying(100),
  customer_id numeric(18,0),
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

-- Table: patient

-- DROP TABLE patient;

CREATE TABLE patient
(
  pat_id character varying(100) NOT NULL,
  customer_id numeric(18,0),
  birth_month character varying(6),
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

CREATE OR REPLACE FUNCTION upsert_patient(pat_id1 character varying(100), customer_id1 numeric(18,0),
  birth_month1 character varying(6), sex1 character varying(254),
  mrn1 character varying(100), patname1 character varying(100),
  cur_pcp_prov_id1 character varying(18))
  RETURNS VOID AS
$$
BEGIN
  LOOP
    UPDATE patient SET birth_month = birth_month1, sex = sex1, mrn = mrn1,
      patname = patname1, cur_pcp_prov_id = cur_pcp_prov_id1 WHERE pat_id = pat_id1 AND customer_id = customer_id1;
    IF found THEN
      RETURN;
    END IF;
    BEGIN
      INSERT INTO patient(pat_id, customer_id, birth_month, sex, mrn, patname, cur_pcp_prov_id)
        VALUES (pat_id1, customer_id1, birth_month1, sex1, mrn1, patname1, cur_pcp_prov_id1);
      RETURN;
    EXCEPTION WHEN unique_violation THEN
    END;
  END LOOP;
END;
$$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION upsert_patient(character varying(100), numeric(18,0), character varying(6),
character varying(254), character varying(100), character varying(100), character varying(18))
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


INSERT INTO ruleTest.rules VALUES ('Test rule name','This is the test rule description','proc',12345,0,200,'12345678,9012345,67890123,1222222,56789876','90324023984,43987523,309753492785,53425243235','These are the details for the test rule','test only in department','test not in department'); 
INSERT INTO ruleTest.rules VALUES ('Test rule name 1','This is the test rule description 1','proc',12345,0,200,'22345678,0012345,77890123,2222222,66789876','00324023984,33987523,009753492785,33425243235','These are the details for the test rule1','test only in department1','test not in department1');
