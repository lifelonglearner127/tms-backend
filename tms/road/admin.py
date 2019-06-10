from django.contrib import admin

from . import models as m


@admin.register(m.Point)
class PointAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Route)
class RouteAdmin(admin.ModelAdmin):
    pass
