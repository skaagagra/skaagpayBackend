from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.db import transaction as db_transaction
from django.shortcuts import get_object_or_404
from .models import RechargeRequest, Operator, Plan
from .serializers import RechargeRequestSerializer, OperatorSerializer, PlanSerializer
from authentication.models import User
from wallet.models import Wallet, Transaction

class UserParamsMixin:
    def get_user(self):
        user_id = self.request.headers.get('X-User-ID')
        if not user_id:
            return None
        return get_object_or_404(User, pk=user_id)

class RechargeListCreateView(generics.ListCreateAPIView, UserParamsMixin):
    serializer_class = RechargeRequestSerializer

    def get_queryset(self):
        user = self.get_user()
        if not user:
            return RechargeRequest.objects.none()
        return RechargeRequest.objects.filter(user=user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        user = self.get_user()
        if not user:
            return Response({'error': 'X-User-ID header required'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        amount = serializer.validated_data['amount']
        is_scheduled = serializer.validated_data.get('is_scheduled', False)
        scheduled_at = serializer.validated_data.get('scheduled_at')
        category = serializer.validated_data.get('category', 'MOBILE_PREPAID')
        
        # Calculate Platform Fee (3% for Postpaid, GAS, DTH) - Prepaid is FREE
        platform_fee = 0
        if category in ['MOBILE_POSTPAID', 'GAS', 'DTH']:
            try:
                platform_fee = float(amount) * 0.03
            except:
                platform_fee = 0
            
        total_deduction = float(amount) + platform_fee
        
        # If Scheduled, just save and return. DEDUCTION HAPPENS LATER (Need to handle fee there too, but out of scope for now)
        if is_scheduled:
             serializer.save(user=user, status='SCHEDULED', platform_fee=platform_fee, total_amount=total_deduction)
             return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Check Wallet Balance
        with db_transaction.atomic():
            wallet, created = Wallet.objects.get_or_create(user=user)
            if wallet.balance < total_deduction:
                return Response({'error': f'Insufficient wallet balance. Required: {total_deduction}'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Deduct Balance
            wallet.balance = float(wallet.balance) - float(total_deduction)
            wallet.save()
            
            # Create Recharge Request
            instance = serializer.save(user=user, platform_fee=platform_fee, total_amount=total_deduction)
            
            # Get Operator Logo if available
            op_logo = None
            op_name = instance.operator
            try:
                op_obj = Operator.objects.filter(name=instance.operator, category=instance.category).first()
                if op_obj:
                    op_logo = op_obj.logo_url
            except:
                pass

            # Log Transaction
            Transaction.objects.create(
                wallet=wallet,
                amount=total_deduction,
                transaction_type='DEBIT',
                description=f"Recharge for {instance.mobile_number}",
                status='PENDING',
                operator_name=op_name,
                operator_logo=op_logo,
                recharge_request=instance
            )
            
            # Notify Admin
            from common.notifications import send_admin_notification
            send_admin_notification(
                title="New Recharge Request",
                body=f"Recharge {instance.amount} (+{platform_fee} fee) for {instance.mobile_number}"
            )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OperatorListView(generics.ListAPIView):
    serializer_class = OperatorSerializer
    permission_classes = [permissions.AllowAny] # Or IsAuthenticated depending on need, sticking to open for now as other views imply loose auth

    def get_queryset(self):
        category = self.request.query_params.get('category')
        if category:
            return Operator.objects.filter(category=category)
        return Operator.objects.all()

class PlanListCreateView(generics.ListCreateAPIView):
    """
    Public List (or Auth User List) & Admin Create.
    For simplicity, allowing open list but restrictive create could be done via permissions.
    """
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny] # Ideally IsAdmin for Create, AllowAny for List

    def get_queryset(self):
        queryset = Plan.objects.select_related('operator').all()
        operator_id = self.request.query_params.get('operator_id')
        circle = self.request.query_params.get('circle')
        plan_type = self.request.query_params.get('plan_type')

        if operator_id:
            queryset = queryset.filter(operator_id=operator_id)
        if circle:
            queryset = queryset.filter(circle=circle)
        if plan_type:
            queryset = queryset.filter(plan_type=plan_type)
            
        return queryset

class PlanRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Admin Only: Update/Delete Plan
    """
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny] # RESTRICT THIS IN PRODUCTION to Admin Only
