from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'full_name', 'address', 'fcm_token', 'is_active')
        read_only_fields = ('id', 'is_active')

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
