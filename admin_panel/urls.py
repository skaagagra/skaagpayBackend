from django.urls import path
from .views import (
    AdminLoginView, 
    AdminDashboardView, 
    AdminTopUpListView, 
    AdminTopUpActionView,
    AdminRechargeListView,
    AdminRechargeUpdateView,
    AdminUserListView,
    AdminUserUpdateView
)

urlpatterns = [
    path('login/', AdminLoginView.as_view(), name='admin-login'),
    path('dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    
    path('topups/', AdminTopUpListView.as_view(), name='admin-topups'),
    path('topups/<int:pk>/action/', AdminTopUpActionView.as_view(), name='admin-topup-action'),
    
    path('recharges/', AdminRechargeListView.as_view(), name='admin-recharges'),
    path('recharges/<int:pk>/', AdminRechargeUpdateView.as_view(), name='admin-recharge-update'),
    
    path('users/', AdminUserListView.as_view(), name='admin-users'),
    path('users/<int:pk>/', AdminUserUpdateView.as_view(), name='admin-user-update'),
]
