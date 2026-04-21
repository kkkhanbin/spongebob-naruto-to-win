from rest_framework import serializers
from .models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['balance', 'bonus_balance', 'currency']
        read_only_fields = fields


class WalletTopUpSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=18,
        decimal_places=2,
        min_value=1,
        required=False,
        default='1000.00'
    )
