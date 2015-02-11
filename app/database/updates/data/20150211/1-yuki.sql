INSERT INTO orderable(
            customer_id, orderable_id, ord_type, system, name, description,
            status, source, cpt_code, cpt_version, proc_rvu_work_comp, proc_rvu_overhd_comp,
            proc_rvu_malprac_comp, proc_rvu_total_no_mod, rx_rxnorm_id, rx_generic_name,
            rx_strength, rx_form, rx_route, rx_thera_class, rx_pharm_class,
            rx_pharm_subclass, rx_simple_generic)
    VALUES (1,'76370','Proc','','CT SINUS COMPLETE W/O CONTRAST','','','HCPCS','76370','HCPCS',NULL,NULL,NULL,NULL,'','','','','','','','','');

INSERT INTO orderable(
            customer_id, orderable_id, ord_type, system, name, description,
            status, source, cpt_code, cpt_version, proc_rvu_work_comp, proc_rvu_overhd_comp,
            proc_rvu_malprac_comp, proc_rvu_total_no_mod, rx_rxnorm_id, rx_generic_name,
            rx_strength, rx_form, rx_route, rx_thera_class, rx_pharm_class,
            rx_pharm_subclass, rx_simple_generic)
    VALUES (1,'1','Med','','CEFIXIME TAB','','','maven','1','maven',NULL,NULL,NULL,NULL,'','','','','','','','','');

INSERT INTO orderable(
            customer_id, orderable_id, ord_type, system, name, description,
            status, source, cpt_code, cpt_version, proc_rvu_work_comp, proc_rvu_overhd_comp,
            proc_rvu_malprac_comp, proc_rvu_total_no_mod, rx_rxnorm_id, rx_generic_name,
            rx_strength, rx_form, rx_route, rx_thera_class, rx_pharm_class,
            rx_pharm_subclass, rx_simple_generic)
    VALUES (1,'2','Proc','','IMMUNOGLOBULINS','','','maven','2','maven',NULL,NULL,NULL,NULL,'','','','','','','','','');

1,'76370','Proc','','CT SINUS COMPLETE W/O CONTRAST','','','HCPCS','76370','HCPCS',NULL,NULL,NULL,NULL,'','','','','','','','',''


INSERT INTO transparent.costmap(
            customer_id, code, code_type, department, cost_type, orderable_id,
            cost)
    VALUES (1,'2','HCPCS','-1',100,'2',10.14);


INSERT INTO transparent.costmap(
            customer_id, code, code_type, department, cost_type, orderable_id,
            cost)
    VALUES (1,'76370','HCPCS','-1',100,'76370',812.47);

INSERT INTO transparent.costmap(
            customer_id, code, code_type, department, cost_type, orderable_id,
            cost)
    VALUES (1,'100581231','rxnorm','-1',100,'100581231',72.77);
