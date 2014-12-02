-- Index: ix_groupcustomerid
-- DROP INDEX ix_groupcustomerid;
CREATE INDEX ix_groupcustomerid
  ON user_group
  USING btree
  (customer_id);