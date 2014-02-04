create user maven password 'temporary' SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN;

CREATE DATABASE testData
  WITH OWNER = maven
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'en_US.UTF-8'
       LC_CTYPE = 'en_US.UTF-8'
       CONNECTION LIMIT = -1;

\c testdata

create language plpgsql;


CREATE TABLE department(
	department_id numeric(18, 0) primary key,
	dep_name varchar(100),
	specialty varchar(50),
	location varchar(100)
) ;
create index ixdeppk on department(department_id);

CREATE TABLE diagnosis(
	dx_id numeric(18, 0) ,
	current_icd9_list varchar(254),
	current_icd10_list varchar(254),
	dx_name varchar(200),
	DX_IMO_ID varchar(254),
	IMO_TERM_ID varchar(30),
	concept_id varchar(254)
) ;
create index ixdiagnosispk on diagnosis(dx_id);

CREATE TABLE encounter(
	pat_id varchar(100),
	CSN varchar(100) primary key,
	enc_type varchar(254),
	contact_date date,
	visit_prov_id varchar(18),
	department_id numeric(18, 0),
	hosp_admsn_time date,
	hosp_disch_time date
) ;
create index ixEncounterPatId on encounter(pat_id);

CREATE TABLE encounterDx(
	pat_id varchar(100),
	CSN varchar(100),
	dx_id numeric(18, 0),
	annotation varchar(200),
	primary_dx_yn varchar(1),
	dx_chronic_yn varchar(1)
) ;
create index ixEncounterDxCsnDx on encounterDx(csn,dx_id);
create index ixEncounterPatId on encounterDx(pat_id);

CREATE TABLE labResult(
	OrderId numeric(18, 0),
	pat_id varchar(100),
	CSN varchar(100),
	result_time date,
	component_id numeric(18, 0),
	result varchar(254),
	numeric_result float,
	reference_low varchar(50),
	reference_high varchar(50),
	reference_unit varchar(100),
	name varchar(75),
	external_name varchar(75),
	base_name varchar(75),
	common_name varchar(254),
	loinc_code varchar(254)
) ;
create index ixLabOrdId on labResult(order_id);
create index ixLabPatId on labResult(pat_id);
create index ixLabCsn on labResult(csn);
create index ixLabComponentId on labResult(component_id);


CREATE TABLE medication(
	medication_id numeric(18, 0) primary key,
	name varchar(255),
	generic_name varchar(200),
	cost varchar(254),
	GPI varchar(192),
	strength varchar(254),
	form varchar(50),
	route varchar(50),
	thera_class varchar(254),
	pharm_class varchar(254),
	pharm_subclass varchar(254),
	simple_generic varchar(254)
) ;
create index ixmedpk on medication(medication_id);

CREATE TABLE medOrder(
	OrderId numeric(18, 0),
	pat_id varchar(100),
	CSN varchar(100),
	ordering_date date,
	ordering_time date,
	order_type varchar(10),
	medication_id numeric(18, 0),
	description varchar(255),
	order_class varchar(254),
	authrzing_prov_id varchar(18)
) ;
create index ixMedOrderOrdId on medorder(orderid);
create index ixMedOrderPatId on medorder(pat_id);
create index ixMedOrderCSN on medorder(csn);

CREATE TABLE medicalProcedure(
	proc_id numeric(18, 0) primary key,
	proc_name varchar(100),
	cpt_code varchar(20),
	base_charge varchar(254),
	rvu_work_compon numeric(12, 2),
	rvu_overhd_compon numeric(12, 2),
	RVu_malprac_compon numeric(12, 2),
	rvu_total_no_mod numeric(12, 2)
) ;
create index ixprocpk on medicalprocedure(proc_id);

CREATE TABLE patient(
	pat_id varchar(100) primary key,
	birth_month varchar(6),
	sex varchar(254),
	mrn varchar(100),
	patName varchar(100),
	cur_pcp_prov_id varchar(18)
) ;
create index ixpatpk on patient(pat_id);

CREATE TABLE problemList(
	pat_id varchar(100),
	dx_id numeric(18, 0),
	noted_date date,
	resolved_date date,
	date_of_entry date,
	chronic_yn varchar(1),
	status varchar(254)
) ;
create index isProbLostPatDx  on problemlist (pat_id,dx_id);

CREATE TABLE procedureOrder(
	OrderId numeric(18, 0),
	pat_id varchar(100),
	CSN varchar(100),
	ordering_date date,
	ordering_time date,
	order_type varchar(254),
	CPT_CODE varchar(20),
	description varchar(254),
	order_class varchar(254),
	authrzing_prov_id varchar(18)
) ;
create index ixProcOrderOrdId on procedureorder(orderid);
create index ixProcOrderPatId on procedureorder(pat_id);
create index ixProcOrderCSN on procedureorder(csn);


CREATE TABLE provider(
	prov_id varchar(18) primary key,
	prov_name varchar(100),
	specialty varchar(254),
	specialty2 varchar(254)
) ;
create index ixprovpk on provider(prov_id);


\copy department from 'department' DELIMITER '|'  null as ''
\copy diagnosis from 'diagnosis' DELIMITER '|'   null as ''
\copy encounter from 'encounter' DELIMITER '|'   null as ''
\copy encounterDx from 'encounterdx' DELIMITER '|'   null as ''
\copy labResult from 'labResult' DELIMITER '|'   null as ''
\copy medicalProcedure from 'medicalprocedure' DELIMITER '|'   null as ''
\copy medication from 'medication' DELIMITER '|'   null as ''
\copy medOrder from 'medorder' DELIMITER '|'  null as ''
\copy patient from 'patient' DELIMITER '|'   null as ''
\copy problemList from 'problemlist' DELIMITER '|'   null as ''
\copy procedureOrder from 'procedureorder' DELIMITER '|'   null as ''
\copy provider from 'provider' DELIMITER '|'   null as ''

