"""
method: post

request body format:
    @string carnum: Required; license plate number,
    @string isheadstock: Required; whether vehicle is front or tailer
    @string orgcode: Required; affiliate number

response body format:
    @int code: Gateway error code, 0 means success
    @string msg: Gateway error description
    @int sub_code: Business return code, 0 means success
    @string sub_msg: Business return description
    @string req_id: requested uuid
    @object data: If both code and sub_code are 0, this field exists
        @string carnum: license plate number
        @string truckid: vehicle id
        @string ownid: vehicle's relationship id
        @string optype: operation type
        @boolean op_result: operation result
        @string op_message: operation description
        @int op_code: operation code, 0 means success

"""

"""
method: post
request body format:
    @string carnum_like: License plate number fuzzy matching, left and right matching
    @int isbind: Whether to bind the device, 0 is not bound, 1 is bound, no transmission is not distinguished
    @string orgcode_like: Institution number, right match
    @string updatetime_ge: Update time, greater than or equal to
    @int deleted: Query data according to the deletion status, 0-> not deleted, 1-> deleted, 2-> all
    @int get_count: Whether to return the total number, if the parameter is passed in, the returned result only contains the total number of eligible conditions
    @int page_no: page number
    @int page_size: Number of pages per page

response body format:
    @string truckid: primary key
    @string carnum: number plate
    @int gpsno: Device No
    @string ownid: OWN table primary key ID
    @string orgcode: Affiliation
    @string fromorgcode: Source organization number
    @int fromtype: Type, 1 self-built, 2 internal sharing, 3 external sharing, 4 external car
    @string aliasname: Vehicle alias
    @string maindriver_id: Driver ID
    @string depdriver_id: Deputy driver ID
    @int lockstatus: Whether to bind ETC card 0: unbound 1: bound
    @int truckmodelid: Model ID
"""
