Table: alert_setting_hist
DROP TABLE alert_setting_hist;

CREATE TABLE alert_setting_hist (
	alert_id numeric(18,0),
  customer_id numeric(18,0),
  provider_id character varying(36),
	datetime timestamp without time zone,
  category character varying(36),
  subcategory character varying(36),
  rule_id integer,
  scope character varying(36),
  action character varying(36),
  action_comment character varying(255)
)
WITH (
      OIDS=FALSE
);
ALTER TABLE public.alert_setting_hist
	OWNER TO maven;
