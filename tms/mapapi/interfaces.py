import requests

from django.conf import settings

from .endpoints import MAPAPI_ENDPOINTS


class GaodeoMapAPI:

    @staticmethod
    def call_map_api_interface(api_name, queries):
        queries['key'] = settings.MAP_WEB_SERVICE_API_KEY

        r = requests.get(
            MAPAPI_ENDPOINTS[api_name]['URL'], params=queries
        )

        response = r.json()
        if response['errcode'] != 0:
            return None
        return response
