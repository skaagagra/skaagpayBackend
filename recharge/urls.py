from django.urls import path
from .views import RechargeListCreateView, OperatorListView, PlanListCreateView, PlanRetrieveUpdateDestroyView

urlpatterns = [
    path('request/', RechargeListCreateView.as_view(), name='recharge-request'),
    path('operators/', OperatorListView.as_view(), name='operator-list'),
    path('plans/', PlanListCreateView.as_view(), name='plan-list-create'),
    path('plans/<int:pk>/', PlanRetrieveUpdateDestroyView.as_view(), name='plan-detail'),
]
