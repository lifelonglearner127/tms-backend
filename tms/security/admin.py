from django.contrib import admin

from . import models as m


@admin.register(m.CompanyPolicy)
class CompanyPolicyAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Question)
class QuestionAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Test)
class TestAdmin(admin.ModelAdmin):
    pass


@admin.register(m.TestResult)
class TestResultAdmin(admin.ModelAdmin):
    pass


@admin.register(m.TestQuestionResult)
class TestQuestionResultAdmin(admin.ModelAdmin):
    pass


@admin.register(m.SecurityLibrary)
class SecurityLibraryAdmin(admin.ModelAdmin):
    pass
