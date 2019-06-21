from django.contrib import admin
from . import models as m


@admin.register(m.RestRequest)
class RestRequestAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Department)
class DepartmentAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Position)
class PositionAdmin(admin.ModelAdmin):
    pass


@admin.register(m.RoleManagement)
class RoleManagementAdmin(admin.ModelAdmin):
    pass


@admin.register(m.StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    pass
