INSERT INTO layouts (layout_id, widget, template, element, priority) VALUES (4, 'adminSettings', 'adminSettings.html', 'contentRow', 1);

ALTER TYPE user_role ADD VALUE 'administrator';
delete from users where user_name='admin';
insert into users (customer_id, prov_id, user_name, official_name, display_name, pw, pw_expiration, state, layouts, roles, ehr_state)
values (1, null, 'admin', 'Customer Administrator', 'Administrator',
'\x243261243034244c717a616b7864454b522e2f6b586366516454552f4f6632545869694a674470574a5253733151724a624f4b6837616c3568386c36',
'2015-01-17 14:14:26.7449', 'active', '{4}','{administrator}','active');