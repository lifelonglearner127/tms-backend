from django.contrib import admin

from . import models as m


@admin.register(m.Product)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(m.LoadingStation)
class LoadingStationAdmin(admin.ModelAdmin):
    pass


@admin.register(m.UnLoadingStation)
class UnLoadingStationAdmin(admin.ModelAdmin):
    pass


@admin.register(m.QualityStation)
class QualityStationAdmin(admin.ModelAdmin):
    pass


@admin.register(m.OilStation)
class OilStationAdmin(admin.ModelAdmin):
    pass
