-- Name: followuptask; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE followuptask (
    task_id serial NOT NULL,
    customer_id integer,
    author_id integer,
    user_id integer,
    patient_id character varying(100),
    delivery character varying(32),
    status character varying(32),
    due timestamp without time zone,
    expire timestamp without time zone,
    msg_subject character varying(255),
    msg_body character varying
);
ALTER TABLE public.followuptask OWNER TO maven;
CREATE INDEX ixuserfutask ON followuptask USING btree (author_id);
CREATE INDEX ixpatfutask ON followuptask USING btree (customer_id, patient_id);