CREATE INDEX idxnodeactivity ON trees.activity USING btree (customer_id, canonical_id, patient_id, node_id, action);
