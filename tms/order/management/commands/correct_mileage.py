from django.core.management.base import BaseCommand
from tms.order.models import Job
from tms.g7.interfaces import G7Interface


class Command(BaseCommand):
    help = 'Recalculate the mileage'

    def handle(self, *args, **options):
        for job in Job.completed_jobs.all():
            loading_station_arrived_on = job.jobstation_set.get(step=0).arrived_station_on

            empty_mileage_queries = {
                'plate_num':
                    job.vehicle.plate_num,
                'from':
                    job.started_on.strftime('%Y-%m-%d %H:%M:%S'),
                'to':
                    loading_station_arrived_on.strftime(
                        '%Y-%m-%d %H:%M:%S'
                    )
            }
            heavy_mileage_queries = {
                'plate_num':
                    job.vehicle.plate_num,
                'from':
                    loading_station_arrived_on.strftime(
                        '%Y-%m-%d %H:%M:%S'
                    ),
                'to':
                    job.finished_on.strftime(
                        '%Y-%m-%d %H:%M:%S'
                    )
            }
            try:
                data = G7Interface.call_g7_http_interface(
                    'VEHICLE_GPS_TOTAL_MILEAGE_INQUIRY',
                    queries=empty_mileage_queries
                )
                empty_mileage = data['total_mileage'] / (100 * 1000)
                data = G7Interface.call_g7_http_interface(
                    'VEHICLE_GPS_TOTAL_MILEAGE_INQUIRY',
                    queries=heavy_mileage_queries
                )
                heavy_mileage = data['total_mileage'] / (100 * 1000)
            except Exception:
                empty_mileage = 0
                heavy_mileage = 0

            job.empty_mileage = empty_mileage
            job.heavy_mileage = heavy_mileage
            job.total_mileage = job.empty_mileage + job.heavy_mileage
            job.highway_mileage = 0
            job.normalway_mileage = 0
            job.save()
