ALTER TABLE users ADD layouts integer[];

CREATE TABLE layouts (
  id serial,
  layout_id numeric(18,0),
  widget character varying(36),
  template character varying(36),
  element character varying(36),
  priority integer
)
WITH (
      OIDS=FALSE
);
ALTER TABLE public.layouts
        OWNER TO maven;