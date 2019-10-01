from django.contrib import admin

from . import models as m


@admin.register(m.BasicSetting)
class BasicSettingAdmin(admin.ModelAdmin):
    pass


# @admin.register(m.ProductCategory)
# class ProductCategoryAdmin(admin.ModelAdmin):
#     pass


@admin.register(m.Product)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Station)
class StationAdmin(admin.ModelAdmin):
    pass
