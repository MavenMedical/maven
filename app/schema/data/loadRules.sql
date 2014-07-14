\connect maven;

update rules.evirule set codetype ='HCPCS';

update rules.codelists set listtype='enc_pl_dx' where listtype='PLENC';

update rules.codelists set listtype='hist_dx' where listtype='DXHX';

update rules.codelists set listtype='enc_dx' where listtype='ENC';

update rules.codelists set listtype='hist_proc' where listtype='HXPX';

update rules.codelists set listtype='pl_dx' where listtype='PL';

UPDATE rules.codelists set intlist=ARRAY[16397004] where ruleid=(select ruleid from rules.evirule where name='AAO 1') and listtype='enc_pl_dx';

INSERT INTO alert_config(customer_id, category, rule_id, validation_status)   VALUES (1, 'CDS', 5809, 400);