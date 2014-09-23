DELETE FROM logins;
ALTER TABLE logins ADD COLUMN customer_id NUMERIC(18,0);
ALTER TABLE logins ALTER COLUMN customer_id SET NOT NULL;
ALTER TABLE users
   ADD COLUMN profession character varying(255);