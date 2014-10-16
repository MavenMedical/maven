-- Table: trees.activity
-- DROP TABLE trees.activity;
CREATE TABLE trees.activity
(
  activity_id serial NOT NULL,
  customer_id numeric(18,0),
  user_id integer,
  patient_id character varying(100),
  protocol_id integer,
  node_id integer,
  datetime timestamp without time zone,
  action character varying(32)
)
WITH (OIDS=FALSE);
ALTER TABLE trees.activity
  OWNER TO maven;