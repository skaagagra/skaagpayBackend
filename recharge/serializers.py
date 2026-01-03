from rest_framework import serializers
from .models import RechargeRequest, Operator

class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = ('id', 'name', 'category', 'is_default')



class RechargeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RechargeRequest
        fields = ('id', 'mobile_number', 'category', 'operator', 'amount', 'status', 'is_scheduled', 'scheduled_at', 'created_at')
        read_only_fields = ('id', 'status', 'created_at')

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value

from .models import Plan

class PlanSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.name', read_only=True)
    
    class Meta:
        model = Plan
        fields = '__all__'
