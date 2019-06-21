from django.contrib import admin

from . import models as m


@admin.register(m.Route)
class RouteAdmin(admin.ModelAdmin):
    pass
