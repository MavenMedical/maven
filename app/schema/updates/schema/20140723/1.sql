--recompile something for testing purposes
CREATE OR REPLACE FUNCTION rules.comparisonstrarray(listtype character varying, patid character varying, framemin integer, framemax integer, customer integer, druglist character varying[])
  RETURNS character varying[] AS
$BODY$
declare rtn varchar[];
	mn int;
	mx int;
begin
	mn:=coalesce(framemin,-99999);
	mx:=coalesce(framemin,1);
	if listType='hist_proc' then
		select array_agg(code_id) into rtn
			from public.order_ord a
			where a.pat_id=patid and a.customer_id=customer and code_system='HCPCS' and current_date+mn<=order_datetime and current_date+mx>=order_datetime
			group by a.pat_id ;
		return rtn;
	elsif listType='drug_list' then 
		return druglist;
	else
		return null;
	end if;
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION rules.comparisonstrarray(character varying, character varying, integer, integer, integer, character varying[])
  OWNER TO postgres;
