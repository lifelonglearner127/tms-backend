import math
from datetime import timedelta
from ..g7.interfaces import G7Interface


x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626
a = 6378245.0
ee = 0.00669342162296594323


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


def out_of_china(lng, lat):
    return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)


def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


def gcj02_to_wgs84(lng, lat):
    if out_of_china(lng, lat):
        return [lng, lat]
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]
