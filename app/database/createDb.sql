create user maven password 'temporary' SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN;

CREATE DATABASE maven
  WITH OWNER = maven
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'en_US.utf8'
       LC_CTYPE = 'en_US.utf8'
       CONNECTION LIMIT = -1;

\c maven

-- Schema: public
-- DROP SCHEMA public;
CREATE SCHEMA public
  AUTHORIZATION postgres;
GRANT ALL ON SCHEMA public TO maven;
GRANT ALL ON SCHEMA public TO public;


/**
**************
EXTENSIONS
**************
*/
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner:
CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner:
COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';

-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner:
CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner:
COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';
