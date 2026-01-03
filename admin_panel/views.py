from rest_framework import generics, status, views
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count
from django.utils import timezone
from authentication.models import User
from wallet.models import TopUpRequest, Wallet
from recharge.models import RechargeRequest
from wallet.serializers import TopUpRequestSerializer, WalletSerializer
from recharge.serializers import RechargeRequestSerializer

# --- Helper Mixin ---
class AdminUserMixin:
    """
    Ensures the user making the request is an Admin.
    """
    def get_admin_user(self):
        user_id = self.request.headers.get('X-User-ID')
        if not user_id:
            return None
        try:
            user = User.objects.get(pk=user_id)
            if user.is_active and (user.is_admin or user.is_superuser):
                return user
        except User.DoesNotExist:
            pass
        return None

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


# --- Views ---

class AdminLoginView(views.APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        fcm_token = request.data.get('fcm_token')

        full_name = request.data.get('full_name')

        if not phone_number or not password:
            return Response({'error': 'Please provide phone number and password'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(phone_number=phone_number)
            if user.check_password(password):
                if user.is_admin or user.is_superuser:
                    # Update FCM Token if provided
                    if fcm_token:
                        user.fcm_token = fcm_token
                        user.save()
                        
                    return Response({
                        'message': 'Login Successful',
                        'user_id': user.id,
                        'full_name': user.full_name,
                        'is_admin': user.is_admin
                    })
                else:
                    return Response({'error': 'Access Denied. Admins only.'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class AdminDashboardView(views.APIView, AdminUserMixin):
    def get(self, request):
        if not self.get_admin_user():
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        total_users = User.objects.count()
        pending_topups = TopUpRequest.objects.filter(status='PENDING').count()
        
        today = timezone.now().date()
        todays_recharges_count = RechargeRequest.objects.filter(created_at__date=today).count()
        todays_recharges_sum = RechargeRequest.objects.filter(created_at__date=today).aggregate(Sum('amount'))['amount__sum'] or 0

        return Response({
            'total_users': total_users,
            'pending_topups': pending_topups,
            'todays_recharges_count': todays_recharges_count,
            'todays_recharges_sum': todays_recharges_sum,
        })


class AdminTopUpListView(generics.ListAPIView, AdminUserMixin):
    serializer_class = TopUpRequestSerializer

    def get_queryset(self):
        return TopUpRequest.objects.all().order_by('-created_at')

    def list(self, request, *args, **kwargs):
        if not self.get_admin_user():
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        status_filter = request.query_params.get('status')
        queryset = self.get_queryset()
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AdminTopUpActionView(views.APIView, AdminUserMixin):
    def post(self, request, pk):
        if not self.get_admin_user():
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        topup = get_object_or_404(TopUpRequest, pk=pk)
        action = request.data.get('action') 

        if topup.status != 'PENDING':
             return Response({'error': f'Request already {topup.status}'}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'APPROVE':
            from django.db import transaction
            with transaction.atomic():
                topup.status = 'APPROVED'
                topup.admin_note = request.data.get('note', 'Approved by Admin')
                topup.save()

                wallet, _ = Wallet.objects.get_or_create(user=topup.user)
                wallet.balance += topup.amount
                wallet.save()

                from wallet.models import Transaction
                Transaction.objects.create(
                    wallet=wallet,
                    amount=topup.amount,
                    transaction_type='CREDIT',
                    description=f"TopUp Approved: {topup.id}"
                )

            return Response({'message': 'TopUp Approved'})
        
        elif action == 'REJECT':
             topup.status = 'REJECTED'
             topup.admin_note = request.data.get('note', 'Rejected by Admin')
             topup.save()
             return Response({'message': 'TopUp Rejected'})
        
        else:
             return Response({'error': 'Invalid Action'}, status=status.HTTP_400_BAD_REQUEST)


class AdminRechargeListView(generics.ListAPIView, AdminUserMixin):
    serializer_class = RechargeRequestSerializer

    def get_queryset(self):
        queryset = RechargeRequest.objects.all().order_by('-created_at')
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param.upper())
        return queryset

    def list(self, request, *args, **kwargs):
        if not self.get_admin_user():
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().list(request, *args, **kwargs)

class AdminRechargeUpdateView(views.APIView, AdminUserMixin):
    def patch(self, request, pk):
        if not self.get_admin_user():
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        recharge = get_object_or_404(RechargeRequest, pk=pk)
        new_status = request.data.get('status')
        
        if new_status not in ['PENDING', 'PROCESSING', 'SUCCESS', 'FAILED', 'SCHEDULED']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
            
        recharge.status = new_status
        recharge.save()
        return Response({'message': 'Recharge status updated'})

# --- User Management Views ---

from rest_framework import serializers
class UserListSerializer(serializers.ModelSerializer):
    wallet_balance = serializers.DecimalField(source='wallet.balance', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'full_name', 'is_active', 'is_admin', 'created_at', 'wallet_balance')

class AdminUserListView(generics.ListAPIView, AdminUserMixin):
    serializer_class = UserListSerializer

    def get_queryset(self):
        return User.objects.all().select_related('wallet').order_by('-created_at')

    def list(self, request, *args, **kwargs):
        if not self.get_admin_user():
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().list(request, *args, **kwargs)

class AdminUserUpdateView(views.APIView, AdminUserMixin):
    def patch(self, request, pk):
        if not self.get_admin_user():
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user = get_object_or_404(User, pk=pk)
        
        # Prevent self-deactivation/lockout if simplistic
        # if user.pk == self.get_admin_user().pk:
        #    return Response({'error': 'Cannot modify your own account'}, status=status.HTTP_400_BAD_REQUEST)

        if 'is_active' in request.data:
            user.is_active = request.data['is_active']
        
        user.save()
        return Response({'message': 'User updated successfully'})
