from django.contrib import admin

from . import models as m


@admin.register(m.Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    pass


@admin.register(m.VehicleDocument)
class VehicleDocumentAdmin(admin.ModelAdmin):
    pass
