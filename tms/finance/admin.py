from django.contrib import admin

from . import models as m


@admin.register(m.ETCCard)
class ETCCardAdmin(admin.ModelAdmin):
    pass


@admin.register(m.ETCCardChargeHistory)
class ETCCardChargeHistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(m.ETCBillHistory)
class ETCBillHistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(m.ETCBillDocument)
class ETCBillDocumentAdmin(admin.ModelAdmin):
    pass


@admin.register(m.FuelCard)
class FuelCardAdmin(admin.ModelAdmin):
    pass


@admin.register(m.FuelCardChargeHistory)
class FuelCardChargeHistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(m.FuelBillHistory)
class FuelBillHistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(m.FuelBillDocument)
class FuelBillDocumentAdmin(admin.ModelAdmin):
    pass


@admin.register(m.BillDocument)
class BillDocumentAdmin(admin.ModelAdmin):
    pass
