from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Wallet, TopUpRequest, Transaction
from .serializers import WalletSerializer, TopUpRequestSerializer, TransactionSerializer, TransferSerializer

# Since we don't have proper Token Auth implemented for this MVP, we will simulate user Context
# In a real app, `permission_classes = [permissions.IsAuthenticated]` would be used
# and user would be `request.user`.
# For now, we will accept `user_id` in the query params or body for demonstration if Auth isn't strictly enforced yet,
# OR we can assume I should add basic code to get user from request if I used a real auth method.
# Given "login with phone" was simple, I'll rely on passing `user_id` header or similar for now to keep it testable 
# without complex Headers/Tokens in the limited browser/tool interaction, BUT 
# allow me to try to write it "Correctly" assuming `request.user` will be populated by some middleware or 
# I will make a custom mixin to fetch user from a header `X-User-ID` for this MVP.

from authentication.models import User

class UserParamsMixin:
    def get_user(self):
        # MVP: Get User ID from Header 'X-User-ID'
        user_id = self.request.headers.get('X-User-ID')
        if not user_id:
            return None
        return get_object_or_404(User, pk=user_id)

class WalletBalanceView(APIView, UserParamsMixin):
    def get(self, request):
        user = self.get_user()
        if not user:
            return Response({'error': 'X-User-ID header required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        wallet, created = Wallet.objects.get_or_create(user=user)
        return Response(WalletSerializer(wallet).data)

class TopUpRequestListCreateView(generics.ListCreateAPIView, UserParamsMixin):
    serializer_class = TopUpRequestSerializer
    
    def get_queryset(self):
        user = self.get_user()
        if not user:
             return TopUpRequest.objects.none()
        return TopUpRequest.objects.filter(user=user).order_by('-created_at')

    def perform_create(self, serializer):
        user = self.get_user()
        if not user:
            raise serializers.ValidationError("User not found or unauthenticated")
        instance = serializer.save(user=user)
        
        # Notify Admin
        from common.notifications import send_admin_notification
        send_admin_notification(
            title="New Top-Up Request",
            body=f"User {user.phone_number} requested {instance.amount}"
        )

class TransactionListView(generics.ListAPIView, UserParamsMixin):
    serializer_class = TransactionSerializer
    
    def get_queryset(self):
        user = self.get_user()
        if not user:
             return Transaction.objects.none()
        # Ensure wallet exists
        if not hasattr(user, 'wallet'):
            return Transaction.objects.none()
        return Transaction.objects.filter(wallet=user.wallet).order_by('-created_at')

from django.db import transaction

class WalletTransferView(APIView, UserParamsMixin):
    def post(self, request):
        user = self.get_user()
        if not user:
            return Response({'error': 'X-User-ID header required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = TransferSerializer(data=request.data)
        if serializer.is_valid():
            recipient_id = serializer.validated_data['recipient_id']
            amount = serializer.validated_data['amount']
            description = serializer.validated_data.get('description', '')

            # 1. Validate Amount
            if amount <= 0:
                return Response({'error': 'Amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)

            # 2. Get Recipient
            try:
                recipient = User.objects.get(custom_user_id=recipient_id)
            except User.DoesNotExist:
                return Response({'error': 'Recipient ID not found'}, status=status.HTTP_404_NOT_FOUND)

            if recipient.id == user.id:
                return Response({'error': 'Cannot transfer to self'}, status=status.HTTP_400_BAD_REQUEST)

            # 3. Perform Transfer Atomically
            try:
                with transaction.atomic():
                    # Refresh sender wallet for safety
                    sender_wallet, _ = Wallet.objects.get_or_create(user=user)
                    
                    if sender_wallet.balance < amount:
                        return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    recipient_wallet, _ = Wallet.objects.get_or_create(user=recipient)

                    # Update Balances
                    sender_wallet.balance -= amount
                    sender_wallet.save()

                    recipient_wallet.balance += amount
                    recipient_wallet.save()

                    # Create Transactions
                    Transaction.objects.create(
                        wallet=sender_wallet,
                        amount=amount,
                        transaction_type='TRANSFER_SENT',
                        description=f"Transfer to {recipient.full_name} ({recipient_id}). {description}"
                    )
                    Transaction.objects.create(
                        wallet=recipient_wallet,
                        amount=amount,
                        transaction_type='TRANSFER_RECEIVED',
                        description=f"Received from {user.full_name} ({user.custom_user_id}). {description}"
                    )

                return Response({
                    'message': 'Transfer successful',
                    'new_balance': sender_wallet.balance
                }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
