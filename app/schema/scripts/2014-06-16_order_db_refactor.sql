-- *************************************************************************
-- Copyright (c) 2014 - Maven Medical
-- ************************
-- AUTHOR: 'Yuki Uchino'
-- ************************
-- DESCRIPTION: Removes unnecessary tables, adds new ones (TODO - to be expanded on further at end)
-- 
-- 
-- 
-- 
-- ************************
-- ASSUMES:
-- ************************
-- SIDE EFFECTS:
-- ************************
-- LAST MODIFIED FOR JIRA ISSUE: MAV-200, MAV-188
-- *************************************************************************


CREATE TYPE ord_event as ENUM('created', 'signed', 'modified', 'canceled');
CREATE TYPE ord_source as ENUM('webservice', 'extract');
CREATE TYPE data_status as ENUM('active', 'inactive');

drop table order_event;

-- Table: order_event;

-- DROP TABLE order_event;

CREATE TABLE order_event
(
  customer_id numeric(18,0),
  order_id numeric(18,0),
  provider_id character varying(18),
  order_event ord_event,
  event_datetime timestamp without time zone,
  source ord_source,
  active_orders json[]
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.order_event
  OWNER TO maven;


CREATE TABLE order_ord
(
  customer_id numeric(18,0),
  order_id numeric(18,0),
  pat_id character varying(100),
  encounter_id character varying(100),
  ordering_provider_id character varying(18),
  auth_provider_id character varying(18),
  orderable_id numeric(18,0),
  status ord_event,
  source ord_source,
  code_id character varying(255),
  code_system character varying(255),
  order_name character varying(255),
  order_type character varying(255),
  order_cost numeric(18,2),
  order_datetime timestamp without time zone
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.order_ord
  OWNER TO maven;

-- Index: ixorder_ord

-- DROP INDEX ixorder_ord;

CREATE INDEX ixorder_ord
  ON public.order_ord
  USING btree
  (encounter_id, customer_id);

drop table orderable;
CREATE TABLE orderable
(
  customer_id numeric(18,0),
  orderable_id numeric(18,0),
  system character varying(255),
  name character varying(255),
  description character varying,
  status data_status,
  ord_type character varying(255),
  source ord_source,
  base_cost numeric(18,2),
  cpt_code character varying(20),
  cpt_version character varying(20),
  proc_rvu_work_comp numeric(18,2),
  proc_rvu_overhd_comp numeric(18,2),
  proc_rvu_malprac_comp numeric(18,2),
  proc_rvu_total_no_mod numeric(18,2),
  rx_rxnorm_id character varying(20),
  rx_generic_name character varying(255),
  rx_strength character varying(20),
  rx_form character varying(20),
  rx_route character varying(20),
  rx_thera_class character varying(20),
  rx_pharm_class character varying(20),
  rx_pharm_subclass character varying(20),
  rx_simple_generic character varying(255)
)
WITH (
    OIDS=FALSE
);

ALTER TABLE public.orderable
  OWNER TO maven;


CREATE OR REPLACE FUNCTION migrate_order_tables ()
RETURNS bool
AS $$
DECLARE
   ord_cost public.costmap;
BEGIN
   FOR ord_cost in costmap LOOP
       INSERT INTO orderable(orderable_id, system, base_cost, ord_type)
         values (ord_cost.billing_code, ord_cost.code_type, ord_cost.cost_amt, ord_cost.cost_type);
   END LOOP;
 END;
$$ LANGUAGE plpgsql;

select migrate_order_tables();

delete migrate_order_tables();

drop table orderable;

insert into orderable(orderable_id, system, base_cost, ord_type, name, status)
    values(2, 'maven', 16.14, 'Medication', 'IMMUNOGLOBULINS', 'active');

insert into orderable(orderable_id, system, base_cost, ord_type, name, status)
    values(3, 'maven', 519.14, 'Medication', 'CEFIXIME TAB', 'active');

insert into orderable(orderable_id, cpt_code, system, base_cost, ord_type, name, cpt_version, status)
  values(5, '76370', 'maven', 807.00, 'Imaging', 'CT SINUS COMPLETE W/O CONTRAST', 'CPT', 'active');
