INSERT INTO customer(
            customer_id, name, abbr, license_type, license_exp)
    VALUES (1, 'Veterans Affairs (VA) Maryland Health Care System', 'VAM', 1, '2015-03-12');

INSERT INTO customer(
            customer_id, name, abbr, license_type, license_exp)
    VALUES (2, 'Johns Hopkins University Hospital', 'JHU', 1, '2015-03-12');

INSERT INTO department(
            department_id, dep_name, specialty, location, customer_id)
    VALUES (286, 'VAM 4S MED/SURG', 'Med/Surg', 'Main Campus', 1);

INSERT INTO department(
            department_id, dep_name, specialty, location, customer_id)
    VALUES (3049173412, 'JHU 4S MED/SURG', 'Med/Surg', 'Main Campus', 2);


INSERT INTO medicalprocedure(
            proc_id, customer_id, proc_name, cpt_code, base_charge, rvu_work_compon,
            rvu_overhd_compon, rvu_malprac_compon, rvu_total_no_mod)
    VALUES (900601, 2, 'JJB BLOOD DRAW A', '36415', '13.79', NULL,
            NULL, NULL, NULL);


INSERT INTO patient(
            pat_id, customer_id, birth_month, sex, mrn, patname, cur_pcp_prov_id)
    VALUES ('1296573026', 2, '06', 'Male', '157662', 'Aardvark, Adam', '');


INSERT INTO procedureorder(
            orderid, pat_id, csn, customer_id, ordering_date, ordering_time,
            order_type, cpt_code, description, order_class, authrzing_prov_id)
    VALUES (7019528, '1296573026', '2139930', 2, '7/20/2012', NULL,
            'MEDICAL IMAGING', '36415', NULL, NULL, '801468');

INSERT INTO costmap(
            costmap_id, dep_id, customer_id, billing_code, code_type, cost_amt,
            cost_type)
    VALUES (1, 286, 1, 1, 'maven', 94.03,
            'med');

INSERT INTO costmap(
            costmap_id, dep_id, customer_id, billing_code, code_type, cost_amt,
            cost_type)
    VALUES (6, 286, 1, 4, 'maven', 519.14,
            'imaging');