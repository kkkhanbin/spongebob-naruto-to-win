from django.conf import settings
from django.db import models


class GameRecord(models.Model):
    GAME_CHOICES = [
        ('roulette', 'Roulette'),
        ('lotto', 'Lotto'),
        ('blackjack', 'Blackjack'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='game_records',
    )
    game = models.CharField(max_length=20, choices=GAME_CHOICES)
    bet_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payout = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    result = models.CharField(max_length=100)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.game} - {self.result}'
