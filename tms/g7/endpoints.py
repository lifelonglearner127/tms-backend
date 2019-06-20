G7_HTTP_ENDPOINTS = {
    'VEHICLE_BASIC': {
        'VEHICLE_ADD': {
            'URL': '/v1/base/truck/add_self_truck',
            'METHOD': 'POST'
        },
        'VEHICLE_DELETE': {
            'URL': '/v1/base/truck/truck_delete',
            'METHOD': 'POST'
        },
        'VEHICLE_INQUIRY': {
            'URL': '/v1/base/truck/truck_info',
            'METHOD': 'POST'
        },
        'VEHICLE_LIST': {
            'URL': '/v1/base/truck/truck_list',
            'METHOD': 'POST'
        },
        'VEHICLE_CHECK_DETAIL': {
            'URL': '/v1/base/truck/truckinfo_include_custom_fields',
            'METHOD': 'POST'
        },
        'VEHICLE_MODEL_DETAIL': {
            'URL': '/v1/base/truck/get_truck_model_info',
            'METHOD': 'POST'
        },
        'VEHICLE_UPDATE': {
            'URL': '/v1/base/truck/update_self_truck',
            'METHOD': 'POST'
        },
        'VEHICLE_INTERNAL_SHARE': {
            'URL': '/v1/base/truck/add_truck_internal_share',
            'METHOD': 'POST'
        }
    },
    'VEHICLE_DATA': {
        'VEHICLE_HISTORY_TRACK_QUERY': {
            'URL': '/v1/device/truck/history_location',
            'METHOD': 'GET'
        },
        'VEHICLE_GPS_TOTAL_MILEAGE_INQUIRY': {
            'URL': '/v1/device/truck/mileage',
            'METHOD': 'GET'
        },
        'VEHICLE_GPS_DAILY_MILEAGE_INQUIRY': {
            'URL': '/v1/device/truck/mileage_daily',
            'METHOD': 'GET'
        },
        'VEHICLE_STATUS_INQUIRY': {
            'URL': '/v1/device/truck/current_info',
            'METHOD': 'GET'
        },
        'VEHICLE_STATUS_BY_GPS': {
            'URL': '/v1/device/truck/current_info_by_gpsno',
            'METHOD': 'GET'
        },
        'BULK_VEHICLE_STATUS_INQUIRY': {
            'URL': '/v1/device/truck/current_info/batch',
            'METHOD': 'POST'
        },
        'BULK_VEHICLE_STATUS_BY_GPS': {
            'URL': '/v1/device/truck/current_info_by_gpsno',
            'METHOD': 'POST'
        },
        'GET_MILEAGE': {
            'URL': '/v1/device/gps/getTruckMileage',
            'METHOD': 'POST'
        }
    }
}
