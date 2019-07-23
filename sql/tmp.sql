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

-- [mine] select job station locations if current vehicle is under mission
select oj.progress, oo.is_same_station, vv.plate_num, au.channel_name, tmp.stations
from order_job oj
left join order_order oo on oo.id=oj.order_id
left join vehicle_vehicle vv on vv.id=oj.vehicle_id
left join account_user au on au.id=oj.driver_id
left join (
	select ojs.job_id, array_agg(json_build_object('id', ist.id, 'station_type', ist.station_type, 'longitude', ist.longitude, 'latitude', ist.latitude) order by ojs.step asc) as stations
	from order_jobstation ojs
	left join info_station ist on ojs.station_id=ist.id
	group by ojs.job_id
) as tmp on oj.id=tmp.job_id
order by oj.id;

-- [mine] select next job station location if current vehicle is under mission
select oj.id, oj.progress, oo.is_same_station, vv.plate_num, au.channel_name, tmp.id, tmp.station_type, tmp.longitude, tmp.latitude
from order_job oj
left join order_order oo on oo.id=oj.order_id
left join vehicle_vehicle vv on vv.id=oj.vehicle_id
left join account_user au on au.id=oj.driver_id
left join (
	select distinct on (ojs.job_id) ojs.job_id, ist.id, ist.station_type, ist.longitude, ist.latitude
	from order_jobstation ojs
	left join info_station ist on ist.id=ojs.station_id
) tmp on tmp.job_id=oj.id
where oj.progress > 1;

-- [mine] select next job station
select distinct on (job_id) job_id, station_id
from order_jobstation
order by job_id, is_completed, step;

-- [mine] select all vehicles with its next job station location if current vehicle is under mission
select vv.plate_num, tmp2.is_same_station, tmp2.progress, tmp2.station_id, tmp2.station_type, tmp2.longitude, tmp2.latitude
from vehicle_vehicle vv
left join (
	select oo.is_same_station, oj.progress, oj.vehicle_id, tmp.station_id, tmp.station_type, tmp.longitude, tmp.latitude
	from (
		select id, order_id, vehicle_id, progress
		from order_job
		where progress > 1
	) oj
	left join order_order oo on oj.order_id=oo.id
	left join (
		select ojs.job_id, ojs.station_id, ist.station_type, ist.longitude, ist.latitude
		from (
			select distinct on (job_id) job_id, station_id
			from order_jobstation
			order by job_id, is_completed, step
		) ojs
		left join info_station ist on ojs.station_id=ist.id
	) tmp on oj.id=tmp.job_id
) tmp2 on vv.id=tmp2.vehicle_id;

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
