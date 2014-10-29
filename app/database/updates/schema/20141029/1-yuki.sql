DROP FUNCTION IF EXISTS trees.comparisonintarray(character varying, bigint[], bigint[], character varying, integer, integer, integer);

-- Function: trees.comparisonintarray(character varying, bigint[], bigint[], character varying, integer, integer, integer)
-- DROP FUNCTION trees.comparisonintarray(character varying, bigint[], bigint[], character varying, integer, integer, integer);
CREATE OR REPLACE FUNCTION trees.comparisonintarray(listtype character varying, encsnomeds bigint[], probsnomeds bigint[], patid character varying, framemin integer, framemax integer, customer integer)
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
                rtn:=(SELECT array_agg(DISTINCT(snomed_id))
                      FROM public.condition a
                      WHERE a.patient_id=patid and a.customer_id=customer and current_date+mn<=date_asserted and current_date+mx>=date_asserted
                      GROUP BY a.patient_id);
                return encsnomeds||probsnomeds||rtn;
        else
                return null;
        end if;
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION trees.comparisonintarray(character varying, bigint[], bigint[], character varying, integer, integer, integer)
  OWNER TO maven;