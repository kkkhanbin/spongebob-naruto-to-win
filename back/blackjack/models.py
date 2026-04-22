from decimal import Decimal

from django.conf import settings
from django.db import models


class GameSession(models.Model):
    STATUS_CHOICES = [
        ('player_turn', 'Player Turn'),
        ('dealer_turn', 'Dealer Turn'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blackjack_sessions',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='player_turn')
    deck_state = models.JSONField(default=list, blank=True)
    dealer_cards = models.JSONField(default=list, blank=True)
    dealer_hidden_revealed = models.BooleanField(default=False)
    current_hand_index = models.PositiveIntegerField(default=0)
    initial_bet = models.DecimalField(max_digits=12, decimal_places=2)
    blackjack_payout_multiplier = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('1.50'),
    )
    balance_before = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    action_nonce = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    settled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Blackjack #{self.pk} - {self.user.username} - {self.status}'


class Hand(models.Model):
    OUTCOME_CHOICES = [
        ('pending', 'Pending'),
        ('blackjack', 'Blackjack'),
        ('win', 'Win'),
        ('lose', 'Lose'),
        ('push', 'Push'),
        ('bust', 'Bust'),
    ]

    session = models.ForeignKey(
        GameSession,
        on_delete=models.CASCADE,
        related_name='hands',
    )
    hand_index = models.PositiveIntegerField()
    cards = models.JSONField(default=list, blank=True)
    wager = models.DecimalField(max_digits=12, decimal_places=2)
    is_split_hand = models.BooleanField(default=False)
    is_doubled = models.BooleanField(default=False)
    has_stood = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES, default='pending')
    payout = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['hand_index']
        unique_together = ('session', 'hand_index')

    def __str__(self):
        return f'Session {self.session_id} hand {self.hand_index}'


class BetTransaction(models.Model):
    TRANSACTION_CHOICES = [
        ('bet', 'Bet'),
        ('double', 'Double'),
        ('split', 'Split'),
        ('payout', 'Payout'),
        ('refund', 'Refund'),
    ]

    session = models.ForeignKey(
        GameSession,
        on_delete=models.CASCADE,
        related_name='bet_transactions',
    )
    hand = models.ForeignKey(
        Hand,
        on_delete=models.CASCADE,
        related_name='bet_transactions',
        null=True,
        blank=True,
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'id']


class ActionLog(models.Model):
    ACTION_CHOICES = [
        ('start', 'Start'),
        ('hit', 'Hit'),
        ('stand', 'Stand'),
        ('double', 'Double'),
        ('split', 'Split'),
        ('dealer_play', 'Dealer Play'),
        ('settle', 'Settle'),
    ]

    session = models.ForeignKey(
        GameSession,
        on_delete=models.CASCADE,
        related_name='action_logs',
    )
    hand = models.ForeignKey(
        Hand,
        on_delete=models.CASCADE,
        related_name='action_logs',
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'id']
