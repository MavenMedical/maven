DROP SCHEMA IF EXISTS protocols CASCADE;

CREATE SCHEMA protocols
  AUTHORIZATION maven;
;
CREATE SEQUENCE protocols.unparsed_pathid_seq
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE protocols.unparsed_pathid_seq
  OWNER TO maven;


CREATE TABLE protocols.steps
(
  pathid integer,
  stepposition integer,
  stepparent integer,
  stepname character varying(200)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE protocols.steps
  OWNER TO maven;

CREATE TABLE protocols.unparsed
(
  pathid serial NOT NULL,
  "JSONSpec" text,
  "pathName" character varying(100)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE protocols.unparsed
  OWNER TO maven;