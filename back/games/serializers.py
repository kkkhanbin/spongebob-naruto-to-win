from rest_framework import serializers

from .models import GameRecord


class GameHistorySerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(source='bet_amount', max_digits=12, decimal_places=2, read_only=True)
    date = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = GameRecord
        fields = ['id', 'game', 'result', 'amount', 'payout', 'date', 'details']


class RoulettePlaySerializer(serializers.Serializer):
    bet_type = serializers.ChoiceField(choices=['red', 'black', 'even', 'odd'])
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=1)


class LottoPlaySerializer(serializers.Serializer):
    numbers = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=49),
        min_length=6,
        max_length=6,
    )
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=1)

    def validate_numbers(self, value):
        if len(set(value)) != 6:
            raise serializers.ValidationError('Choose 6 unique numbers.')
        return sorted(value)
