-- Table: alert_setting_hist
-- DROP TABLE alert_setting_hist;

CREATE TABLE alert_setting_hist (
	customer_id numeric(18,0), 
	provider_id character varying(36),  
	category character varying(36), 
	subcategory character varying(36), 
	rule_id integer, 
	scope character varying(36),
	action character varying(36),
)
WITH (, , 
      OIDS=FALSE
);
ALTER TABLE public.alert_setting_hist
	OWNER TO maven;
