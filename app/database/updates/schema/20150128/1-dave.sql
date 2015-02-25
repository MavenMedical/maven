-- Function: encounterreport(character varying, integer)

-- DROP FUNCTION encounterreport(character varying, integer);

CREATE OR REPLACE FUNCTION encounterreport(v_encid character varying, v_custid integer)
  RETURNS text AS
$BODY$
declare 
    v_template text;
    v_listtemplate text;
    v_listitem text;
    v_name varchar(200);
    v_sex varchar(10);
    v_dob varchar(100);
    v_mrn varchar(100);
    v_pcp varchar(100);
    v_enctype varchar(100);
    v_encdate varchar(100);
    v_prov varchar(200);
    v_problist text;
    v_enclist text;
    v_ordlist text;
begin
	select 
		b.patname --into v_name, 
		,cast(b.birthdate as varchar) --into v_dob ,
		,b.sex --into v_sex;
		,b.mrn --into v_mrn,
		,coalesce(pcp.prov_name,'None') --into v_pcp ,
		,a.enc_type --into v_enctype,
		,cast(a.contact_date as varchar) --into v_encdate,
		,coalesce(encprov.prov_name,'None') --into v_prov,
		into v_name,v_dob,v_sex,v_mrn,v_pcp,v_enctype,v_encdate,v_prov
	from encounter a inner join patient b on a.patient_id=b.patient_id
		left outer join provider pcp on b.cur_pcp_prov_id=pcp.prov_id
		left outer join provider encprov on a.visit_prov_id=encprov.prov_id
	where a.csn=v_encid and a.customer_id=v_custid;
	v_template='
	<style>
	<!--
	 /* Font Definitions */
	 @font-face
		{font-family:Wingdings;
		panose-1:5 0 0 0 0 0 0 0 0 0;}
	@font-face
		{font-family:"Cambria Math";
		panose-1:2 4 5 3 5 4 6 3 2 4;}
	@font-face
		{font-family:"Calibri Light";
		panose-1:2 15 3 2 2 2 4 3 2 4;}
	@font-face
		{font-family:Calibri;
		panose-1:2 15 5 2 2 2 4 3 2 4;}
	 /* Style Definitions */
	 p.MsoNormal, li.MsoNormal, div.MsoNormal
		{margin-top:0in;
		margin-right:0in;
		margin-bottom:8.0pt;
		margin-left:0in;
		line-height:107%;
		font-size:11.0pt;
		font-family:"Calibri","sans-serif";}
	h1
		{mso-style-link:"Heading 1 Char";
		margin-top:12.0pt;
		margin-right:0in;
		margin-bottom:0in;
		margin-left:0in;
		margin-bottom:.0001pt;
		line-height:107%;
		page-break-after:avoid;
		font-size:16.0pt;
		font-family:"Calibri Light","sans-serif";
		color:#2E74B5;
		font-weight:normal;}
	h2
		{mso-style-link:"Heading 2 Char";
		margin-top:2.0pt;
		margin-right:0in;
		margin-bottom:0in;
		margin-left:0in;
		margin-bottom:.0001pt;
		line-height:107%;
		page-break-after:avoid;
		font-size:13.0pt;
		font-family:"Calibri Light","sans-serif";
		color:#2E74B5;
		font-weight:normal;}
	p.MsoListParagraph, li.MsoListParagraph, div.MsoListParagraph
		{margin-top:0in;
		margin-right:0in;
		margin-bottom:8.0pt;
		margin-left:.5in;
		line-height:107%;
		font-size:11.0pt;
		font-family:"Calibri","sans-serif";}
	p.MsoListParagraphCxSpFirst, li.MsoListParagraphCxSpFirst, 

	div.MsoListParagraphCxSpFirst
		{margin-top:0in;
		margin-right:0in;
		margin-bottom:0in;
		margin-left:.5in;
		margin-bottom:.0001pt;
		line-height:107%;
		font-size:11.0pt;
		font-family:"Calibri","sans-serif";}
	p.MsoListParagraphCxSpMiddle, li.MsoListParagraphCxSpMiddle, 

	div.MsoListParagraphCxSpMiddle
		{margin-top:0in;
		margin-right:0in;
		margin-bottom:0in;
		margin-left:.5in;
		margin-bottom:.0001pt;
		line-height:107%;
		font-size:11.0pt;
		font-family:"Calibri","sans-serif";}
	p.MsoListParagraphCxSpLast, li.MsoListParagraphCxSpLast, 

	div.MsoListParagraphCxSpLast
		{margin-top:0in;
		margin-right:0in;
		margin-bottom:8.0pt;
		margin-left:.5in;
		line-height:107%;
		font-size:11.0pt;
		font-family:"Calibri","sans-serif";}
	span.Heading1Char
		{mso-style-name:"Heading 1 Char";
		mso-style-link:"Heading 1";
		font-family:"Calibri Light","sans-serif";
		color:#2E74B5;}
	span.Heading2Char
		{mso-style-name:"Heading 2 Char";
		mso-style-link:"Heading 2";
		font-family:"Calibri Light","sans-serif";
		color:#2E74B5;}
	.MsoChpDefault
		{font-family:"Calibri","sans-serif";}
	.MsoPapDefault
		{margin-bottom:8.0pt;
		line-height:107%;}
	@page WordSection1
		{size:8.5in 11.0in;
		margin:1.0in 1.0in 1.0in 1.0in;}
	div.WordSection1
		{page:WordSection1;}
	 /* List Definitions */
	 ol
		{margin-bottom:0in;}
	ul
		{margin-bottom:0in;}
	-->
	</style>


	<div class=WordSection1>

	<h1><strong><span style=''font-family:"Calibri Light","sans-

	serif"''>[[Patient Name]]</span></strong></h1>

	<table class=MsoTableGrid border=0 cellspacing=0 cellpadding=0
	 style=''border-collapse:collapse;border:none''>
	 <tr>
	  <td width=128 valign=top style=''width:95.75pt;padding:0in 5.4pt 0in 

	5.4pt''>
	  <p class=MsoNormal style=''margin-bottom:0in;margin-

	bottom:.0001pt;line-height:
	  normal''><strong><span style=''font-family:"Calibri","sans-

	serif";font-weight:
	  normal''>&nbsp;</span></strong></p>
	  </td>
	  <td width=128 valign=top style=''width:95.75pt;padding:0in 5.4pt 0in 

	5.4pt''>
	  <p class=MsoNormal style=''margin-bottom:0in;margin-

	bottom:.0001pt;line-height:
	  normal''><strong><span style=''font-family:"Calibri","sans-

	serif";font-weight:
	  normal''>[[Sex]]</span></strong></p>
	  </td>
	  <td width=128 valign=top style=''width:95.75pt;padding:0in 5.4pt 0in 

	5.4pt''>
	  <p class=MsoNormal style=''margin-bottom:0in;margin-

	bottom:.0001pt;line-height:
	  normal''><strong><span style=''font-family:"Calibri","sans-

	serif";font-weight:
	  normal''>[[DOB]]</span></strong></p>
	  </td>
	  <td width=128 valign=top style=''width:95.75pt;padding:0in 5.4pt 0in 

	5.4pt''>
	  <p class=MsoNormal style=''margin-bottom:0in;margin-

	bottom:.0001pt;line-height:
	  normal''><strong><span style=''font-family:"Calibri","sans-

	serif";font-weight:
	  normal''>[[MRN]]</span></strong></p>
	  </td>
	  <td width=128 valign=top style=''width:95.8pt;padding:0in 5.4pt 0in 

	5.4pt''>
	  <p class=MsoNormal style=''margin-bottom:0in;margin-

	bottom:.0001pt;line-height:
	  normal''><strong><span style=''font-family:"Calibri","sans-

	serif";font-weight:
	  normal''>[[PCP]]</span></strong></p>
	  </td>
	 </tr>
	</table>

	<h2><strong><span style=''font-family:"Calibri Light","sans-

	serif";font-weight:
	normal''>Problem List</span></strong></h2>
	[[Problem List]]



	<h1><strong><span style=''font-family:"Calibri Light","sans-

	serif"''>[[Type]] Encounter
	on [[ENCDATE]] with [[Provider]]</span></strong></h1>

	<h2><strong><span style=''font-family:"Calibri Light","sans-

	serif";font-weight:
	normal''>Encounter Problems</span></strong></h2>
	[[EncList]]

	<p class=MsoNormal><strong><span style=''font-family:"Calibri","sans-

	serif";
	font-weight:normal''>&nbsp;</span></strong></p>

	<p class=MsoNormal style=''margin-left:.5in''><strong><span 

	style=''font-family:
	"Calibri","sans-serif";font-weight:normal''>&nbsp;</span></strong></p>
	
<h2><strong><span style=''font-family:"Calibri Light","sans-

	serif";font-weight:
	normal''>Orders</span></strong></h2>
	[[Order List]]


	</div>';

	v_listtemplate='<p class=MsoListParagraphCxSpFirst style=''text-
	indent:-.25in''><strong><span
	style=''font-family:Symbol;font-weight:normal''>·<span 
	style=''font:7.0pt "Times New 
	Roman"''>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
	</span></span></strong><strong><span style=''font-
	family:"Calibri","sans-serif";
	font-weight:normal''>[[ListItem]]</span></strong></p>';


	v_template=replace(v_template,'[[Patient Name]]',v_name);
	v_template=replace(v_template,'[[Sex]]','Sex: '||v_sex);
	v_template=replace(v_template,'[[DOB]]','DOB: '||v_dob);
	v_template=replace(v_template,'[[MRN]]','MRN: '||v_mrn);
	v_template=replace(v_template,'[[PCP]]','PCP: '||v_pcp);
	v_template=replace(v_template,'[[Type]]',v_enctype);
	v_template=replace(v_template,'[[ENCDATE]]',v_encdate);
	v_template=replace(v_template,'[[Provider]]',v_prov);
	
	v_problist='';
	v_enclist='';
	v_ordlist='';
	
	for v_listitem in select  term||'( '||dx_code_id||')'  from condition a
		inner join terminology.descriptions b on a.snomed_id=b.conceptid
		where a.encounter_id=v_encid and dx_category='Problem List' and active=1 and typeid=900000000000003001
		and customer_id=v_custid 
	loop
		v_problist=v_problist||replace(v_listtemplate,'[[ListItem]]',v_listitem);
	end loop;
	if v_problist='' then	
		v_problist=replace(v_listtemplate,'[[ListItem]]','None on file');
	end if;
	
	v_enclist='';

	for v_listitem in select  term||'( '||dx_code_id||')'  from condition a
		inner join terminology.descriptions b on a.snomed_id=b.conceptid
		where a.encounter_id=v_encid and dx_category='Encounter' and active=1 and typeid=900000000000003001
		and customer_id=v_custid 
	loop
		v_enclist=v_enclist||replace(v_listtemplate,'[[ListItem]]',v_listitem);
	end loop;
	if v_enclist='' then	
		v_enclist=replace(v_listtemplate,'[[ListItem]]','None on file');
	end if;

       for v_listitem in select  order_name from order_ord a
		where a.encounter_id=v_encid
		and customer_id=v_custid 
	loop
		v_ordlist=v_ordlist||replace(v_listtemplate,'[[ListItem]]',v_listitem);
	end loop;
	if v_ordlist='' then	
		v_ordlist=replace(v_listtemplate,'[[ListItem]]','None on file');
	end if;

	v_template=replace(v_template,'[[Problem List]]',v_problist);
	v_template=replace(v_template,'[[EncList]]',v_enclist);
	v_template=replace(v_template,'[[Order List]]',v_ordlist);
	return v_template;
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION encounterreport(character varying, integer)
  OWNER TO maven;


-- Function: encounterreport(character varying, character varying, date, integer)

-- DROP FUNCTION encounterreport(character varying, character varying, date, integer);

CREATE OR REPLACE FUNCTION encounterreport(v_prov_id character varying, v_patientid character varying, v_date date, v_custid integer)
  RETURNS text AS
$BODY$
declare 
    v_encid varchar(20);
begin
	select csn into v_encid from encounter where customer_id=v_custid and patient_id=v_patientId and visit_prov_id=v_prov_id and contact_date=v_date order by csn desc limit 1;
	return encounterreport(v_encid,v_custid);
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION encounterreport(character varying, character varying, date, integer)
  OWNER TO maven;

