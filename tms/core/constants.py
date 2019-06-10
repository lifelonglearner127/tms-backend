# Info app
# ----------------------------------------------------------------------------
# product type choices
PRODUCT_TYPE_GASOLINE = 'G'
PRODUCT_TYPE_OIL = 'O'
PRODUCT_TYPE = (
    (PRODUCT_TYPE_GASOLINE, '汽油'),
    (PRODUCT_TYPE_OIL, '油')
)

# station type
STATION_TYPE_LOADING_STATION = 'L'
STATION_TYPE_UNLOADING_STATION = 'U'
STATION_TYPE_QUALITY_STATION = 'Q'
STATION_TYPE_OIL_STATION = 'O'
STATION_TYPE = (
    (STATION_TYPE_LOADING_STATION, '装货地'),
    (STATION_TYPE_UNLOADING_STATION, '卸货地'),
    (STATION_TYPE_QUALITY_STATION, '质检点'),
    (STATION_TYPE_OIL_STATION, '合作油站')
)

# duration unit choices
TIME_MEASURE_UNIT_MINITE = 'M'
TIME_MEASURE_UNIT_HOUR = 'H'
TIME_MEASURE_UNIT = (
    (TIME_MEASURE_UNIT_MINITE, '分钟'),
    (TIME_MEASURE_UNIT_HOUR, '小时'),
)

PRICE_VARY_DURATION_UNIT_WEEK = 'W'
PRICE_VARY_DURATION_UNIT_MONTH = 'M'
PRICE_VARY_DURATION_UNIT_YEAR = 'Y'
PRICE_VARY_DURATION_UNIT = (
    (PRICE_VARY_DURATION_UNIT_WEEK, '周'),
    (PRICE_VARY_DURATION_UNIT_MONTH, '月'),
    (PRICE_VARY_DURATION_UNIT_YEAR, '年')
)

# product unit measure choices
PRODUCT_MEASURE_UNIT_LITRE = 'L'
PRODUCT_MEASURE_UNIT_TON = 'T'
PRODUCT_MEASURE_UNIT = (
    (PRODUCT_MEASURE_UNIT_LITRE, '公升'),
    (PRODUCT_MEASURE_UNIT_TON, '吨')
)


# Vehicle app - Vehicle constants
# ----------------------------------------------------------------------------
# vehicle model choices
VEHICLE_MODEL_TYPE_TRUCK = 'T'
VEHICLE_MODEL_TYPE_SEMI_TRAILER = 'S'
VEHICLE_MODEL_TYPE = (
    (VEHICLE_MODEL_TYPE_TRUCK, '牵引车'),
    (VEHICLE_MODEL_TYPE_SEMI_TRAILER, '半挂罐车')
)

# vehicle brand choices
VEHICLE_BRAND_TONGHUA = 'T'
VEHICLE_BRAND_LIBERATION = 'L'
VEHICLE_BRAND_YANGZHOU = 'Y'
VEHICLE_BRAND = (
    (VEHICLE_BRAND_TONGHUA, '通华'),
    (VEHICLE_BRAND_LIBERATION, '解放'),
    (VEHICLE_BRAND_YANGZHOU, '扬州中集')
)

# vehicle document type choices
VEHICLE_DOCUMENT_TYPE_D1 = '1'
VEHICLE_DOCUMENT_TYPE_D2 = '2'
VEHICLE_DOCUMENT_TYPE = (
    (VEHICLE_DOCUMENT_TYPE_D1, 'D1'),
    (VEHICLE_DOCUMENT_TYPE_D2, 'D2')
)

# vehicle status
VEHICLE_STATUS_AVAILABLE = 'A'
VEHICLE_STATUS_INWORK = 'P'
VEHICLE_STATUS_REPAIR = 'R'
VEHICLE_STATUS = (
    (VEHICLE_STATUS_AVAILABLE, 'Available'),
    (VEHICLE_STATUS_INWORK, 'In Work'),
    (VEHICLE_STATUS_REPAIR, 'Repair')
)

# Account app - Account constants
# ----------------------------------------------------------------------------
# user role choices
USER_ROLE_ADMIN = 'A'
USER_ROLE_STAFF = 'S'
USER_ROLE_DRIVER = 'D'
USER_ROLE_ESCORT = 'E'
USER_ROLE_CUSTOMER = 'C'
USER_ROLE = (
    (USER_ROLE_ADMIN, '管理人员'),
    (USER_ROLE_STAFF, '工作人员'),
    (USER_ROLE_DRIVER, '驾驶人员'),
    (USER_ROLE_ESCORT, '押运人员'),
    (USER_ROLE_CUSTOMER, '客户')
)

# driver status
DRIVER_STATUS_AVAILABLE = 'A'
DRIVER_STATUS_INWORK = 'W'
DRIVER_STATUS = (
    (DRIVER_STATUS_AVAILABLE, 'Available'),
    (DRIVER_STATUS_INWORK, 'In Work')
)

# user document type choices
USER_DOCUMENT_TYPE_D1 = '1'
USER_DOCUMENT_TYPE_D2 = '2'
USER_DOCUMENT_TYPE = (
    (USER_DOCUMENT_TYPE_D1, 'D1'),
    (USER_DOCUMENT_TYPE_D2, 'D2')
)


# Order app - Order status constants
# ----------------------------------------------------------------------------
# order status choices
ORDER_STATUS_PENDING = 'P'
ORDER_STATUS_INPROGRESS = 'I'
ORDER_STATUS_COMPLETE = 'C'
ORDER_STATUS = (
    (ORDER_STATUS_PENDING, 'Pending'),
    (ORDER_STATUS_INPROGRESS, 'In Progress'),
    (ORDER_STATUS_COMPLETE, 'Complete')
)

# order source choices
ORDER_SOURCE_INTERNAL = 'I'
ORDER_SOURCE_CUSTOMER = 'C'
ORDER_SOURCE = (
    (ORDER_SOURCE_INTERNAL, '内部'),
    (ORDER_SOURCE_CUSTOMER, 'App')
)

# payment method choices
PAYMENT_METHOD_TON = 'T'
PAYMENT_METHOD_TON_PER_DISTANCE = 'D'
PAYMENT_METHOD_PRICE = 'P'
PAYMENT_METHOD = (
    (PAYMENT_METHOD_TON, '吨'),
    (PAYMENT_METHOD_TON_PER_DISTANCE, '吨/公里'),
    (PAYMENT_METHOD_PRICE, '一口价')
)


# job app
# ----------------------------------------------------------------------------
# job status choices
JOB_PROGRESS_NOT_STARTED = 0
JOB_PROGRESS_COMPLETE = 1
JOB_PROGRESS_TO_LOADING_STATION = 2
JOB_PROGRESS_ARRIVED_AT_LOADING_STATION = 3
JOB_PROGRESS_LOADING_AT_LOADING_STATION = 4
JOB_PROGRESS_FINISH_LOADING_AT_LOADING_STATION = 5
JOB_PROGRESS_TO_QUALITY_STATION = 6
JOB_PROGRESS_ARRIVED_AT_QUALITY_STATION = 7
JOB_PROGRESS_CHECKING_AT_QUALITY_STATION = 8
JOB_PROGRESS_FINISH_CHECKING_AT_QUALITY_STATION = 9
JOB_PROGRESS_TO_UNLOADING_STATION = 10
JOB_PRGORESS_ARRIVED_AT_UNLOADING_STATION = 11
JOB_PROGRESS_UNLOADING_AT_UNLOADING_STATION = 12
JOB_PROGRESS_FINISH_UNLOADING_AT_UNLOADING_STATION = 13

JOB_PROGRESS = (
    (
        JOB_PROGRESS_NOT_STARTED,
        'Job Progress - Not Started'
    ),
    (
        JOB_PROGRESS_COMPLETE,
        'Job Progress - Completed'
    ),
    (
        JOB_PROGRESS_TO_LOADING_STATION,
        'Job Progress - To Loading Station'
    ),
    (
        JOB_PROGRESS_ARRIVED_AT_LOADING_STATION,
        'Job Progress - Arrived at Loading Station'
    ),
    (
        JOB_PROGRESS_LOADING_AT_LOADING_STATION,
        'Job Progress - Loading at Loading Station'
    ),
    (
        JOB_PROGRESS_FINISH_LOADING_AT_LOADING_STATION,
        'Job Progress - Finish Loading at Loading Station'
    ),
    (
        JOB_PROGRESS_TO_QUALITY_STATION,
        'Job Progress - To Quality Station'
    ),
    (
        JOB_PROGRESS_ARRIVED_AT_QUALITY_STATION,
        'Job Progress - Arrived at Quality Station'
    ),
    (
        JOB_PROGRESS_CHECKING_AT_QUALITY_STATION,
        'Job Progress - Checking at Quality Station'
    ),
    (
        JOB_PROGRESS_FINISH_CHECKING_AT_QUALITY_STATION,
        'Job Progress - Finish Checking at Quality Station'
    ),
    (
        JOB_PROGRESS_TO_UNLOADING_STATION,
        'Job Progress - To Unloading Station'
    ),
    (
        JOB_PRGORESS_ARRIVED_AT_UNLOADING_STATION,
        'Job Progress - Arrived at Unloading Station'
    ),
    (
        JOB_PROGRESS_UNLOADING_AT_UNLOADING_STATION,
        'Job Progress - Unloading at Unloading Station'
    ),
    (
        JOB_PROGRESS_FINISH_UNLOADING_AT_UNLOADING_STATION,
        'Job Progress - Finish Unloading Station'
    )
)

# bill document type
BILL_FROM_OIL_STATION = 'O'
BILL_FROM_LOADING_STATION = 'L'
BILL_FROM_UNLOADING_STATION = 'U'
BILL_FROM_QUALITY_STATION = 'Q'
BILL_TYPE = (
    (BILL_FROM_OIL_STATION, 'Bill from Oil Station'),
    (BILL_FROM_LOADING_STATION, 'Bill from Loading Station'),
    (BILL_FROM_UNLOADING_STATION, 'Bill from UnLoading Station'),
    (BILL_FROM_QUALITY_STATION, 'Bill from Quality Station')
)

# road app
# ----------------------------------------------------------------------------
BLACKDOT_TYPE_ROAD_REPAIR = 'R'
BLACKDOT_TYPE_ROAD_LIMIT_TIME = 'L'
BLACKDOT_TYPE = (
    (BLACKDOT_TYPE_ROAD_REPAIR, 'Repair Road'),
    (BLACKDOT_TYPE_ROAD_LIMIT_TIME, 'Time Limit')
)

POINT_TYPE_LOADING_STATION = STATION_TYPE_LOADING_STATION
POINT_TYPE_UNLOADING_STATION = STATION_TYPE_UNLOADING_STATION
POINT_TYPE_QUALITY_STATION = STATION_TYPE_QUALITY_STATION
POINT_TYPE_OIL_STATION = STATION_TYPE_OIL_STATION
POINT_TYPE_BLACK_DOT = 'B'
POINT_TYPE = (
    (POINT_TYPE_LOADING_STATION, '装货点'),
    (POINT_TYPE_UNLOADING_STATION, '卸货点'),
    (POINT_TYPE_QUALITY_STATION, '质检点'),
    (POINT_TYPE_OIL_STATION, '合作油站点'),
    (POINT_TYPE_BLACK_DOT, '黑点')
)


# Metric Units constants
# ----------------------------------------------------------------------------
UNIT_WEIGHT_TON = 'T'
UNIT_WEIGHT_KILOGRAM = 'K'
UNIT_WEIGHT = (
    (UNIT_WEIGHT_TON, 't'),
    (UNIT_WEIGHT_KILOGRAM, 'Kg')
)
