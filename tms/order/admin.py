from django.contrib import admin

from . import models as m


@admin.register(m.Order)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(m.OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    pass


@admin.register(m.OrderReport)
class OrderReportProductAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Job)
class JobAdmin(admin.ModelAdmin):
    pass


@admin.register(m.LoadingStationProductCheck)
class LoadingStationProductCheckAdmin(admin.ModelAdmin):
    pass


@admin.register(m.JobStation)
class JobStationAdmin(admin.ModelAdmin):
    pass


@admin.register(m.JobStationProduct)
class JobStationProductAdmin(admin.ModelAdmin):
    pass


@admin.register(m.JobReport)
class JobReportAdmin(admin.ModelAdmin):
    pass


@admin.register(m.VehicleUserBind)
class VehicleUserBindAdmin(admin.ModelAdmin):
    pass
