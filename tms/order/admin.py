from django.contrib import admin

from . import models as m


@admin.register(m.Order)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(m.OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    pass


@admin.register(m.OrderProductDeliver)
class OrderProductDeliverAdmin(admin.ModelAdmin):
    pass
