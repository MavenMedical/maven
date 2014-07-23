--creating a test to simply re-compile the current comparisonintarray function

CREATE OR REPLACE FUNCTION rules.comparisonintarray(listtype character varying, encsnomeds bigint[], probsnomeds bigint[], patid character varying, framemin integer, framemax integer, customer integer)
  RETURNS bigint[] AS
$BODY$
declare rtn bigint[];
        mn int;
        mx int;
begin
        mn:=coalesce(framemin,-99999);
        mx:=coalesce(framemin,1);
        if listType='pl_dx' then
                return probsnomeds;
        elsif listtype='enc_dx' then
                return encSnomeds;
        elsif listtype='enc_pl_dx' then
                return encSnomeds||probsnomeds;
        elsif listtype='hist_dx' then
                select encsnomeds||probsnomeds||array_agg(snomed_id) into rtn
                        from public.condition a
                        where a.pat_id=patid and a.customer_id=customer and  current_date+mn<=date_asserted and current_date+mx>=date_asserted
                        group by a.pat_id ;
                return rtn;
        else
                return null;
        end if;
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION rules.comparisonintarray(character varying, bigint[], bigint[], character varying, integer, integer, integer)
  OWNER TO postgres;

