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
            ord_type, source, base_cost, cpt_code, cpt_version, proc_rvu_work_comp,
            proc_rvu_overhd_comp, proc_rvu_malprac_comp, proc_rvu_total_no_mod,
            rx_rxnorm_id, rx_generic_name, rx_strength, rx_form, rx_route,
            rx_thera_class, rx_pharm_class, rx_pharm_subclass, rx_simple_generic)
    VALUES (1, '5', 'clientEMR', 'CT SINUS COMPLETE W/O CONTRAST', NULL, 'active',
            'Imaging', NULL, 807.00, '76370', 'CPT', NULL,
            NULL, NULL, NULL,
            NULL, NULL, NULL, NULL, NULL,
            NULL, NULL, NULL, NULL);

INSERT INTO orderable(
            customer_id, orderable_id, system, name, description, status,
            ord_type, source, base_cost, cpt_code, cpt_version, proc_rvu_work_comp,
            proc_rvu_overhd_comp, proc_rvu_malprac_comp, proc_rvu_total_no_mod,
            rx_rxnorm_id, rx_generic_name, rx_strength, rx_form, rx_route,
            rx_thera_class, rx_pharm_class, rx_pharm_subclass, rx_simple_generic)
    VALUES (1, '2', 'clientEMR', 'IMMUNOGLOBULINS', NULL, 'active',
            'Lab', NULL, 16.14, '82784', 'CPT', NULL,
            NULL, NULL, NULL,
            NULL, NULL, NULL, NULL, NULL,
            NULL, NULL, NULL, NULL);

INSERT INTO orderable(
            customer_id, orderable_id, system, name, description, status,
            ord_type, source, base_cost, cpt_code, cpt_version, proc_rvu_work_comp,
            proc_rvu_overhd_comp, proc_rvu_malprac_comp, proc_rvu_total_no_mod,
            rx_rxnorm_id, rx_generic_name, rx_strength, rx_form, rx_route,
            rx_thera_class, rx_pharm_class, rx_pharm_subclass, rx_simple_generic)
    VALUES (1, '3', 'clientEMR', 'CEFIXIME TAB', NULL, 'active',
            'Medication', NULL, 519.14, NULL, NULL, NULL,
            NULL, NULL, NULL,
            '25033', NULL, NULL, NULL, NULL,
            NULL, NULL, NULL, NULL);

