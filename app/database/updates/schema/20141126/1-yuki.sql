-- Table: categories.log_tag
-- DROP TABLE categories.log_tag;
CREATE TABLE categories.log_tag
(
  value serial PRIMARY KEY,
  name character varying(255)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE categories.log_tag
  OWNER TO maven;

-- Index: ix_logtagid
-- DROP INDEX ix_logtagid;
CREATE INDEX ix_logtagid
  ON categories.log_tag USING btree
  (value);


-- Table: log
-- DROP TABLE log;
CREATE TABLE log
(
  log_id serial PRIMARY KEY,
  customer_id integer,
  log_datetime timestamp without time zone,
  username character varying,
  device character varying,
  tags integer[],
  body character varying
)
WITH (
  OIDS=FALSE
);
ALTER TABLE log
  OWNER TO maven;

-- Index: ix_groupid
-- DROP INDEX ix_groupid;
CREATE INDEX ix_logid
  ON log  USING btree
  (log_id);

-- Index: ix_customeridlog
-- DROP INDEX ix_customeridlog;
CREATE INDEX ix_customeridlog
  ON log
  USING btree
  (customer_id);