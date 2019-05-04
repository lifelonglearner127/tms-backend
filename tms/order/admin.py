from django.contrib import admin
from .models import Order, OrderProduct, OrderProductDeliver


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    pass


@admin.register(OrderProductDeliver)
class OrderProductDeliverAdmin(admin.ModelAdmin):
    pass
