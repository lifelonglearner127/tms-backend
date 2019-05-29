from django.contrib import admin

from . import models as m


@admin.register(m.Job)
class JobAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Mission)
class MissionAdmin(admin.ModelAdmin):
    pass


@admin.register(m.JobBillDocument)
class JobBillDocumentAdmin(admin.ModelAdmin):
    pass


@admin.register(m.DriverNotification)
class DriverNotificationAdmin(admin.ModelAdmin):
    pass
