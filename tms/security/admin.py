from django.contrib import admin

from . import models as m


@admin.register(m.CompanyPolicy)
class CompanyPolicyAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Question)
class QuestionAdmin(admin.ModelAdmin):
    pass


# @admin.register(m.SecurityKnowledge)
# class SecurityKnowledgeAdmin(admin.ModelAdmin):
#     pass
