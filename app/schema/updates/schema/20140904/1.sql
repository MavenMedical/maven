ALTER TABLE users
   ADD COLUMN ehr_state userstate;

update users set ehr_state = 'active';