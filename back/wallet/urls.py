from django.urls import path

from .views import WalletDepositView, WalletView

urlpatterns = [
    path('', WalletView.as_view(), name='wallet'),
    path('deposit/', WalletDepositView.as_view(), name='wallet-deposit'),
]
