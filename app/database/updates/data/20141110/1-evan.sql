delete from public.layouts * where widget = '/pathway/triggerEditor';
insert into public.layouts (layout_id, widget, template, element, priority) values (2, '/pathway/triggerEditor', '/pathway/RuleWizardPage.html', 'contentRow', 1);