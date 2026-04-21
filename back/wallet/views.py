from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Wallet
from .serializers import WalletDepositSerializer, WalletSerializer


def get_wallet_for_user(user):
    wallet, _ = Wallet.objects.get_or_create(user=user)
    return wallet


class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet = get_wallet_for_user(request.user)
        return Response(WalletSerializer(wallet).data)


class WalletDepositView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WalletDepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        wallet = get_wallet_for_user(request.user)
        wallet.balance += serializer.validated_data['amount']
        wallet.save(update_fields=['balance', 'updated_at'])

        return Response(WalletSerializer(wallet).data, status=status.HTTP_200_OK)
