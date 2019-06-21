from django.contrib import admin
from . import models as m


@admin.register(m.Notification)
class NotificationAdmin(admin.ModelAdmin):
    pass
