CREATE TABLE audit (
  id serial,
  datetime timestamp without time zone,
  user_id integer,
  patient_id character varying(100),
	action character varying(36),
  data_type character varying(36)
)
WITH (
      OIDS=FALSE
);
ALTER TABLE public.audit
        OWNER TO maven;

CREATE INDEX ixaudit
  ON public.audit
  USING btree
  (user_id);