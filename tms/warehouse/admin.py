from django.contrib import admin

from . import models as m


@admin.register(m.WarehouseProduct)
class WarehouseProductAdmin(admin.ModelAdmin):
    pass


@admin.register(m.InTransaction)
class InTransactionAdmin(admin.ModelAdmin):
    pass


@admin.register(m.OutTransaction)
class OutTransactionAdmin(admin.ModelAdmin):
    pass
