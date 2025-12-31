from django.urls import path
from .views import RechargeListCreateView, OperatorListView

urlpatterns = [
    path('request/', RechargeListCreateView.as_view(), name='recharge-request'),
    path('operators/', OperatorListView.as_view(), name='operator-list'),
]
