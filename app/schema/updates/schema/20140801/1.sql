DROP TABLE alert_setting_hist;

create type actiontype as enum ('like', 'dislike', 'opt in', 'opt out');
CREATE TABLE alert_setting_hist (
	alert_id numeric(18,0),
	user_id serial,
  customer_id numeric(18,0),
	datetime timestamp without time zone,
  category character varying(36),
  subcategory character varying(36),
  rule_id integer,
  scope character varying(36),
  action actiontype,
  action_comment character varying(255)
)
WITH (
      OIDS=FALSE
);
ALTER TABLE public.alert_setting_hist
        OWNER TO maven;