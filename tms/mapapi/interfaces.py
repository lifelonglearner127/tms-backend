from itertools import groupby
import requests

from django.conf import settings

from .endpoints import MAPAPI_ENDPOINTS


class RoutePlanInterface:

    @staticmethod
    def call_map_api_interface(origin, destination):
        queries = {
            'key': settings.MAP_WEB_SERVICE_API_KEY,
            'origin': ','.join(map(str, origin)),
            'destination': ','.join(map(str, destination)),
            'size': 2
        }

        r = requests.get(
            MAPAPI_ENDPOINTS['RoutePlan']['URL'], params=queries
        )

        response = r.json()
        if response['errcode'] != 0:
            return None

        paths = []
        for path in response['data']['route']['paths']:
            polylines = []
            for step in path['steps']:
                polylines.extend([
                    [float(p) for p in point.split(',')]
                    for point in step['polyline'].split(';')
                ])
            paths.append([x[0] for x in groupby(polylines)])

        return paths
