-- [mine] select vehicle plate number and its current job progress
select vv.plate_num, oj.progress, vv.branches
from vehicle_vehicle vv
left outer join (
	select vehicle_id, progress
	from order_job
	where progress > 1
) oj on vv.id = oj.vehicle_id;

-- [mine] select vehicle having next job along with order client name
select oj.vehicle_id, au.name
from vehicle_vehicle vv, order_job oj, order_order oo, account_user au
where vv.id = oj.vehicle_id and oj.order_id = oo.id and au.id=oo.customer_id and oj.progress = 1
group by oj.vehicle_id, au.name;

-- [mine] select vehicle status depending on order
select *
from (
	select vv.id, vv.plate_num, vv.branches[1] branch1, vv.branches[2] branch2, vv.branches[3] branch3, oj.progress
	from vehicle_vehicle vv
	left outer join
	(
		select vehicle_id, progress
		from order_job
		where progress > 1
	) oj
	on vv.id = oj.vehicle_id
) tmp1
left outer join 
(
	select oj.vehicle_id, min(oj.start_due_time) due_time, au.name customer
	from vehicle_vehicle vv, order_job oj, order_order oo, account_user au
	where vv.id = oj.vehicle_id and oj.order_id = oo.id and au.id=oo.customer_id and oj.progress = 1
	group by oj.vehicle_id, au.name
) tmp2
on tmp1.id = tmp2.vehicle_id;


-- [reference] select vehicle status depending on order
select  *
from  ( 
	select vv.id, vv.plate_num, oj.progress, vv.branches
	from vehicle_vehicle vv left outer join (select * from order_job where progress > 1) oj on vv.id = oj.vehicle_id) tmp1 
	left outer join
	  (
		select oj.vehicle_id, min(oj.start_due_time), au.name
		from vehicle_vehicle vv, order_order oo, order_job oj, account_user au
		where vv.id = oj.vehicle_id and oj.order_id = oo.id and au.id=oo.customer_id 
		and oj.progress = 1 and oj.start_due_time > now()
		group by oj.vehicle_id, au.name
		) tmp2
	on tmp1.id = tmp2.vehicle_id

