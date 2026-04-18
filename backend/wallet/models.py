from django.db import models
from django.conf import settings


User = settings.AUTH_USER_MODEL


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')

    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    bonus_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    currency = models.CharField(max_length=10, default="USD")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
