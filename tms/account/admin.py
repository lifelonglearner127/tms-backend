from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from . import models as m


class UserCreationForm(forms.ModelForm):

    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput
    )

    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput
    )

    class Meta:
        model = m.User
        fields = (
            'username',
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = m.User
        fields = '__all__'

    def clean_password(self):
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('username', 'name', 'mobile', 'role')
    list_filter = ('role',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('name', 'mobile',)}),
        ('Permissions', {'fields': ('role',)}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('username', 'password1', 'password2')
            }
        ),
    )
    search_fields = ('username',)
    ordering = ('username',)
    filter_horizontal = ()


@admin.register(m.CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(m.StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(m.DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(m.EscortProfile)
class EscortProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(m.StaffDocument)
class StaffDocumentAdmin(admin.ModelAdmin):
    pass


admin.site.register(m.User, UserAdmin)
admin.site.unregister(Group)
