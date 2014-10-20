ALTER TABLE audit ADD COLUMN target_customer INTEGER;
CREATE INDEX ix_orderordcustomer ON public.order_ord USING btree (customer_id);
CREATE INDEX ix_encountercustomer ON public.encounter USING btree (customer_id);
CREATE INDEX ix_patientcustomer ON public.patient USING btree (customer_id);
CREATE INDEX ix_userscustomer ON public.users USING btree (customer_id);
CREATE INDEX ix_providercustomer ON public.provider USING btree (customer_id);
CREATE INDEX ix_alertcustomer ON public.alert USING btree (customer_id);
CREATE INDEX ix_alertsettingcustomer ON public.alert_setting_hist USING btree (customer_id);

