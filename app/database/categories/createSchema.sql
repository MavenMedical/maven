\connect maven;

-- Name: categories; Type: SCHEMA; Schema: -; Owner: maven
CREATE SCHEMA categories;
ALTER SCHEMA categories OWNER TO maven;

/**
**************
**************
TABLES IN CATEGORIES SCHEMA
**************
**************
*/
-- Name: cost_type; Type: TABLE; Schema: categories; Owner: maven; Tablespace:
CREATE TABLE categories.cost_type (
    value integer,
    name character varying(255)
);
ALTER TABLE categories.cost_type OWNER TO maven;
ALTER TABLE ONLY categories.cost_type
    ADD CONSTRAINT costtype_pkey PRIMARY KEY (value);
CREATE INDEX ixcosttype ON categories.cost_type USING btree (value);

-- Name: validation_status; Type: TABLE; Schema: categories; Owner: maven; Tablespace:
CREATE TABLE categories.validation_status (
    value integer,
    name character varying(255)
);
ALTER TABLE categories.validation_status OWNER TO maven;
ALTER TABLE ONLY categories.validation_status
    ADD CONSTRAINT valstatus_pkey PRIMARY KEY (value);
CREATE INDEX ixvalstatus ON categories.validation_status USING btree (value);

REVOKE ALL ON SCHEMA categories FROM PUBLIC;
REVOKE ALL ON SCHEMA categories FROM maven;
GRANT ALL ON SCHEMA categories TO maven;