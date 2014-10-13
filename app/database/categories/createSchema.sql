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

-- Name: validation_status; Type: TABLE; Schema: categories; Owner: maven; Tablespace:
CREATE TABLE categories.validation_status (
    value integer,
    name character varying(255)
);
ALTER TABLE categories.validation_status OWNER TO maven;