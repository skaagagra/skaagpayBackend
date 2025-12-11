from rest_framework import serializers
from .models import RechargeRequest

class RechargeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RechargeRequest
        fields = ('id', 'mobile_number', 'operator', 'amount', 'status', 'is_scheduled', 'scheduled_at', 'created_at')
        read_only_fields = ('id', 'status', 'created_at')

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value
