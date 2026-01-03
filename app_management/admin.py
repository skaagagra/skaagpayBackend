from django.contrib import admin
from .models import AppVersion

@admin.register(AppVersion)
class AppVersionAdmin(admin.ModelAdmin):
    list_display = ('version_name', 'version_code', 'created_at')
    list_filter = ('version_code', 'created_at')
    search_fields = ('version_name',)