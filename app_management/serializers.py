from rest_framework import serializers
from .models import AppVersion

class AppVersionSerializer(serializers.ModelSerializer):
    apk_url = serializers.SerializerMethodField()

    class Meta:
        model = AppVersion
        fields = ['id', 'version_name', 'version_code', 'apk_file', 'apk_url', 'release_notes', 'is_force_update', 'created_at']
        read_only_fields = ['created_at']

    def get_apk_url(self, obj):
        request = self.context.get('request')
        if obj.apk_file and request:
            return request.build_absolute_uri(obj.apk_file.url)
        return obj.apk_file.url if obj.apk_file else None
