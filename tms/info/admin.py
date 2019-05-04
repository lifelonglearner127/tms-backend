from django.contrib import admin
from .models import (
    Product, LoadingStation, UnLoadingStation, QualityStation, OilStation
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(LoadingStation)
class LoadingStationAdmin(admin.ModelAdmin):
    pass


@admin.register(UnLoadingStation)
class UnLoadingStationAdmin(admin.ModelAdmin):
    pass


@admin.register(QualityStation)
class QualityStationAdmin(admin.ModelAdmin):
    pass


@admin.register(OilStation)
class OilStationAdmin(admin.ModelAdmin):
    pass
