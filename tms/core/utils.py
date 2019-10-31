from datetime import timedelta
from ..g7.interfaces import G7Interface


def format_datetime(dt):
    return dt.strftime("%Y年%m月%d日 %H:%M:%S") if dt else ''


def get_branches(job):
    branches = []
    for job_station in job.jobstation_set.all()[2:]:
        for job_station_product in job_station.jobstationproduct_set.all():
            order_product = job.order.orderproduct_set.filter(product=job_station_product.product).first()
            for branch in branches:
                if branch['branch'] == job_station_product.branch:
                    branch['unloading_stations'].append({
                        'unloading_station': {
                            'address': job_station.station.address,
                            'time': job_station_product.due_time.strftime("%Y-%m-%d %H:%M")
                        },
                        'weight': str(job_station_product.mission_weight)
                        + order_product.get_weight_measure_unit_display()
                    })
                    break
            else:
                branches.append({
                    'branch': job_station_product.branch,
                    'product': job_station_product.product.name,
                    'unloading_stations': [{
                        'unloading_station': {
                            'address': job_station.station.address,
                            'time': job_station_product.due_time.strftime("%Y-%m-%d %H:%M")
                        },
                        'weight': str(job_station_product.mission_weight)
                        + order_product.get_weight_measure_unit_display()
                    }]
                })

    return branches


def get_mileage(plate_num, from_datetime, to_datetime):
    mileage = 0
    middle_datetime = from_datetime
    while True:
        if to_datetime > from_datetime + timedelta(days=30):
            middle_datetime = from_datetime + timedelta(days=30)
        else:
            middle_datetime = to_datetime

        queries = {
            'plate_num': plate_num,
            'from': from_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'to': middle_datetime.strftime('%Y-%m-%d %H:%M:%S')
        }
        try:
            ret = G7Interface.call_g7_http_interface(
                'VEHICLE_GPS_TOTAL_MILEAGE_INQUIRY',
                queries=queries
            )
            if ret is not None:
                mileage += ret.get('total_mileage', 0) / (100 * 1000)   # calculated in km

            from_datetime = middle_datetime
            if middle_datetime == to_datetime:
                break
        except Exception:
            break

    return mileage
