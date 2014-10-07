/*********************************
Function: Trees.InsertProtocol
Description: Used to insert new protocols and maintain the protocol id's 
Created: MAV-480 Oct2014 Dave
Call Like: select trees.insertProtocol('{}' ,0,'test')
Returns: True on success, False on failure
********************************/
create or replace function trees.insertProtocol(fullspec json,custid_in numeric(18,0),name_in varchar(100),desc_in varchar(1000) default ''
    ,minage_in numeric(18,2) default 0,maxage_in numeric(18,2) default 200, sex_in varchar(1) default '%')
returns boolean 
as 
$$
declare
	v_pathid int;
begin
	select coalesce(max(protocol_id)+1,1) into v_pathid from trees.protocol;
	insert into trees.protocol (protocol_id,customer_id,name,description,minage,maxage,sex,full_spec)
		values(v_pathid,custid_in,name_in,desc_in,minage_in,maxage_in,sex_in,fullspec);
	return true;
exception when others then 
	return false;
end;
$$ language plpgsql;


/****************************************
Remove the sequence dependency of trees.protocol.protocol_id and make it the primary key
******************************************/
drop sequence trees.protocol_protocol_id_seq cascade;
alter table trees.protocol add constraint PK_Protocol primary key (protocol_id);

/*********************************************
index the PK
**********************************************/
create index ixPkTreesProtocol on trees.protocol(protocol_id);
