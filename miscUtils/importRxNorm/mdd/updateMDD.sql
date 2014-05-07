\connect maven
drop table if exists  terminology.drugMaxDailyDose;
create table terminology.drugMaxDailyDose(
DSSTox_RID	varchar(200) primary key
,DSSTox_CID	varchar(200)
,DSSTox_Generic_SID	varchar(200)
,DSSTox_FileID	varchar(200)
,STRUCTURE_Formula	varchar(2000)
,STRUCTURE_MolecularWeight	varchar(2000)
,STRUCTURE_ChemicalType	varchar(2000)
,STRUCTURE_TestedForm_DefinedOrganic varchar(2000)	
,STRUCTURE_Shown	varchar(2000)
,TestSubstance_ChemicalName	varchar(2000)
,TestSubstance_CASRN	varchar(2000)
,TestSubstance_Description	varchar(2000)
,ChemicalNote	varchar(2000)
,STRUCTURE_ChemicalName_IUPAC	varchar(2000)
,STRUCTURE_SMILES	varchar(2000)
,STRUCTURE_Parent_SMILES	varchar(2000)
,STRUCTURE_InChI	varchar(2000)
,STRUCTURE_InChIKey	varchar(2000)
,StudyType	varchar(200)
,Endpoint	varchar(200)
,Species	varchar(200)
,ChemicalReplicateCount	varchar(200)
,ChemClass_MRDD_grouping	varchar(200)
,TherapeuticCategory	varchar(200)
,Dose_MRDD_mg	float
,Dose_MRDD_mmol	float
,LOGINV_MRDD_mmol	float
,ActivityScore_FDAMDD	varchar(200)
,ActivityCategory_MRDD_mmol	varchar(200)
,ActivityCategory_MCASE_mg	varchar(200)
,Note_FDAMDD			varchar(2000)
);
\copy terminology.drugMaxDailydose from 'MDD.csv' delimiter ',' CSV
