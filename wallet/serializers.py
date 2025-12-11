from rest_framework import serializers
from .models import Wallet, Transaction, TopUpRequest

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ('balance',)

class TopUpRequestSerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(source='user.phone_number', read_only=True)

    class Meta:
        model = TopUpRequest
        fields = ('id', 'user_phone', 'amount', 'screenshot', 'status', 'created_at')
        read_only_fields = ('id', 'status', 'created_at')

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
