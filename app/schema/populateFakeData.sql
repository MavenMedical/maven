-- 
-- Insert fake user
--
INSERT INTO users(
       user_id, customer_id, prov_id, user_name, official_name, display_name, pw, pw_expiration, state)
   VALUES (1, 1, 'JHU1093124', 'maven', 'Maven', 'Dr Maven', 
           '$2a$04$LqzakxdEKR./kXcfQdTU/Of2TXiiJgDpWJRSs1QrJbOKh7al5h8l6', now() + '180 days'::INTERVAL, 'active');


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
-- Add some fake historical patients
--
INSERT INTO patient(
            pat_id, customer_id, birthdate, sex, mrn, patname, cur_pcp_prov_id)
    VALUES ('1296573026', 2, '1982-10-02', 'Male', '157662', 'Aardvark, Adam', '');


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
    VALUES (1, '5|76|3140325', '142', '1235412', 'final', '2014-05-25T14:22:00',
            'Hemoglobin A1c is relatively low for this patient', 7.4, '%', 1, 16,
            '%', NULL, '4548-4', NULL, NULL, NULL,
            'Hemoglobin A1c', 1209479872, 'Hb A1c', 'Hb A1c', 'Hemoglobin A1c');


--
-- Populate Orderable table with some data
--
INSERT INTO orderable(
            customer_id, orderable_id, system, name, description, status,
            ord_type, source, cpt_code, cpt_version, proc_rvu_work_comp,
            proc_rvu_overhd_comp, proc_rvu_malprac_comp, proc_rvu_total_no_mod,
            rx_rxnorm_id, rx_generic_name, rx_strength, rx_form, rx_route,
            rx_thera_class, rx_pharm_class, rx_pharm_subclass, rx_simple_generic)
    VALUES (1, '5', 'clientEMR', 'CT SINUS COMPLETE W/O CONTRAST', NULL, 'active',
            'Imaging', NULL, '76370', 'HCPCS', NULL,
            NULL, NULL, NULL,
            NULL, NULL, NULL, NULL, NULL,
            NULL, NULL, NULL, NULL);

INSERT INTO orderable(
            customer_id, orderable_id, system, name, description, status,
            ord_type, source, cpt_code, cpt_version, proc_rvu_work_comp,
            proc_rvu_overhd_comp, proc_rvu_malprac_comp, proc_rvu_total_no_mod,
            rx_rxnorm_id, rx_generic_name, rx_strength, rx_form, rx_route,
            rx_thera_class, rx_pharm_class, rx_pharm_subclass, rx_simple_generic)
    VALUES (1, '18724', 'clientEMR', 'CT Scan Head', NULL, 'active',
            'Imaging', NULL, '70470', 'HCPCS', NULL,
            NULL, NULL, NULL,
            NULL, NULL, NULL, NULL, NULL,
            NULL, NULL, NULL, NULL);

INSERT INTO orderable(
            customer_id, orderable_id, system, name, description, status,
            ord_type, source, cpt_code, cpt_version, proc_rvu_work_comp,
            proc_rvu_overhd_comp, proc_rvu_malprac_comp, proc_rvu_total_no_mod,
            rx_rxnorm_id, rx_generic_name, rx_strength, rx_form, rx_route,
            rx_thera_class, rx_pharm_class, rx_pharm_subclass, rx_simple_generic)
    VALUES (1, '2', 'clientEMR', 'IMMUNOGLOBULINS', NULL, 'active',
            'Lab', NULL, '82784', 'HCPCS', NULL,
            NULL, NULL, NULL,
            NULL, NULL, NULL, NULL, NULL,
            NULL, NULL, NULL, NULL);

INSERT INTO orderable(
            customer_id, orderable_id, system, name, description, status,
            ord_type, source, cpt_code, cpt_version, proc_rvu_work_comp,
            proc_rvu_overhd_comp, proc_rvu_malprac_comp, proc_rvu_total_no_mod,
            rx_rxnorm_id, rx_generic_name, rx_strength, rx_form, rx_route,
            rx_thera_class, rx_pharm_class, rx_pharm_subclass, rx_simple_generic)
    VALUES (1, '7', 'clientEMR', 'CT Pelvic w/ Contrast', NULL, 'active',
            'Imaging', NULL, '72191', 'HCPCS', NULL,
            NULL, NULL, NULL,
            NULL, NULL, NULL, NULL, NULL,
            NULL, NULL, NULL, NULL);

INSERT INTO orderable(
            customer_id, orderable_id, system, name, description, status,
            ord_type, source, cpt_code, cpt_version, proc_rvu_work_comp,
            proc_rvu_overhd_comp, proc_rvu_malprac_comp, proc_rvu_total_no_mod,
            rx_rxnorm_id, rx_generic_name, rx_strength, rx_form, rx_route,
            rx_thera_class, rx_pharm_class, rx_pharm_subclass, rx_simple_generic)
    VALUES (1, '3', 'clientEMR', 'CEFIXIME TAB', NULL, 'active',
            'Medication', NULL, NULL, NULL, NULL,
            NULL, NULL, NULL,
            '25033', NULL, NULL, NULL, NULL,
            NULL, NULL, NULL, NULL);

INSERT INTO costmap(
            customer_id, code, code_type, department, cost_type, orderable_id,
            cost)
    VALUES (1, '76370', 'HCPCS', '286', 'Procedure Cost', '5',
            807.00);

INSERT INTO costmap(
            customer_id, code, code_type, department, cost_type, orderable_id,
            cost)
    VALUES (1, '70470', 'HCPCS', '-1', 'Procedure Cost', '18724',
            792.78);

INSERT INTO costmap(
            customer_id, code, code_type, department, cost_type, orderable_id,
            cost)
    VALUES (1, '72191', 'HCPCS', '286', 'Procedure Cost', '72191',
            742.79);

INSERT INTO costmap(
            customer_id, code, code_type, department, cost_type, orderable_id,
            cost)
    VALUES (1, '25033', 'rxnorm', '-1', 'Procedure Cost', '3',
            519.14);

INSERT INTO costmap(
            customer_id, code, code_type, department, cost_type, orderable_id,
            cost)
    VALUES (1, '82784', 'HCPCS', '286', 'Procedure Cost', '2',
            16.14);

INSERT INTO rules.evirule(
            ruleid, name, minage, maxage, sex, codetype, fullspec, comments,
            remainingdetails)
    VALUES (5, 'ACR 5', 0.00, 200.00, '%', 'CPT', '{"details":[{"id":0,"type":"historic_dx","exists":false,"snomed":445039006, "frame_min":-100000, "frame_max":0},{"id":1,Age:15:200}]}', NULL,
            '{"details":[{"id":0,"type":"encounter_dx","exists":false, "snomed":95659007},{"id":1,"type":"encounter_dx","exists":false, "snomed":95660002},{"id":2,"type":"encounter_dx","exists":false, "snomed":41413006},{"id":3,"type":"historic_dx","exists":false,"snomed":26544005, "frame_min":-100000, "frame_max":0},{"id":4,"type":"historic_dx","exists":false,"snomed":87486003, "frame_min":-100000, "frame_max":0},{"id":5,"type":"historic_dx","exists":false,"snomed": 80910005 , "frame_min":-100000, "frame_max":0},{"id":6,"type":"historic_dx","exists":false,"snomed":74732009, "frame_min":-100000, "frame_max":0},{"id":7,"type":"historic_dx","exists":false,"snomed":20262006, "frame_min":-100000, "frame_max":0},{"id":8,"type":"historic_dx","exists":false,"snomed":128613002, "frame_min":-100000, "frame_max":0},{"id":9,"type":"historic_dx","exists":false,"snomed":15758002, "frame_min":-100000, "frame_max":0},{"id":10,"type":"historic_dx","exists":false,"snomed":106150003, "frame_min":-100000, "frame_max":0},{"id":11,"type":"historic_dx","exists":false,"snomed":55342001, "frame_min":-100000, "frame_max":0},{"id":12,"type":"problem_list","exists":false,"snomed":118185001},{"id":13,"type":"problem_list","exists":false,"snomed":86406008},{"id":14,"type":"problem_list","exists":false,"snomed":271730003},{"id":15,"type":"encounter_dx","exists":false,"snomed": 386661006},{"id":16,"type":"encounter_dx","exists":false,"snomed": 82271004},{"id":17,"type":"lab","result":55,"relation":"<","default":true, "loinc": "43402-7","frame_min":-1, "frame_max":0}]}');


INSERT INTO alert_config(
            customer_id, department, category, rule_id, validation_status,
            provide_optouts)
    VALUES (1, NULL, 'cds', 5, 100,
            NULL);