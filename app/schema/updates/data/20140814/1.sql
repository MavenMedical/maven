insert into users(customer_id, prov_id, user_name, official_name, display_name, pw, pw_expiration, state, layouts) select '2', '10041', 'cliffhux', 'Heathcliff Huxtable', 'Dr. Huxtable', pw, pw_expiration, state, '{ 2 }' from users where user_id=1;
insert into layouts (id, layout_id, widget, template, element, priority) select 13, 2, widget, template, element, priority from layouts where widget='topBanner';
insert into layouts (id, layout_id, widget, template, element, priority) select 14, 2, widget, template, element, priority from layouts where widget='providerProfile';
insert into layouts (id, layout_id, widget, template, element, priority) select 15, 2, widget, template, element, priority from layouts where widget='encounterSummary';
insert into layouts (id, layout_id, widget, template, element, priority) values (16, 2, 'maveninfo', 'maveninfo.html', 'floating-right', 1);
insert into layouts (id, layout_id, widget, template, element, priority) values (17, 2, 'pathway', 'pathway.html', 'rowA-1-1', 1);
