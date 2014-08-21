update users set roles = ARRAY['provider', 'supervisor']::user_role[];
insert into users(customer_id, user_name, official_name, display_name, pw, pw_expiration, state, layouts, roles) select '0', 'support', 'Maven Employee', 'Maven Support', pw, pw_expiration, state, '{ 3 }', ARRAY['mavensupport']::user_role[] from users where user_name='maven';
insert into layouts (layout_id, widget, template, element, priority) values (3, 'topBanner', 'topBanner.html', 'fixed-topA-1-1', 1);
insert into layouts (layout_id, widget, template, element, priority) values (3, 'settings', 'settings.html', 'settings-modal', 1);

