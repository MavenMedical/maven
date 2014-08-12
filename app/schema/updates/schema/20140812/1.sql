ALTER TABLE users ADD layouts integer[];

CREATE TABLE layouts (
  id serial,
  layout_id integer,
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

CREATE INDEX ixlayout
  ON public.layouts
  USING btree
  (layout_id);