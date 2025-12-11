from rest_framework import serializers
from .models import Wallet, Transaction, TopUpRequest

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ('balance',)

class TopUpRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopUpRequest
        fields = ('id', 'amount', 'screenshot', 'status', 'created_at')
        read_only_fields = ('id', 'status', 'created_at')

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
