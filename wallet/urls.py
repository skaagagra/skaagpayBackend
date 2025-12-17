from django.urls import path
from .views import WalletBalanceView, TopUpRequestListCreateView, TransactionListView, WalletTransferView

urlpatterns = [
    path('balance/', WalletBalanceView.as_view(), name='wallet-balance'),
    path('topup/', TopUpRequestListCreateView.as_view(), name='wallet-topup'),
    path('transactions/', TransactionListView.as_view(), name='wallet-transactions'),
    path('transfer/', WalletTransferView.as_view(), name='wallet-transfer'),
]
