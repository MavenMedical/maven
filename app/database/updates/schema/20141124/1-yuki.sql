-- Table: user_group
-- DROP TABLE user_group;
CREATE TABLE user_group
(
  group_id serial,
  customer_id integer,
  group_name character varying,
  group_description character varying,
  status character varying(36),
  department_id character varying(255)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE user_group
  OWNER TO maven;

-- Index: ix_groupid
-- DROP INDEX ix_groupid;
CREATE INDEX ix_groupid
  ON user_group
  USING btree
  (group_id);
-- Index: ix_departmentid
-- DROP INDEX ix_departmentid;
CREATE INDEX ix_departmentid
  ON user_group
  USING btree
  (department_id, customer_id);




-- Table: user_membership
-- DROP TABLE user_membership;
CREATE TABLE user_membership
(
  membership_id serial,
  customer_id integer,
  group_id integer,
  user_id integer,
  user_name character varying,
  status character varying(36),
  begin_datetime timestamp without time zone,
  end_datetime timestamp without time zone
)
WITH (
  OIDS=FALSE
);
ALTER TABLE user_membership
  OWNER TO maven;

-- Index: ix_useridmembership
-- DROP INDEX ix_useridmembership;
CREATE INDEX ix_useridmembership
  ON user_membership
  USING btree
  (user_id);

-- Index: ix_usernamemembership
-- DROP INDEX ix_usernamemembership;
CREATE INDEX ix_usernamemembership
  ON user_membership
  USING btree
  (user_name, customer_id);

-- Index: ix_groupidmemembership
-- DROP INDEX ix_groupidmembership;
CREATE INDEX ix_groupidmembership
  ON user_membership
  USING btree
  (group_id);
