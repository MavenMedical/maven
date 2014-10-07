/****************************
Index for optimizing the below heavily used query:
SELECT validation_status,department,category,rule_id,provide_optouts 
FROM alert_config 
WHERE (customer_id=12 or customer_id=-1) AND category='COST' AND (department= -1 or department='-1') 
ORDER BY customer_id 
DESC, department DESC LIMIT 1;
*******************************************/
create index IX_AlertConfigCustCatDep on public.alert_config(customer_id,category,department);


/*******************************************************
Index for optimizing this heavily used query
SELECT audit.device,audit.id,audit.action,audit.patient,audit.username,audit.datetime,audit.details 
FROM public."audit" 
WHERE audit.username = 'DEMOSCRIPTS' 
AND audit.customer = 12 
ORDER BY audit.datetime DESC  LIMIT 5 OFFSET 0;
*********************************************************/
create index IX_AuditCustUserDate on public.audit(customer,username,datetime);

/*******************************************************
Index for optimizing this heavily used query
upsert_condition
*********************************************************/
create index IX_ConditionEncCust on public.condition(encounter_id,customer_id);


/*******************************************************
Indexes for optimizing this heavily used query and helping PK enforcement
create index IX_ConditionEncCust on public.condition(encounter_id,customer_id);
SELECT users.user_id,users.official_name,users.roles,users.display_name,...
FROM users LEFT JOIN customer on users.customer_id = customer.customer_id 
WHERE users.customer_id = '6' AND users.user_name = UPPER('CLIFFHUX');
*********************************************************/
create index IxUserCustUser on public.users(user_name,customer_id);
create index PK_USers on public.users(user_id);


