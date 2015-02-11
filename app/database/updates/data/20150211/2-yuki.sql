INSERT INTO alert_config(
            customer_id, department, category, rule_id, validation_status,
            provide_optouts, priority)
    VALUES (1, -1, 'COST', NULL, 400, NULL, 101);

INSERT INTO orderable(
            customer_id, orderable_id, ord_type, system, name, description,
            status, source, cpt_code, cpt_version, proc_rvu_work_comp, proc_rvu_overhd_comp,
            proc_rvu_malprac_comp, proc_rvu_total_no_mod, rx_rxnorm_id, rx_generic_name,
            rx_strength, rx_form, rx_route, rx_thera_class, rx_pharm_class,
            rx_pharm_subclass, rx_simple_generic);

INSERT INTO transparent.costmap(
        customer_id, code, code_type, department, cost_type, orderable_id,
        cost)
VALUES (1,'5','maven','-1',100,'5',3.72);
