import json
from django.conf import settings

from com.chinawayltd.api.gateway.sdk import client
from com.chinawayltd.api.gateway.sdk.http import request
from com.chinawayltd.api.gateway.sdk.common import constant

from .endpoints import G7_OPENAPI_ENDPOINTS


vehicle_basic_client = client.DefaultClient(
    app_key=settings.OPENAPI_VEHICLE_BASIC_ACCESS_ID,
    app_secret=settings.OPENAPI_VEHICLE_BASIC_SECRET
)

vehicle_data_client = client.DefaultClient(
    app_key=settings.OPENAPI_VEHICLE_DATA_ACCESS_ID,
    app_secret=settings.OPENAPI_VEHICLE_DATA_SECRET
)


class G7Interface:

    @staticmethod
    def call_g7_http_interface(api_name, body=None, queries=None):
        cli = None
        api_call = None

        for module_name, module in G7_OPENAPI_ENDPOINTS.items():
            for name, api in module.items():
                if name == api_name:
                    if module_name == 'VEHICLE_BASIC':
                        cli = vehicle_basic_client
                    elif module_name == 'VEHICLE_DATA':
                        cli = vehicle_data_client
                    api_call = api
                    break

        if cli is None or api_call is None:
            return

        req = request.Request(
            host=settings.OPENAPI_HOST,
            protocol=constant.HTTP,
            baseurl=settings.OPENAPI_BASEURL,
            url=api_call['URL'],
            method=api_call['METHOD'],
            time_out=30000
        )

        if queries is not None:
            req.set_queries(queries)

        if body is not None:
            req.set_body(json.dumps(body))
            req.set_content_type(constant.CONTENT_TYPE_JSON)

        try:
            status, headers, body = cli.execute(req)
            if status != 200:
                # TODO: logging
                err_str = 'G7 Interface return non-success status code'
                raise Exception(err_str)

            body = json.loads(body.decode('utf-8'))
            if body['code'] or body['sub_code']:
                # TODO: logging
                raise Exception(body)

            return body['data']
        except Exception as e:
            print(e)
            # TODO: logging
