# Info app - Product constants
# ----------------------------------------------------------------------------
# product type choices
PRODUCT_TYPE_GASOLINE = 'gas'
PRODUCT_TYPE_OIL = 'oil'
PRODUCT_TYPE = (
    (PRODUCT_TYPE_GASOLINE, 'Gas'),
    (PRODUCT_TYPE_OIL, 'Oil')
)

# station type
STATION_TYPE_LOADING_STATION = 'L'
STATION_TYPE_UNLOADING_STATION = 'U'
STATION_TYPE_QUALITY_STATION = 'Q'
STATION_TYPE_OIL_STATION = 'O'
STATION_TYPE = (
    (STATION_TYPE_LOADING_STATION, 'Loading Station'),
    (STATION_TYPE_UNLOADING_STATION, 'Unloading Station'),
    (STATION_TYPE_QUALITY_STATION, 'Quality Station'),
    (STATION_TYPE_OIL_STATION, 'Oil Station')
)

# duration unit choices
DURATION_UNIT_MINITE = 'M'
DURATION_UNIT_HOUR = 'H'
DURATION_UNIT = (
    (DURATION_UNIT_MINITE, 'Minute'),
    (DURATION_UNIT_HOUR, 'Hour'),
)


# Vehicle app - Vehicle constants
# ----------------------------------------------------------------------------
# vehicle model choices
VEHICLE_MODEL_TYPE_TRUCK = 'T'
VEHICLE_MODEL_TYPE_SEMI_TRAILER = 'S'
VEHICLE_MODEL_TYPE = (
    (VEHICLE_MODEL_TYPE_TRUCK, 'Truck'),
    (VEHICLE_MODEL_TYPE_SEMI_TRAILER, 'Semi-trailer')
)

# vehicle brand choices
VEHICLE_BRAND_TONGHUA = 'T'
VEHICLE_BRAND_LIBERATION = 'L'
VEHICLE_BRAND_YANGZHOU = 'Y'
VEHICLE_BRAND = (
    (VEHICLE_BRAND_TONGHUA, 'Tonghua'),
    (VEHICLE_BRAND_LIBERATION, 'Liberation'),
    (VEHICLE_BRAND_YANGZHOU, 'Yangzhou')
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
    (USER_ROLE_ADMIN, 'Admin'),
    (USER_ROLE_STAFF, 'Staff'),
    (USER_ROLE_DRIVER, 'Driver'),
    (USER_ROLE_ESCORT, 'Escort'),
    (USER_ROLE_CUSTOMER, 'Customer')
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
    (ORDER_SOURCE_INTERNAL, 'From Staff'),
    (ORDER_SOURCE_CUSTOMER, 'From Customer')
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
    (JOB_PROGRESS_NOT_STARTED, 'Job Progress - Not Started'),
    (JOB_PROGRESS_COMPLETE, 'Job Progress - Completed'),
    (JOB_PROGRESS_TO_LOADING_STATION, 'Job Progress - To Loading Station'),
    (JOB_PROGRESS_ARRIVED_AT_LOADING_STATION, 'Job Progress - Arrived at Loading Station'),
    (JOB_PROGRESS_LOADING_AT_LOADING_STATION, 'Job Progress - Loading at Loading Station'),
    (JOB_PROGRESS_FINISH_LOADING_AT_LOADING_STATION, 'Job Progress - Finish Loading at Loading Station'),
    (JOB_PROGRESS_TO_QUALITY_STATION, 'Job Progress - To Quality Station'),
    (JOB_PROGRESS_ARRIVED_AT_QUALITY_STATION, 'Job Progress - Arrived at Quality Station'),
    (JOB_PROGRESS_CHECKING_AT_QUALITY_STATION, 'Job Progress - Checking at Quality Station'),
    (JOB_PROGRESS_FINISH_CHECKING_AT_QUALITY_STATION, 'Job Progress - Finish Checking at Quality Station'),
    (JOB_PROGRESS_TO_UNLOADING_STATION, 'Job Progress - To Unloading Station'),
    (JOB_PRGORESS_ARRIVED_AT_UNLOADING_STATION, 'Job Progress - Arrived at Unloading Station'),
    (JOB_PROGRESS_UNLOADING_AT_UNLOADING_STATION, 'Job Progress - Unloading at Unloading Station'),
    (JOB_PROGRESS_FINISH_UNLOADING_AT_UNLOADING_STATION, 'Job Progress - Finish Unloading Station')
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

POINT_TYPE_LOADING_STATION = 'L'
POINT_TYPE_UNLOADING_STATION = 'U'
POINT_TYPE_QUALITY_STATION = 'Q'
POINT_TYPE_OIL_STATION = 'O'
POINT_TYPE = (
    (POINT_TYPE_LOADING_STATION, 'Loading Station'),
    (POINT_TYPE_UNLOADING_STATION, 'Unloading Station'),
    (POINT_TYPE_QUALITY_STATION, 'Quality Station'),
    (POINT_TYPE_OIL_STATION, 'Oil Station')
)


# Metric Units constants
# ----------------------------------------------------------------------------
UNIT_WEIGHT_TON = 'T'
UNIT_WEIGHT_KILOGRAM = 'K'
UNIT_WEIGHT = (
    (UNIT_WEIGHT_TON, 't'),
    (UNIT_WEIGHT_KILOGRAM, 'Kg')
)
