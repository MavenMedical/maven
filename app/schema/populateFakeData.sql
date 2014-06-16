--
-- Insert customer data
--
INSERT INTO customer(
            customer_id, name, abbr, license_type, license_exp)
    VALUES (1, 'Veterans Affairs (VA) Maryland Health Care System', 'VAM', 1, '2015-03-12');

INSERT INTO customer(
            customer_id, name, abbr, license_type, license_exp)
    VALUES (2, 'Catholic Health Services of Long Island', 'CHSLI', 1, '2015-03-12');

INSERT INTO customer(
            customer_id, name, abbr, license_type, license_exp)
    VALUES (3, 'Johns Hopkins University Hospital', 'JHU', 1, '2015-03-12');



--
-- Create a couple of fake departments
--
INSERT INTO department(
            department_id, dep_name, specialty, location, customer_id)
    VALUES (286, 'VAM 4S MED/SURG', 'Med/Surg', 'Main Campus', 1);

INSERT INTO department(
            department_id, dep_name, specialty, location, customer_id)
    VALUES (3049173412, 'JHU 4S MED/SURG', 'Med/Surg', 'Main Campus', 2);




--
-- Add some fake historical procedure data
--
INSERT INTO medicalprocedure(
            proc_id, customer_id, proc_name, cpt_code, base_charge, rvu_work_compon,
            rvu_overhd_compon, rvu_malprac_compon, rvu_total_no_mod)
    VALUES (900601, 2, 'JJB BLOOD DRAW A', '36415', '13.79', NULL,
            NULL, NULL, NULL);


--
-- Add some fake historical patients
--
INSERT INTO patient(
            pat_id, customer_id, birthdate, sex, mrn, patname, cur_pcp_prov_id)
    VALUES ('1296573026', 2, '1982-10-02', 'Male', '157662', 'Aardvark, Adam', '');



--
-- Populate costmap table with data
--
INSERT INTO costmap(dep_id, customer_id, billing_code, code_type, cost_amt,
            cost_type)
    VALUES (286, 1, '2', 'maven', 16.14,
            'med');

INSERT INTO costmap(dep_id, customer_id, billing_code, code_type, cost_amt,
            cost_type)
    VALUES (286, 1, '3', 'maven', 519.14,
            'med');

INSERT INTO costmap(dep_id, customer_id, billing_code, code_type, cost_amt,
            cost_type)
    VALUES (286, 1, '76370', 'maven', 807.00,
            'imaging');


INSERT INTO sleuth_rule(
            rule_id, customer_id, dep_id, code_trigger, code_trigger_type,
            name, tag_line, description, rule_details)
    VALUES (1, 1, 286, '76370', 'CPT',
            'Sinusitis', 'Dont order CT Scans for uncomplicated acute sinusitis', 'Viral infections cause the majority of acute rhinosinusitis and only 0.5-2 percent progress to bacterial infections', '{"details":
    [
        {"type": "encounter_dx", "exists": true, "snomed": 36971009},
        {"type": "encounter_dx", "exists": false, "snomed": 40055000},
        {"type": "encounter_dx", "exists": false, "snomed": 195788001},
        {"type": "encounter_dx", "exists": false, "snomed": 425011002},
        {"type": "encounter_dx", "exists": false, "snomed": 371127003},
        {"type": "encounter_dx", "exists": false, "snomed": 232390009},
        {"type": "encounter_dx", "exists": false, "snomed": 86406008},
        {"type": "problemlist_dx", "exists": false, "snomed": 86406008},
        {"type": "problemlist_dx", "exists": false, "snomed": 414030009},
        {"type": "problemlist_dx", "exists": false, "snomed": 190905008},
        {"type": "lab", "exists": true, "snomed": "43396009", "start": "-30", "end": "0", "operator": "<", "value": "8"},
        {"type": "med", "exists": false, "rxnorm": "1"}
    ]
}');


--
-- Populate Sleuth Evidence Table
--
INSERT INTO sleuth_evidence(
            customer_id, sleuth_rule, short_name, name, description,
            source, source_url)
    VALUES (1, 1, 'Sinusitis', 'Choosing Wisely: Sinusitis', 'Viral infections cause the majo',
            'Choosing Wisely', 'http://www.choosingwisely.org/doctor-patient-lists/american-academy-of-allergy-asthma-immunology/');



--
-- Populate Observation table with some data (that would have come in from the historical dump as well as the HL7 Lab feed)
--
INSERT INTO observation(
            customer_id, encounter_id, order_id, pat_id, status, result_time,
            comments, numeric_result, units, reference_low, reference_high,
            reference_unit, method, loinc_code, snomed_id, code_id, code_system,
            name, component_id, external_name, base_name, common_name)
    VALUES (1, '5|76|3140325', 3, '1235412', 'final', '2014-05-25T14:22:00',
            'Hemoglobin A1c is relatively low for this patient', 7.4, '%', 1, 16,
            '%', NULL, '4548-4', NULL, NULL, NULL,
            'Hemoglobin A1c', 1209479872, 'Hb A1c', 'Hb A1c', 'Hemoglobin A1c');


--
-- Populate alert table
--
INSERT INTO alert(
            customer_id, provider_id, pat_id, encounter_id, category,
            status, order_id, code_trigger, code_trigger_type, cds_rule,
            alert_datetime, short_title, long_title, short_desc, long_desc,
            outcome, saving)
    VALUES (1,'JHU1093124','1235412','5|76|3140325','cost',NULL,NULL,NULL,NULL,NULL,'2014-06-12 17:23:49','Encounter Cost: 1350.0',NULL,NULL,'IMMUNOGLOBULINS: $20 CEFIXIME TAB : $520 CT SINUS COMPLETE W/O CONTRAST: $810',NULL,NULL);

INSERT INTO alert(
            customer_id, provider_id, pat_id, encounter_id, category,
            status, order_id, code_trigger, code_trigger_type, cds_rule,
            alert_datetime, short_title, long_title, short_desc, long_desc,
            outcome, saving)
    VALUES (1,'JHU1093124','1235412','5|76|3140325','dup_ord',NULL,NULL,'3','maven',NULL,'2014-06-12 17:23:49.835404','Duplicate Order: CEFIXIME TAB ','','Clinical observations are available for a duplicate order recently placed.','Hemoglobin A1c: 7.4 % (2014-05-25 14:22:00)',NULL,16.14);


INSERT INTO alert(
            customer_id, provider_id, pat_id, encounter_id, category,
            status, order_id, code_trigger, code_trigger_type, cds_rule,
            alert_datetime, short_title, long_title, short_desc, long_desc,
            outcome, saving)
    aVALUES (1,'JHU1093124','1235412','5|76|3140325','cds',NULL,NULL,'76370',NULL,1,'2014-06-12 17:23:49.908729','Sinusitis','Dont order CT Scans for uncomplicated acute sinusitis','','Viral infections cause the majority of acute rhinosinusitis and only 0.5-2 percent progress to bacterial infections',NULL,807.12);