from django.contrib import admin
from . import models as m


@admin.register(m.DriverJobNotification)
class DriverJobNotificationAdmin(admin.ModelAdmin):
    pass
