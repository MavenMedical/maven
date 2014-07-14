\connect maven;
/******************************
CostMap Data
The creation of the costmap data starts by importing the VA Contract prices and the NADAC prices.
Then you run the below SQL to get the calculated drug prices. 
   	update test.vaprices set pkg=upper(pkg);

	insert into costmap 
	select distinct -1 cust
	,ndc_1||'-'||ndc_2||'-'||ndc_3 code
	,'NDC' codetype
	,-1dept 
	,case unit when 'MG' then -352 when 'GM' then -352 when 'ML' then -351 else -350 end costtype
	,ndc_1||'-'||ndc_2||'-'||ndc_3 ordid
	,case unit when 'MG' then 1000*price_per else price_per end cst
	from (select
	cast(multiplier as numeric(18,9))*cast(a.number as numeric(18,9)) total
	,fss_price/(cast(multiplier as numeric(18,9))*cast(a.number as numeric(18,9))) price_per
	,case units when 'ML' then 'ML' when 'MG' then 'MG' when 'GM' then 'GM' else 'EA' end unit
	,fss_price
	,*
	from 
	(
	select
	coalesce(replace(substring(pkg from '[0-9,\.]*X'),'X',''),'1') multiplier
	,coalesce(replace(pkg,substring(pkg from '[0-9,\.]*X'),''),pkg) leftover 
	,replace(substring(coalesce(replace(pkg,substring(pkg from '[0-9,\.]*X'),''),pkg) from '[0-9,\.]*' ),',','') number
	,coalesce(trim(replace(coalesce(replace(pkg,substring(pkg from '[0-9,\.]*X'),''),pkg),substring(coalesce(replace(pkg,substring(pkg from '[0-9,\.]*X'),''),pkg) from '[0-9,\.]*' ),'')),'EA') units
	,*
	from test.vaprices
	) a
	where number!='' and multiplier!=''
	and fss_price>0
	and units in ('ML','MG','UD','','GM')
	)b;

	--set enable_seqscan=true
	insert into costmap
	select -1,c.ndc,'NDC',-1,a.cost_type-100,c.ndc,a.cost
	from costmap a
	inner join terminology.rxsnomeds b on a.code=b.ndc and a.code_type='NDC'
	inner join terminology.rxsnomeds c on c.snomed=b.snomed;

*******************************/

--the following line should be uncommented to maintain the cost map history
--insert into public.costmaphistory (select customer_id,orderable_id,'Proc',department,cost_type,cost,'Medicare defaults',current_date from public.costmap where customer_id=-1 and code_type='HCPCS');
delete from public.costmap where customer_id=-1;
delete from public.orderable where customer_id=-1;
\copy public.costmap from 'CostMapDefaults.csv' DELIMITER ','  null as '' CSV 
\copy public.orderable(customer_id,orderable_id,ord_type,system,name,description,status,source,cpt_code,cpt_version) from 'OrderableDefaults.csv' DELIMITER ',' null as '' quote as '"' CSV

--insert cost type values
insert into categories.cost_type values (-151, 'NADAC Cost (ML)');
insert into categories.cost_type values (-150, 'NADAC Cost (EA)');
insert into categories.cost_type values (-152, 'NADAC Cost (GM)');
insert into categories.cost_type values (-100, 'Medicare Charge Average');
insert into categories.cost_type values (-200, 'Medicare Payment Average');
insert into categories.cost_type values (-300, 'Medicare Allowed Average');
insert into categories.cost_type values (-251, 'NADAC Calculated Cost (ML)');
insert into categories.cost_type values (-250, 'NADAC Calculated Cost (EA)');
insert into categories.cost_type values (-252, 'NADAC Calculated Cost (GM)');
insert into categories.cost_type values (-351, 'VA Contract Cost (ML)');
insert into categories.cost_type values (-350, 'VA Contract Cost (EA)');
insert into categories.cost_type values (-352, 'VA Contract Cost (GM)');
insert into categories.cost_type values (-451, 'Calculated VA Contract Cost (ML)');
insert into categories.cost_type values (-450, 'Calculated VA Contract Cost  (EA)');
insert into categories.cost_type values (-452, 'Calculated VA Contract Cost (GM)');
