from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import WalletView

router = DefaultRouter()

urlpatterns = [
    path('wallet/', WalletView.as_view(), name='wallet')
]
