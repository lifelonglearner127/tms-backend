from django.contrib import admin

from . import models as m


@admin.register(m.Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    pass


@admin.register(m.VehicleMaintenanceRequest)
class VehicleMaintenanceRequestAdmin(admin.ModelAdmin):
    pass


@admin.register(m.VehicleBeforeDrivingDocument)
class VehicleBeforeDrivingDocumentAdmin(admin.ModelAdmin):
    pass


@admin.register(m.VehicleBeforeDrivingCheckHistory)
class VehicleBeforeDrivingCheckHistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(m.VehicleBeforeDrivingItemCheck)
class VehicleBeforeDrivingItemCheckAdmin(admin.ModelAdmin):
    pass


@admin.register(m.VehicleDrivingDocument)
class VehicleDrivingDocumentAdmin(admin.ModelAdmin):
    pass


@admin.register(m.VehicleDrivingCheckHistory)
class VehicleDrivingCheckHistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(m.VehicleDrivingItemCheck)
class VehicleDrivingItemCheckAdmin(admin.ModelAdmin):
    pass


@admin.register(m.VehicleAfterDrivingDocument)
class VehicleAfterDrivingDocumentAdmin(admin.ModelAdmin):
    pass


@admin.register(m.VehicleAfterDrivingCheckHistory)
class VehicleAfterDrivingCheckHistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(m.VehicleAfterDrivingItemCheck)
class VehicleAfterDrivingItemCheckAdmin(admin.ModelAdmin):
    pass
