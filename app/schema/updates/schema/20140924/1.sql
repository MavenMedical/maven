-- Table: user_pref
-- DROP TABLE: users;

CREATE TABLE user_pref
(
  customer_id numeric(18,0) NOT NULL,
  user_name character varying(100),
  notify_primary character varying(32),
  notify_secondary character varying(32)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE users
  OWNER TO maven;