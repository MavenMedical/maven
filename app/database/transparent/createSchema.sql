\connect maven;

-- Name: rules; Type: SCHEMA; Schema: -; Owner: maven
CREATE SCHEMA transparent;
ALTER SCHEMA transparent OWNER TO maven;

/**
**************
**************
TABLES IN TRANSPARENT SCHEMA
**************
**************
*/
-- Name: transparent.costmap; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE transparent.costmap (
    customer_id integer,
    code character varying(36),
    code_type character varying(36),
    department character varying(255),
    cost_type integer,
    orderable_id character varying(36),
    cost numeric(18,2)
);
ALTER TABLE transparent.costmap OWNER TO maven;

-- Name: costmap_historic; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE transparent.costmap_historic (
    customer_id integer,
    code character varying(36),
    code_type character varying(36),
    department character varying(255),
    cost_type integer,
    orderable_id character varying(36),
    cost numeric(18,2),
    source_info character varying,
    exp_date timestamp without time zone
);
ALTER TABLE transparent.costmap_historic OWNER TO maven;

-- Name: transparent.nadac; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE transparent.nadac (
    name character varying(4000),
    ndc character varying(20) NOT NULL,
    unitcost numeric(18,9),
    effectivedate numeric(18,2),
    units character varying(20),
    pharmacytype character varying(20),
    isotc character varying(2),
    explanationcodes character varying(20),
    ratesettingclass character varying(20),
    genericunitcost numeric(18,9),
    genericeffectivedate character varying(200)
);
ALTER TABLE transparent.nadac OWNER TO maven;

-- Name: transparent.nadacarchive; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE transparent.nadacarchive (
    name character varying(4000),
    ndc character varying(20) NOT NULL,
    unitcost numeric(18,9),
    effectivedate numeric(18,2),
    units character varying(20),
    pharmacytype character varying(20),
    isotc character varying(2),
    explanationcodes character varying(20),
    ratesettingclass character varying(20),
    genericunitcost numeric(18,9),
    genericeffectivedate character varying(200),
    fromdate date NOT NULL,
    todate date NOT NULL
);
ALTER TABLE transparent.nadacarchive OWNER TO maven;

-- Name: transparent.ucl; Type: TABLE; Schema: public; Owner: maven; Tablespace:
CREATE TABLE transparent.ucl (
    ucl_id character varying(100),
    customer_id integer,
    post_date timestamp without time zone,
    svcs_date timestamp without time zone,
    patient_id character varying(100),
    encounter_id character varying(100),
    order_id numeric(18,0),
    proc_id numeric(18,0),
    med_id numeric(18,0),
    bill_prov_id character varying(18),
    svcs_prov_id character varying(18),
    charge_amt numeric(12,2),
    cost_amt numeric(12,2),
    quantity numeric(9,0),
    department_id numeric(18,0),
    billing_code character varying(25),
    code_type character varying(25)
);
ALTER TABLE transparent.ucl OWNER TO maven;

/**
**************
**************
FUNCTIONS IN TRANSPARENT SCHEMA
**************
**************
*/
-- Name: getalternativetable(character varying); Type: FUNCTION; Schema: public; Owner: maven
CREATE FUNCTION transparent.getalternativetable(v_ndc character varying) RETURNS TABLE(brandname character varying, relcost numeric)
    LANGUAGE plpgsql
    AS $$
declare nadacCost numeric(18,2);
begin
      --select getNadacFromNDC(v_ndc) into nadacCost;
      return query select x.brandname,avg(nadac.unitcost)--,avg(nadac.unitcost)*nadacCost
         from terminology.drugclassancestry b
                inner join terminology.drugclassancestry x on x.classaui=b.classaui
                inner join public.nadac nadac on nadac.ndc=x.ndc
                 where b.ndc=v_ndc
                 and x.routename=b.routename
        group by x.brandname;

end;
$$;
ALTER FUNCTION transparent.getalternativetable(v_ndc character varying) OWNER TO maven;

-- Name: getclassnamefromndc(character varying); Type: FUNCTION; Schema: public; Owner: maven
CREATE FUNCTION transparent.getclassnamefromndc(v_ndc character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $$
Declare rtn varchar(200);
begin
        select classname into rtn from terminology.drugclassancestry a
	inner join terminology.drugclass b on a.classaui=b.rxaui
        where ndc=v_ndc
        order by snomedid limit 1;
        return rtn;
end;
$$;
ALTER FUNCTION transparent.getclassnamefromndc(v_ndc character varying) OWNER TO maven;

-- Name: transparent.getclasssnomedfromndc(character varying); Type: FUNCTION; Schema: public; Owner: maven
CREATE FUNCTION transparent.getclasssnomedfromndc(v_ndc character varying) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
Declare rtn numeric;
begin
        select max(c.SnomedId) into rtn
        from terminology.drugclassancestry b
        inner join terminology.drugclass c on b.classaui=c.rxaui
         where b.ndc=v_ndc ;

        return rtn;
end;
$$;
ALTER FUNCTION transparent.getclasssnomedfromndc(v_ndc character varying) OWNER TO maven;

-- Name: transparent.getnadacfromndc(character varying); Type: FUNCTION; Schema: public; Owner: maven
CREATE FUNCTION transparent.getnadacfromndc(v_ndc character varying) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
declare nadacCost numeric(18,2);
begin
 select unitcost into nadacCost from public.nadac where ndc=v_ndc limit 1;
 return nadaccost;
end;
$$;
ALTER FUNCTION transparent.getnadacfromndc(v_ndc character varying) OWNER TO maven;

-- Name: transparent.isndcchild(numeric, character varying); Type: FUNCTION; Schema: public; Owner: maven
CREATE FUNCTION transparent.isndcchild(vparentconcept numeric, ndc character varying) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
Declare rtn Boolean;
Declare Sno numeric;
begin
        select getClassSnomedFromNDC(ndc) into sno;
        return isSnomedChild(vparentconcept,sno);
end;
$$;
ALTER FUNCTION transparent.isndcchild(vparentconcept numeric, ndc character varying) OWNER TO maven;

--
-- Name: transparent.translatenadacunitstonumeric(); Type: FUNCTION; Schema: public; Owner: maven
CREATE FUNCTION transparent.translatenadacunitstonumeric() RETURNS TABLE(units character varying, ndc character varying, unitcost numeric)
    LANGUAGE plpgsql
    AS $$
begin
  FOR units, ndc, unitCost IN
    SELECT nadac.units, nadac.ndc, nadac.unitcost FROM nadac
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
$$;
ALTER FUNCTION transparent.translatenadacunitstonumeric() OWNER TO maven;

-- Name: transparent.updatenadacarchive(); Type: FUNCTION; Schema: public; Owner: maven
CREATE FUNCTION transparent.updatenadacarchive() RETURNS void
    LANGUAGE plpgsql
    AS $$

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
$$;
ALTER FUNCTION transparent.updatenadacarchive() OWNER TO maven;