from django.contrib import admin

from .models import Vehicle, VehicleDocument


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    pass


@admin.register(VehicleDocument)
class VehicleDocumentAdmin(admin.ModelAdmin):
    pass
