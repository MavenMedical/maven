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

-- Schema: Logging

-- DROP SCHEMA "Logging";

CREATE SCHEMA "Logging"
  AUTHORIZATION maven;

COMMENT ON SCHEMA "Logging"
  IS 'This schema is to track/log every time ana lert is fired and the content in which it was fired';


-- Table: "Logging".alerts

-- DROP TABLE "Logging".alerts;

CREATE TABLE "Logging".alerts
(
  pid character varying(20) NOT NULL,
  userid character varying(20) NOT NULL,
  encounter_id character varying(20) NOT NULL,
  dep character varying(50),
  encounter_date timestamp without time zone NOT NULL,
  alert_date timestamp without time zone NOT NULL,
  orderable character varying(50),
  provider character varying(50),
  outcome character varying(50)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE "Logging".alerts
  OWNER TO maven;

-- Index: "Logging".ixdepartment

-- DROP INDEX "Logging".ixdepartment;

CREATE INDEX ixdepartment
  ON "Logging".alerts
  USING btree
  (dep COLLATE pg_catalog."default");

-- Index: "Logging".ixencounter_date

-- DROP INDEX "Logging".ixencounter_date;

CREATE INDEX ixencounter_date
  ON "Logging".alerts
  USING btree
  (encounter_date);

-- Index: "Logging".ixpatient

-- DROP INDEX "Logging".ixpatient;

CREATE INDEX ixpatient
  ON "Logging".alerts
  USING btree
  (pid COLLATE pg_catalog."default");

-- Index: "Logging".ixuser

-- DROP INDEX "Logging".ixuser;

CREATE INDEX ixuser
  ON "Logging".alerts
  USING btree
  (userid COLLATE pg_catalog."default");

create schema ruleTest authorization maven;
-- Table: ruleTest.rules

DROP TABLE ruleTest.rules;

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

