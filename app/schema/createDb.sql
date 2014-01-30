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

)
WITH (
  OIDS=FALSE
);
ALTER TABLE terminology.codemap
  OWNER TO maven;



-- Table: terminology.concept

-- DROP TABLE terminology.concept;

CREATE TABLE terminology.concept
(

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

)
WITH (
  OIDS=FALSE
);
ALTER TABLE terminology.relationships
  OWNER TO maven;
-- Table: terminology.snomedmap

-- DROP TABLE terminology.snomedmap;

CREATE TABLE terminology.snomedmap
(

)
WITH (
  OIDS=FALSE
);
ALTER TABLE terminology.snomedmap
  OWNER TO maven;

create index ixConceptActiveConceptId on Concept(Id,active);
create index ixCodeMap on codeMap (SnomedId,code);
create index ixCodeMapCodes on CodeMap(code,CodeType);
Create Index ixRelationships on Relationships(SourceId,TypeId,DestinationId);
create index ixRelationshipsDest on Relationships(destinationId,typeid,SourceId);
Create index ixDescriptionsConcept on Descriptions(ConceptId,Active);

