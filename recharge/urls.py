from django.urls import path
from .views import RechargeListCreateView

urlpatterns = [
    path('request/', RechargeListCreateView.as_view(), name='recharge-request'),
]
