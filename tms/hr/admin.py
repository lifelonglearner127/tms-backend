from django.contrib import admin
from . import models as m


@admin.register(m.RestRequest)
class RestRequestAdmin(admin.ModelAdmin):
    pass
