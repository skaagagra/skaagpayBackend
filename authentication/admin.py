from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    list_display = ('phone_number', 'full_name', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'full_name', 'password'),
        }),
    )
    search_fields = ('phone_number', 'full_name')
    ordering = ('phone_number',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)
