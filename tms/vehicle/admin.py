from django.contrib import admin

from . import models as m


@admin.register(m.Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    pass


@admin.register(m.VehicleDriverDailyBind)
class VehicleDriverDailyBindAdmin(admin.ModelAdmin):
    pass


@admin.register(m.VehicleCheckDocument)
class VehicleCheckDocumentAdmin(admin.ModelAdmin):
    pass


@admin.register(m.VehicleCheckHistory)
class VehicleCheckHistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(m.VehicleBeforeDrivingItemCheck)
class VehicleBeforeDrivingItemCheckAdmin(admin.ModelAdmin):
    pass


@admin.register(m.VehicleDrivingItemCheck)
class VehicleDrivingItemCheckAdmin(admin.ModelAdmin):
    pass


@admin.register(m.VehicleAfterDrivingItemCheck)
class VehicleAfterDrivingItemCheckAdmin(admin.ModelAdmin):
    pass
