from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User


class UserSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(
        source='wallet.balance',
        max_digits=18,
        decimal_places=2,
        read_only=True
    )
    bonus_balance = serializers.DecimalField(
        source='wallet.bonus_balance',
        max_digits=18,
        decimal_places=2,
        read_only=True
    )
    kyc_status = serializers.CharField(
        source='kyc.status',
        read_only=True
    )

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'is_verified',
            'is_banned',
            'balance',
            'bonus_balance',
            'kyc_status',
            'created_at'
        ]
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        return user

