SYSTEM_HEADERS = (
    X_CA_SIGNATURE, X_CA_TIMESTAMP
) = (
    'Authorization',  'X-G7-OpenAPI-Timestamp'
)

SYSTEM_MARKER = (
    AUTH_PREFIX, SPE2_COLON
) = (
    'g7ac', ':'
)


HTTP_HEADERS = (
    HTTP_HEADER_CONTENT_MD5,
    HTTP_HEADER_CONTENT_TYPE, HTTP_HEADER_USER_AGENT, HTTP_HEADER_DATE
) = (
    'Content-MD5',
    'Content-Type', 'User-Agent', 'Date'
)

HTTP_PROTOCOL = (
    HTTP, HTTPS
) = (
    'http', 'https'
)

HTTP_METHOD = (
    GET, POST, PUT, DELETE, HEADER
) = (
    'GET', 'POST', 'PUT', 'DELETE', 'HEADER'
)

CONTENT_TYPE = (
    CONTENT_TYPE_STREAM,
    CONTENT_TYPE_JSON, CONTENT_TYPE_XML, CONTENT_TYPE_TEXT
) = (
    'application/octet-stream',
    'application/json; charset=UTF-8', 'application/xml', 'application/text'
)

BODY_TYPE = (
    FORM, STREAM
) = (
    'FORM', 'STREAM'
)
