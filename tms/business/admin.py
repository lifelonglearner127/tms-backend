from django.contrib import admin

from . import models as m


@admin.register(m.RestRequest)
class RestRequestAdmin(admin.ModelAdmin):
    pass


@admin.register(m.ParkingRequest)
class ParkingRequestAdmin(admin.ModelAdmin):
    pass


@admin.register(m.DriverChangeRequest)
class DriverChangeRequestAdmin(admin.ModelAdmin):
    pass


@admin.register(m.EscortChangeRequest)
class EscortChangeRequestAdmin(admin.ModelAdmin):
    pass
