from django.core.management.base import BaseCommand
from tms.vehicle.models import Vehicle, VehicleWorkerBind
from tms.hr.models import StaffProfile
from tms.core import constants as c


class Command(BaseCommand):
    help = 'Recalculate the mileage'

    def handle(self, *args, **options):
        for vehicle in Vehicle.objects.all():
            vehicle.status = c.VEHICLE_STATUS_AVAILABLE
            vehicle.save()

        for worker in StaffProfile.objects.all():
            if worker.user.user_type in [c.USER_TYPE_DRIVER, c.USER_TYPE_ESCORT,
                                         c.USER_TYPE_GUEST_DRIVER, c.USER_TYPE_GUEST_ESCORT]:
                worker.status = c.WORK_STATUS_AVAILABLE
                worker.save()

        VehicleWorkerBind.objects.all().delete()
