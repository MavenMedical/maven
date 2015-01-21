
/*
This function is used to push child protocols out to other organizations for the very first time. 
After the first time they are created (they will live under the /community/parentOrg folder) they will
then be maintained by the "publish" button which will send emails to the orgs notifying them of changes. 
*/
create or replace function trees.community_publish(v_canonical_id int) returns int
as $$
begin
	--insert canonicals for every organization that doesnt currently have a pointer to this canonical
	insert into trees.canonical_protocol (name,customer_id,enabled,current_id,deleted,parent_id,folder)
	(
		select max(parent.name) "name",c.customer_id,false enabled,-1 current_id,false deleted, max(parent.canonical_id) parent_id,'community/'||max(d.name) folder
		from trees.canonical_protocol parent
		inner join customer c on 1=1
		inner join customer d on parent.customer_id=d.customer_id
		left outer join trees.canonical_protocol child on child.parent_id=parent.canonical_id  and child.customer_id=c.customer_id
		where parent.canonical_id=v_canonical_id and c.customer_id>0 and c.customer_id<>parent.customer_id
		group by c.customer_id having max(child.canonical_id) is null
	);

	--insert protocols for the newly created canonical
	insert into trees.protocol (customer_id,description,minage,maxage,sex,full_spec,canonical_id,deleted,creator,parent_id,tags,creation_time)
	(
		select child.customer_id,pro.description,pro.minage,pro.maxage,pro.sex,pro.full_spec,child.canonical_id,false,null,null,null,current_timestamp
		from trees.canonical_protocol child
		inner join trees.canonical_protocol parent on parent.canonical_id=child.parent_id
		inner join trees.protocol pro on pro.protocol_id=parent.current_id
		where child.current_id=-1
	);

	--update canonicals to point to protocols (maintain references)
	update trees.canonical_protocol a
	set current_id=(select protocol_id from trees.protocol x where x.canonical_id=a.canonical_id)
	where current_id=-1;

	return 1; --i worked
end;
$$
language plpgsql;

