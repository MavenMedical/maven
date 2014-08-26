INSERT INTO customer(
            customer_id, name, abbr, license_type, license_exp, clientapp_config)
    VALUES (4, 'Medstar', 'MDSTR', 1, '2015-07-25', NULL);

INSERT INTO customer(
            customer_id, name, abbr, license_type, license_exp, clientapp_config)
    VALUES (5, 'Chesapeake Urology Asssociates', 'CUA', 1, '2015-08-20', '{"emr": "Allscripts Professional", "version": "14.0"}');

INSERT INTO alert_config(
            customer_id, department, category, rule_id, validation_status,
            provide_optouts)
    VALUES (5, -1, 'PATHWAY', NULL, ?,
            ?);