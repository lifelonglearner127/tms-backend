from django.contrib import admin

from . import models as m


@admin.register(m.Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    pass


@admin.register(m.VehicleMaintenanceRequest)
class VehicleMaintenanceRequestAdmin(admin.ModelAdmin):
    pass


@admin.register(m.VehicleUserBind)
class VehicleUserBindAdmin(admin.ModelAdmin):
    pass
