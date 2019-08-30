from django.contrib import admin

from . import models as m


@admin.register(m.ETCCard)
class ETCCardAdmin(admin.ModelAdmin):
    pass


@admin.register(m.ETCCardChargeHistory)
class ETCCardChargeHistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(m.ETCCardUsageHistory)
class ETCCardUsageHistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(m.ETCCardUsageDocument)
class ETCCardUsageDocumentAdmin(admin.ModelAdmin):
    pass


@admin.register(m.FuelCard)
class FuelCardAdmin(admin.ModelAdmin):
    pass


@admin.register(m.FuelCardChargeHistory)
class FuelCardChargeHistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(m.FuelCardUsageHistory)
class FuelCardUsageHistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(m.FuelCardUsageDocument)
class FuelCardUsageDocumentAdmin(admin.ModelAdmin):
    pass


@admin.register(m.OrderPayment)
class OrderPaymentAdmin(admin.ModelAdmin):
    pass


@admin.register(m.BillDocument)
class BillDocumentAdmin(admin.ModelAdmin):
    pass
