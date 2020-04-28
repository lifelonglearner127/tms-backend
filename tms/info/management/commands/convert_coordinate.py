from django.core.management.base import BaseCommand
from tms.info.models import Station
from tms.core.utils import gcj02_to_wgs84


class Command(BaseCommand):
    help = 'Recalculate the mileage'

    def handle(self, *args, **options):
        for station in Station.objects.all():
            longitude = float(station.longitude)
            latitude = float(station.latitude)
            new_coords = gcj02_to_wgs84(longitude, latitude)
            station.gps_longitude = new_coords[0]
            station.gps_latitude = new_coords[1]
            station.save()
