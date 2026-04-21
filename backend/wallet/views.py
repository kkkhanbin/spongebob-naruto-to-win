from decimal import Decimal

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from wallet.serializers import WalletSerializer
from wallet.serializers import WalletTopUpSerializer
from games.services import credit_wallet


class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet = request.user.wallet
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)


class WalletTopUpView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WalletTopUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data.get('amount', Decimal('1000.00'))
        if amount <= 0:
            raise ValidationError('Top-up amount must be positive.')

        wallet = credit_wallet(
            user=request.user,
            amount=amount,
            kind='top_up',
            description='Wallet top-up'
        )

        return Response(WalletSerializer(wallet).data, status=status.HTTP_200_OK)
