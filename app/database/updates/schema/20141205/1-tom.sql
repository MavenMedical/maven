ALTER TABLE trees.activity ADD COLUMN canonical_id INTEGER;
CREATE INDEX idxpatientpathway ON trees.activity USING btree (patient_id, canonical_id, datetime);
