select *, 'df'
from 
(select plate_num, id as vehicle_id, 
	(select oj.order_id
	from order_job as oj
	where oj.vehicle_id = vv.id and oj.progress = 1 and oj.start_due_time >now()
	order by oj.start_due_time
	limit 1) as order_id
from vehicle_vehicle as vv ) tmp1
left outer join (select oo.id, oo.customer_id, ac."name" as customer_name from order_order oo, account_user ac where oo.customer_id = ac.id ) tmp on tmp.id = tmp1.order_id 
left outer join order_job oj on tmp1.vehicle_id = oj.vehicle_id
 


select *
from order_order oo
where oo.id = (select oj.order_id
				from order_job as oj 
				where oj.progress = 1 and oj.start_due_time >now()
				order by oj.start_due_time
				limit 1)


select oo.id, oo.customer_id, ac."name" as customer_name from order_order oo, account_user ac where oo.customer_id = ac.id 
