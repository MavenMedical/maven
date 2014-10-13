\connect maven
CREATE OR REPLACE FUNCTION transparent.updatenadacarchive()
  RETURNS void AS
$BODY$

begin
	if not Exists (select * from information_schema.tables where table_name='nadac') then
		create table transparent.NADAC
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
		create index IxNadacNDC on transparent.NADAC(NDC);

		create table transparent.NadacArchive
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
		create index ixNadacArcNdcDt on transparent.nadacarchive(ndc,fromdate,todate);
                alter table transparent.nadac owner to maven;
                alter table transparent.nadacarchive owner to maven;
	end if;
        	
	update transparent.NadacArchive set todate=current_Date where todate='2100-01-01';
	insert into transparent.nadacarchive (select *,current_date,date '2100-01-01' from transparent.nadac);
		
end;
$BODY$
  Language plpgsql;

select updatenadacarchive();
truncate table public.nadac;
\copy transparent.nadac from 'NADAC.csv' delimiter ',' CSV
delete from public.costmap where customer_id=-1 and code_type='NDC';

CREATE OR REPLACE FUNCTION translatenadacunitstonumeric()
  RETURNS TABLE(units character varying, ndc character varying, unitCost numeric) AS
$BODY$
begin
  FOR units, ndc, unitCost IN
    SELECT nadac.units, nadac.ndc, nadac.unitcost FROM transparent.nadac
      LOOP
        IF units = 'EA' THEN
          INSERT INTO costmap(
            customer_id, code, code_type, department, cost_type, orderable_id,
            cost)
          VALUES (-1, ndc, 'NDC', -1, -150, ndc,
                  unitCost);
        ELSEIF units = 'GM' THEN
          INSERT INTO costmap(
            customer_id, code, code_type, department, cost_type, orderable_id,
            cost)
          VALUES (-1, ndc, 'NDC', -1, -152, ndc,
                  unitCost);
        ELSEIF units = 'ML' THEN
          INSERT INTO costmap(
            customer_id, code, code_type, department, cost_type, orderable_id,
            cost)
          VALUES (-1, ndc, 'NDC', -1, -151, ndc,
                  unitCost);
        END IF;
        RETURN NEXT;
      END LOOP;
      RETURN;
end
$BODY$
  Language plpgsql;
select translatenadacunitstonumeric();
insert into public.orderable (customer_id,orderable_id,ord_type,name,description) (Select -1,NDC,'Med',name,name from transparent.NADAC);