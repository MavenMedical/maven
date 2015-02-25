 -- Step 1:  Confirm database backend evalRules function configured for customer
 -- Step 2:  Send HTML message matching any of Step 1s ASSERT configurations (alerts fired)
 --
 --     these tests back_end function rules.evalrules is matching/returning Choosing Wisely Alerts
 --     test should be run:  (1) if any refactoring to rules functions or tables below
 --                                         (2) identify customer specific issues in alert_config…missing alerts
 --                          future enhancements:  write front-end function to pass name…and to use PG Windows functions to fill arrays
 --
 -- Key tables:  alert_config (ruleid for each alert active for customer…validation_status .GT. Zero)
 --                       evirule (row or ruleid with name of Choosing Wisely rule, age/(gender filter, and JSON not included in this test (remaining details)
 --                    trigcodes (matches on ruleid and codetype from evirule…represents procedure ordered HCPCS)
 --                   codelists (arrays of SNOMEDs required to be True or false…1st array passed to function is diagnostic…2nd problems)
 --  evalrules parameters passed
--   $1   trigger code
--   $2   code type
--   $3   age
--   $4   gender
--   $5   [encSnomeds]
--   $6   [probSnomeds]
--   $7   patient
--   $8   customer
--
--  submit bug report for composition evaluator to pass F not female
--
--  ICD 388.2 is encounter diagnosis in HTML testing file....79471008 encSnomed in this test
--  ICD 959.01 is PL in HTML file probSnomed 82271004 in problem list
-- ICD 461.9 is an unrelated SNOMED 15805002 to cause no match in encounter test
--
-- assumes rules.evirules has row with name='AAO 1', and corresponding rows in rules.trigcodes and rules.codelists
--   display content of key tables before testing rules to confirm test environment contains expected values
-- 
SELECT NOW() as Start;
-- terminology.codemap contents...for endToEnd crosswalk with  EHR-HTML
SELECT  * from terminology.codemap where code in ('388.2','959.01','461.9'); /* EXPECT  79471008,ICD-9,388.2   15805002,ICD-9,461.9  82271004,ICD-9,959.01 */
-- Add short-title, short=-description to test alert display
UPDATE rules.evirule set fullspec='{    "evidence": {        "short-title": "Choosing Wisely: Head CT for sudden hearing loss",        "short-description": "Here’s additional info on imaging for initial management of sudden hearing loss",        "long-title": "Don’t order computed tomography (CT) scan of the head/brain for sudden hearing loss.",        "long-description": "Computed tomography scanning is expensive, exposes the patient to radiation and offers no useful information that would improve initial management. CT scanning may be appropriate in patients with focal neurologic findings, a history of trauma or chronic ear disease.",        "sources": [            {                "Hyperlink": "www.choosingwidely.org",                "Abbreviation": "AAO",                "Name": "American Academy of Otolaryngolgy"            }        ]    }}' where name='AAO 1';  
--
-- evirule contents
SELECT * from rules.evirule where name='AAO 1';      /* EXPECT 5809;,AAO 1",0.00,200.00,%,HCPCS,{"details":[]}, "{    "evidence": {"short-title": "Choosing Wisely: Head CT for sudden hearing loss", "short-description": "Here’s additional info on imaging for initial management of sudden hearing loss",        "long-title": "Don’t order computed tomograph (...)"*/
 --
 -- trigcodes contents
 --
SELECT * from rules.trigcodes where ruleid=(select ruleid from rules.evirule where name='AAO 1') ;     /* EXPECT code of 70470 */
 --
 -- codelist contents
 --
SELECT * from rules.codelists where ruleid=(select ruleid from rules.evirule where name='AAO 1') ORDER BY listtype;    /* EXPECT two rows:  enc_dx,t, {79471008}  enc_pl_dx,f;{16397004,82271004} */
 --
 -- alert_config contents…truncate table
 -- 
-- reset enc_pl_dx
UPDATE rules.codelists set intlist=ARRAY[16397004,82271004] where ruleid=(select ruleid from rules.evirule where name='AAO 1') and listtype='enc_pl_dx';
-- note...change in future...if alert_config is not in safer and more segemented schema for testing
TRUNCATE alert_config;
  -- All Tests should return boolean of T
SELECT (count(*)=0)  as tst_01_AlertConfigForCustomer_Fail from rules.evalrules('70470', 'HCPCS', '11.52', 'F', ARRAY[79471008], ARRAY[1], '1235412', 1, ARRAY[]::CHARACTER[]);
 --
 -- add row to alert_config with -1 validation status
INSERT INTO alert_config(customer_id, category, rule_id, validation_status)   VALUES (1, 'CDS', (select ruleid from rules.evirule where name='AAO 1'), -1);
SELECT (count(*)=0)  as tst_02_noAlertConfigGTzero_Fail from rules.evalrules('70470', 'HCPCS', '11.52', 'F', ARRAY[79471008], ARRAY[1], '1235412', 1, ARRAY[]::CHARACTER[]);
 -- set alert_config validation status to 400…now reportable in workflow
 --
UPDATE alert_config set validation_status=400 where rule_id=(select ruleid from rules.evirule where name='AAO 1');
--
SELECT (count(*)=1) as tst_03_AlertConfigTrigCodelistMatch_Assert from rules.evalrules('70470', 'HCPCS', '11.52', 'F', ARRAY[79471008], ARRAY[1], '1235412', 1, ARRAY[]::CHARACTER[]);
SELECT (count(*)=0) as tst_04_nullEncounter_Fail from rules.evalrules('70470', 'HCPCS', '11.52', 'F', ARRAY[]::integer[], ARRAY[1], '1235412', 1, ARRAY[]::CHARACTER[]);
SELECT (count(*)=0) as tst_05_matchEncounter_Fail from rules.evalrules('70470', 'HCPCS', '11.52', 'F', ARRAY[15805002], ARRAY[1], '1235412', 1, ARRAY[]::CHARACTER[]);
SELECT (count(*)=1) as tst_06_nullProblemMatch_Assert  from rules.evalrules('70470', 'HCPCS', '11.52', 'F', ARRAY[79471008], ARRAY[]::integer[], '1235412', 1, ARRAY[]::CHARACTER[]);
SELECT (count(*)=0) as tst_07_ProblemMatch_Fail from rules.evalrules('70470', 'HCPCS', '11.52', 'F', ARRAY[79471008], ARRAY[82271004], '1235412', 1, ARRAY[]::CHARACTER[]);  /* ICD 959.01 is probSnomed 82271004 in HTML */
SELECT (count(*)=0) as tst_08_enc_in_enc_pl_Match_Fail from rules.evalrules('70470', 'HCPCS', '11.52', 'F', ARRAY[82271004,79471008], ARRAY[1], '1235412', 1, ARRAY[]::CHARACTER[]);  /* ICD 959.01 is ENC_PL_DX in EncSomed 82271004 */
SELECT NOW() as Finish;
