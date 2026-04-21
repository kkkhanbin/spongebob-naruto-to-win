from django.urls import path

from .views import WalletView, WalletTopUpView

urlpatterns = [
    path('wallet/', WalletView.as_view(), name='wallet'),
    path('wallet/top-up/', WalletTopUpView.as_view(), name='wallet-top-up'),
]
