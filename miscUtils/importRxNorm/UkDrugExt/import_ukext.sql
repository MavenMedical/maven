\connect maven;

drop table terminology.DrugConcept;
drop table terminology.DrugDesc;
drop table terminology.DrugRel;

create table terminology.DrugConcept
(
   id numeric(18,0) primary key
   ,status int
   ,name varchar(4000)
   ,ctv3id varchar(200)
   ,snomedid varchar(200)
   ,isprimitive int
);
create index ixDrugConceptId on terminology.drugconcept(id);

create table terminology.DrugDesc
(
   Id numeric(18,0) primary  key
   ,Status int
   ,ConceptId numeric(18,0)
   ,Term varchar(4000)
   ,initialCapitalStatus int
   ,descriptionType varchar(200)
   ,languageCode varchar(200)
);
create index ixDrugDescConceptId  on terminology.DrugDesc(ConceptId);

create table terminology.DrugRel 
(
   id numeric(18,0) primary key
   ,sourceid numeric(18,0)
   ,typeid numeric(18,0)
   ,destinationid numeric(18,0)
   ,CharacteristicType int
   ,Refinability int
   ,relationshipgroup int
);
create index ixDrugRelSDT on terminology.DrugRel (sourceid,destinationid,typeid);
create index ixDrugRelDST on terminology.drugrel (destinationid,sourceid,typeid);

\copy terminology.Drugconcept from 'Concept.tmp' delimiter E'\t' null as ''
\copy terminology.DrugDesc from 'Desc.tmp' delimiter E'\t' null as ''
\copy terminology.DrugRel from 'Rel.tmp' delimiter E'\t' null as ''

