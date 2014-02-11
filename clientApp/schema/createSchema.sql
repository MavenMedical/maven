create user maven password 'temporary' SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN;

CREATE DATABASE maven
  WITH OWNER = maven
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'en_US.UTF-8'
       LC_CTYPE = 'en_US.UTF-8'
       CONNECTION LIMIT = -1;

\c maven

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
	concept_id varchar(2000)
) ;
create index ixdiagnosispk on diagnosis(dx_id);


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

CREATE TABLE provider(
	prov_id varchar(18) primary key,
	prov_name varchar(100),
	specialty varchar(254),
	specialty2 varchar(254)
) ;
create index ixprovpk on provider(prov_id);



