from rest_framework import serializers


class StartBlackjackSerializer(serializers.Serializer):
    bet = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=1)


class SessionActionSerializer(serializers.Serializer):
    action_nonce = serializers.IntegerField(min_value=0)


class BlackjackHandStateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    hand_index = serializers.IntegerField()
    cards = serializers.ListField(child=serializers.DictField())
    wager = serializers.DecimalField(max_digits=12, decimal_places=2)
    total = serializers.IntegerField()
    is_soft = serializers.BooleanField()
    is_active = serializers.BooleanField()
    is_finished = serializers.BooleanField()
    is_doubled = serializers.BooleanField()
    is_split_hand = serializers.BooleanField()
    can_hit = serializers.BooleanField()
    can_stand = serializers.BooleanField()
    can_double = serializers.BooleanField()
    can_split = serializers.BooleanField()
    outcome = serializers.CharField()
    payout = serializers.DecimalField(max_digits=12, decimal_places=2)


class BlackjackStateSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    status = serializers.CharField()
    balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    balance_before = serializers.DecimalField(max_digits=12, decimal_places=2)
    balance_after = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True)
    current_hand_index = serializers.IntegerField()
    dealer_hidden_revealed = serializers.BooleanField()
    dealer_cards = serializers.ListField(child=serializers.DictField())
    dealer_total = serializers.IntegerField(allow_null=True)
    hands = BlackjackHandStateSerializer(many=True)
    available_actions = serializers.ListField(child=serializers.CharField())
    message = serializers.CharField()
    action_nonce = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
