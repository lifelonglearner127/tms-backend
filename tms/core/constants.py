# Info app - Product constants
# ----------------------------------------------------------------------------
PRODUCT_TYPE_GASOLINE = 'gas'
PRODUCT_TYPE_OIL = 'oil'
PRODUCT_TYPE = (
    (PRODUCT_TYPE_GASOLINE, 'Gas'),
    (PRODUCT_TYPE_OIL, 'Oil')
)


# Info app - Product constants
# ----------------------------------------------------------------------------
DURATION_UNIT_MINITE = 'M'
DURATION_UNIT_HOUR = 'H'
DURATION_UNIT = (
    (DURATION_UNIT_MINITE, 'Minute'),
    (DURATION_UNIT_HOUR, 'Hour'),
)


# Vehicle app - Vehicle constants
# ----------------------------------------------------------------------------
VEHICLE_MODEL_TYPE_TRUCK = 'T'
VEHICLE_MODEL_TYPE_SEMI_TRAILER = 'S'
VEHICLE_MODEL_TYPE = (
    (VEHICLE_MODEL_TYPE_TRUCK, 'Truck'),
    (VEHICLE_MODEL_TYPE_SEMI_TRAILER, 'Semi-trailer')
)

VEHICLE_BRAND_TONGHUA = 'T'
VEHICLE_BRAND_LIBERATION = 'L'
VEHICLE_BRAND_YANGZHOU = 'Y'
VEHICLE_BRAND = (
    (VEHICLE_BRAND_TONGHUA, 'Tonghua'),
    (VEHICLE_BRAND_LIBERATION, 'Liberation'),
    (VEHICLE_BRAND_YANGZHOU, 'Yangzhou')
)


# Account app - Account constants
# ----------------------------------------------------------------------------
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


# Account app - Account constants
# ----------------------------------------------------------------------------
USER_DOCUMENT_TYPE_D1 = '1'
USER_DOCUMENT_TYPE_D2 = '2'
USER_DOCUMENT_TYPE = (
    (USER_DOCUMENT_TYPE_D1, 'D1'),
    (USER_DOCUMENT_TYPE_D2, 'D2')
)


# Job app - Job status constants
# ----------------------------------------------------------------------------
JOB_STATUS_PENDING = 'P'
JOB_STATUS_INPROGRESS = 'I'
JOB_STATUS_COMPLETE = 'C'
JOB_STATUS = (
    (JOB_STATUS_PENDING, 'Pending'),
    (JOB_STATUS_INPROGRESS, 'In Progress'),
    (JOB_STATUS_COMPLETE, 'Complete')
)


# Order app - Order status constants
# ----------------------------------------------------------------------------
ORDER_STATUS_PENDING = 'P'
ORDER_STATUS_INPROGRESS = 'I'
ORDER_STATUS_COMPLETE = 'C'
ORDER_STATUS = (
    (ORDER_STATUS_PENDING, 'Pending'),
    (ORDER_STATUS_INPROGRESS, 'In Progress'),
    (ORDER_STATUS_COMPLETE, 'Complete')
)


# Order app - Order source constants
# ----------------------------------------------------------------------------
ORDER_SOURCE_INTERNAL = 'I'
ORDER_SOURCE_CUSTOMER = 'C'
ORDER_SOURCE = (
    (ORDER_SOURCE_INTERNAL, 'From Staff'),
    (ORDER_SOURCE_CUSTOMER, 'From Customer')
)


# Metric Units constants
# ----------------------------------------------------------------------------
UNIT_WEIGHT_TON = 'T'
UNIT_WEIGHT_KILOGRAM = 'K'
UNIT_WEIGHT = (
    (UNIT_WEIGHT_TON, 't'),
    (UNIT_WEIGHT_KILOGRAM, 'Kg')
)
