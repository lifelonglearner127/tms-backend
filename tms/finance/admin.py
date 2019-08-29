from django.contrib import admin

from . import models as m


@admin.register(m.ETCCard)
class ETCCardAdmin(admin.ModelAdmin):
    pass


@admin.register(m.ETCCardChargeHistory)
class ETCCardChargeHistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(m.FuelCard)
class FuelCardAdmin(admin.ModelAdmin):
    pass


@admin.register(m.OrderPayment)
class OrderPaymentAdmin(admin.ModelAdmin):
    pass


@admin.register(m.BillDocument)
class BillDocumentAdmin(admin.ModelAdmin):
    pass
