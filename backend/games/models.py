from django.conf import settings
from django.db import models


User = settings.AUTH_USER_MODEL


class BlackjackSession(models.Model):
    GAME_TYPE = 'blackjack'

    STATUS_CHOICES = (
        ('player_turn', 'Player Turn'),
        ('dealer_turn', 'Dealer Turn'),
        ('finished', 'Finished'),
    )

    OUTCOME_CHOICES = (
        ('pending', 'Pending'),
        ('win', 'Win'),
        ('loss', 'Loss'),
        ('push', 'Push'),
        ('mixed', 'Mixed'),
        ('blackjack', 'Blackjack'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blackjack_sessions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='player_turn')
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES, default='pending')
    bet_amount = models.DecimalField(max_digits=18, decimal_places=2)
    total_wagered = models.DecimalField(max_digits=18, decimal_places=2)
    payout_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    net_result = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    player_hands = models.JSONField(default=list)
    dealer_cards = models.JSONField(default=list)
    deck = models.JSONField(default=list)
    current_hand_index = models.PositiveIntegerField(default=0)
    result_message = models.CharField(max_length=255, blank=True)
    client_seed = models.CharField(max_length=128, blank=True)
    server_seed = models.CharField(max_length=128)
    server_seed_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']


class Transaction(models.Model):
    KIND_CHOICES = (
        ('top_up', 'Top Up'),
        ('bet', 'Bet'),
        ('payout', 'Payout'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    session = models.ForeignKey(
        BlackjackSession,
        on_delete=models.SET_NULL,
        related_name='transactions',
        null=True,
        blank=True
    )
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    balance_after = models.DecimalField(max_digits=18, decimal_places=2)
    description = models.CharField(max_length=255)
    game_type = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
