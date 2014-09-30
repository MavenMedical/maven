CREATE EXTENSION pgcrypto;
CREATE TABLE shared_bytes ( shared bytea, created_on time );
INSERT INTO shared_bytes (shared, created_on) values (gen_random_bytes(64), now());
ALTER TABLE shared_bytes OWNER TO maven;
