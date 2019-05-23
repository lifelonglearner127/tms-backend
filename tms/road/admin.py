from django.contrib import admin

from . import models as m


@admin.register(m.Point)
class PointAdmin(admin.ModelAdmin):
    pass


@admin.register(m.BlackPoint)
class BlackPointAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Path)
class PathAdmin(admin.ModelAdmin):
    pass
