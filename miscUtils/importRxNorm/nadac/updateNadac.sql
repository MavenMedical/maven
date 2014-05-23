\connect maven
CREATE OR REPLACE FUNCTION updatenadacarchive()
  RETURNS void AS
$BODY$

begin
	if not Exists (select * from information_schema.tables where table_name='nadac') then
		create table NADAC
		(
			name varchar(4000) 
			,NDC varchar(20) primary key
			,unitCost numeric(18,9)
			,effectiveDate numeric(18,2) 
			,units varchar(20)
			,pharmacyType varchar(20)
			,isOtc varchar(2)
			,explanationCodes varchar(20)
			,RateSettingClass varchar(20)
			,GenericUnitCost numeric(18,9)
			,GenericEffectiveDate varchar(200) 
		);
		create index IxNadacNDC on NADAC(NDC);

		create table NadacArchive
		(
			name varchar(4000) 
			,NDC varchar(20) 
			,unitCost numeric(18,9)
			,effectiveDate numeric(18,2)
			,units varchar(20)
			,pharmacyType varchar(20)
			,isOtc varchar(2)
			,explanationCodes varchar(20)
			,RateSettingClass varchar(20)
			,GenericUnitCost numeric(18,9)
			,GenericEffectiveDate varchar(200)
			,fromdate date
			,todate date
			,primary key (ndc,fromdate,todate)
		);
		create index ixNadacArcNdcDt on nadacarchive(ndc,fromdate,todate);
                alter table nadac owner to maven;
                alter table nadacarchive owner to maven;
	end if;
        	
	update NadacArchive set todate=current_Date where todate='2100-01-01';
	insert into nadacarchive (select *,current_date,date '2100-01-01' from nadac);
		
end;
$BODY$
  Language plpgsql;

select updatenadacarchive();
truncate table public.nadac;
\copy nadac from 'NADAC.csv' delimiter ',' CSV
