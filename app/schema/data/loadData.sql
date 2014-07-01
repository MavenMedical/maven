\connect maven;
--the following line should be uncommented to maintain the cost map history
--insert into public.costmaphistory (select customer_id,orderable_id,'Proc',department,cost_type,cost,'Medicare defaults',current_date from public.costmap where customer_id=-1 and code_type='HCPCS');
delete from public.costmap where customer_id=-1 and code_type='HCPCS';
delete from public.orderable where customer_id=-1 and ord_type='Proc';
\copy public.costmap from 'CostMapDefaults.csv' DELIMITER ','  null as '' CSV 
\copy public.orderable(customer_id,orderable_id,ord_type,system,name,description,status,source,base_cost,cpt_code) from 'OrderableDefaults.csv' DELIMITER ',' null as '' quote as '"' CSV

