DROP TABLE protocols.unparsed;
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