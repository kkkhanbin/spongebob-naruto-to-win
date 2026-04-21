from rest_framework import serializers

from games.models import BlackjackSession, Transaction
from games.services import available_actions, hand_value


class TransactionSerializer(serializers.ModelSerializer):
    signed_amount = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id',
            'kind',
            'amount',
            'signed_amount',
            'balance_after',
            'description',
            'game_type',
            'created_at'
        ]

    def get_signed_amount(self, obj):
        return f'{obj.amount:.2f}'


class BlackjackStartSerializer(serializers.Serializer):
    bet_amount = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=1)
    client_seed = serializers.CharField(max_length=128, required=False, allow_blank=True)


class BlackjackActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['hit', 'stand', 'double', 'split'])


class BlackjackSessionSerializer(serializers.ModelSerializer):
    available_actions = serializers.SerializerMethodField()
    dealer_total = serializers.SerializerMethodField()
    dealer_cards = serializers.SerializerMethodField()
    show_server_seed = serializers.SerializerMethodField()
    game_type = serializers.SerializerMethodField()

    class Meta:
        model = BlackjackSession
        fields = [
            'id',
            'game_type',
            'status',
            'outcome',
            'bet_amount',
            'total_wagered',
            'payout_amount',
            'net_result',
            'player_hands',
            'dealer_cards',
            'dealer_total',
            'current_hand_index',
            'result_message',
            'client_seed',
            'server_seed_hash',
            'show_server_seed',
            'created_at',
            'updated_at',
            'finished_at',
            'available_actions'
        ]

    def get_available_actions(self, obj):
        return available_actions(obj)

    def get_dealer_total(self, obj):
        if obj.status != 'finished' and len(obj.dealer_cards) > 1:
            return hand_value([obj.dealer_cards[0]])[0]
        return hand_value(obj.dealer_cards)[0]

    def get_dealer_cards(self, obj):
        if obj.status != 'finished' and len(obj.dealer_cards) > 1:
            return [obj.dealer_cards[0], 'XX']
        return obj.dealer_cards

    def get_show_server_seed(self, obj):
        return obj.server_seed if obj.status == 'finished' else None

    def get_game_type(self, obj):
        return BlackjackSession.GAME_TYPE
