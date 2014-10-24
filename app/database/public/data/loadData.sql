\connect maven

--Add the default shared_bytes
INSERT INTO public.shared_bytes (shared, created_on) values (gen_random_bytes(256), now());

--Add the default Maven Customer so that the support user can be activated
INSERT INTO public.customer (customer_id, name) VALUES (0, 'Maven');

--Add the default Maven Support User
INSERT INTO public.users(customer_id, prov_id, user_name, official_name, display_name,
                  pw, pw_expiration, old_passwords, state, layouts, roles, ehr_state, profession)
    VALUES (0, NULL, 'SUPPORT', 'Maven Support', 'Maven Support',
            '\x243261243034244c717a616b7864454b522e2f6b586366516454552f4f6632545869694a674470574a5253733151724a624f4b6837616c3568386c36', '2015-01-17 14:14:26.7449', NULL, 'active', ARRAY[3], ARRAY['mavensupport'], 'active', 'Maven Support');

COPY public.layouts (layout_id, widget, template, element, priority) FROM stdin;
3	customerList	customerList.html	contentRow	2
2	/pathway/actionList	/pathway/treeTemplate.html	floating-right	1
2	/pathway/pathwaysList	/pathway/treeTemplate.html	floating-left	1
2	/pathway/TreeView	/pathway/treeTemplate.html	contentRow	1
1000	pathway	pathway.html	contentRow	1
3	customerCreation	customerCreation.html	contentRow	1
4	userList	userScroll.html	contentRow	3
4	topBanner	topBanner.html	fixed-topA	0
4	adminSettings	adminSettings.html	contentRow	1
2	maveninfo	maveninfo.html	side-popup	1
3	providerProfile	providerProfile.html	profile-modal	1
4	providerProfile	providerProfile.html	profile-modal	1
2	auditList	auditScroll.html	pane5-content	2
3	auditList	auditScroll.html	pane5-content	2
4	auditList	auditScroll.html	pane5-content	2
1	auditList	auditScroll.html	pane5-content	2
2	/pathway/toolbar	/pathway/toolbar.html	fixed-topB	1
2	welcome	welcome.html	welcome-modal	1
1	datepicker-calendar	datepicker-calendar.html	datepicker-modal	1
1	settings	settings.html	settings-modal	1
1	providerProfile	providerProfile.html	profile-modal	1
1	alertList	alertScroll.html	floating-right	1
2	providerProfile	providerProfile.html	profile-modal	1
3	settings	settings.html	settings-modal	1
1	patientInfo	patientInfo.html	fixed-topB	1
2	patientInfo	patientInfo.html	fixed-topB	1
1	patientSearch	patientSearch.html	fixed-topB	2
1	topBanner	topBanner.html	fixed-topA	1
2	topBanner	topBanner.html	fixed-topA	1
3	topBanner	topBanner.html	fixed-topA	1
1	patientList	patientList.html	contentRow	1
1	encounterSummary	encounterSummary.html	contentRow	2
1	orderList	orderScroll.html	contentRow	3
1	costtable	costbreakdown-table.html	contentRow	4
1	spend_histogram	spend_histogram.html	contentRow	5
\.
