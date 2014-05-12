\connect maven

DROP  TABLE IF EXISTS source_organization;
CREATE TABLE source_organization (
  copyright_id varchar(255) not null,
  name varchar(255) default null,
  copyright text,
  terms_of_use text,
  url varchar(255) default null,
  primary key (copyright_id)
) ;

DROP  TABLE IF EXISTS loinc;
CREATE TABLE loinc (
  loinc_num varchar(10) not null,
  component varchar(255) default null,
  property varchar(30) default null,
  time_aspct varchar(15) default null,
  system varchar(100) default null,
  scale_typ varchar(30) default null,
  method_typ varchar(50) default null,
  class varchar(20) default null,
  source varchar(8) default null,
  date_last_changed varchar(30) default null,
  chng_type varchar(3) default null,
  comments text,
  status varchar(11) default null,
  consumer_name varchar(255) default null,
  molar_mass varchar(13) default null,
  classtype numeric(11,0) default null,
  formula varchar(255) default null,
  species varchar(20) default null,
  exmpl_answers text,
  acssym text,
  base_name varchar(50) default null,
  naaccr_id varchar(20) default null,
  code_table varchar(10) default null,
  survey_quest_text text,
  survey_quest_src varchar(50) default null,
  unitsrequired varchar(1) default null,
  submitted_units varchar(30) default null,
  relatednames2 text,
  shortname varchar(40) default null,
  order_obs varchar(15) default null,
  cdisc_common_tests varchar(1) default null,
  hl7_field_subfield_id varchar(50) default null,
  external_copyright_notice text,
  example_units varchar(255) default null,
  long_common_name varchar(255) default null,
  hl7_v2_datatype varchar(255) default null,
  hl7_v3_datatype varchar(255) default null,
  curated_range_and_units text,
  document_section varchar(255) default null,
  example_ucum_units varchar(255) default null,
  example_si_ucum_units varchar(255) default null,
  status_reason varchar(9) default null,
  status_text text,
  change_reason_public text,
  common_test_rank integer default null,
  common_order_rank integer default null,
  common_si_test_rank integer default null,
  hl7_attachment_structure varchar(15) default null,
  primary key (loinc_num)

);

DROP TABLE IF EXISTS map_to;
CREATE TABLE map_to (
  loinc varchar(10) DEFAULT NULL,
  map_to varchar(10) DEFAULT NULL,
  comment text,
  primary key (loinc, map_to)

);

\copy map_to from 'map_to2.csv' csv
\copy loinc from 'loinc2.csv' csv
\copy source_organization from 'source_organization2.csv' csv
