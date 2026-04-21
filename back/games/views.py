from decimal import Decimal
import random

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from wallet.views import get_wallet_for_user

from .models import GameRecord
from .serializers import GameHistorySerializer, LottoPlaySerializer, RoulettePlaySerializer

RED_NUMBERS = {
    1, 3, 5, 7, 9, 12, 14, 16, 18,
    19, 21, 23, 25, 27, 30, 32, 34, 36,
}
LOTTO_PAYOUTS = {
    2: Decimal('1.50'),
    3: Decimal('3.00'),
    4: Decimal('10.00'),
    5: Decimal('50.00'),
    6: Decimal('200.00'),
}


class GameHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        records = GameRecord.objects.filter(user=request.user)
        return Response(GameHistorySerializer(records, many=True).data)


class RoulettePlayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RoulettePlaySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        wallet = get_wallet_for_user(request.user)
        amount = serializer.validated_data['amount']
        if wallet.balance < amount:
            return Response({'detail': 'Insufficient balance.'}, status=status.HTTP_400_BAD_REQUEST)

        result_number = random.randint(0, 36)
        bet_type = serializer.validated_data['bet_type']
        is_red = result_number in RED_NUMBERS
        is_black = result_number != 0 and not is_red
        is_even = result_number != 0 and result_number % 2 == 0
        is_odd = result_number % 2 == 1

        did_win = (
            (bet_type == 'red' and is_red)
            or (bet_type == 'black' and is_black)
            or (bet_type == 'even' and is_even)
            or (bet_type == 'odd' and is_odd)
        )
        payout = amount * Decimal('2.00') if did_win else Decimal('0')

        wallet.balance = wallet.balance - amount + payout
        wallet.save(update_fields=['balance', 'updated_at'])

        GameRecord.objects.create(
            user=request.user,
            game='roulette',
            bet_amount=amount,
            payout=payout,
            result='win' if did_win else 'lose',
            details={'bet_type': bet_type, 'rolled_number': result_number},
        )

        return Response(
            {
                'result': result_number,
                'win': did_win,
                'payout': payout,
                'balance': wallet.balance,
            },
            status=status.HTTP_200_OK,
        )


class LottoPlayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LottoPlaySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        wallet = get_wallet_for_user(request.user)
        amount = serializer.validated_data['amount']
        numbers = serializer.validated_data['numbers']
        if wallet.balance < amount:
            return Response({'detail': 'Insufficient balance.'}, status=status.HTTP_400_BAD_REQUEST)

        winning_numbers = sorted(random.sample(range(1, 50), 6))
        matches = len(set(numbers) & set(winning_numbers))
        multiplier = LOTTO_PAYOUTS.get(matches, Decimal('0'))
        payout = amount * multiplier if multiplier else Decimal('0')
        did_win = payout > 0

        wallet.balance = wallet.balance - amount + payout
        wallet.save(update_fields=['balance', 'updated_at'])

        GameRecord.objects.create(
            user=request.user,
            game='lotto',
            bet_amount=amount,
            payout=payout,
            result=f'{matches} matches',
            details={
                'selected_numbers': numbers,
                'winning_numbers': winning_numbers,
                'matches': matches,
            },
        )

        return Response(
            {
                'winning_numbers': winning_numbers,
                'matches': matches,
                'win': did_win,
                'payout': payout,
                'balance': wallet.balance,
            },
            status=status.HTTP_200_OK,
        )
