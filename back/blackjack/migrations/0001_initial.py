from decimal import Decimal

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GameSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('player_turn', 'Player Turn'), ('dealer_turn', 'Dealer Turn'), ('completed', 'Completed')], default='player_turn', max_length=20)),
                ('deck_state', models.JSONField(blank=True, default=list)),
                ('dealer_cards', models.JSONField(blank=True, default=list)),
                ('dealer_hidden_revealed', models.BooleanField(default=False)),
                ('current_hand_index', models.PositiveIntegerField(default=0)),
                ('initial_bet', models.DecimalField(decimal_places=2, max_digits=12)),
                ('blackjack_payout_multiplier', models.DecimalField(decimal_places=2, default=Decimal('1.50'), max_digits=6)),
                ('balance_before', models.DecimalField(decimal_places=2, max_digits=12)),
                ('balance_after', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('action_nonce', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('settled_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blackjack_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Hand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hand_index', models.PositiveIntegerField()),
                ('cards', models.JSONField(blank=True, default=list)),
                ('wager', models.DecimalField(decimal_places=2, max_digits=12)),
                ('is_split_hand', models.BooleanField(default=False)),
                ('is_doubled', models.BooleanField(default=False)),
                ('has_stood', models.BooleanField(default=False)),
                ('is_finished', models.BooleanField(default=False)),
                ('outcome', models.CharField(choices=[('pending', 'Pending'), ('blackjack', 'Blackjack'), ('win', 'Win'), ('lose', 'Lose'), ('push', 'Push'), ('bust', 'Bust')], default='pending', max_length=20)),
                ('payout', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hands', to='blackjack.gamesession')),
            ],
            options={
                'ordering': ['hand_index'],
                'unique_together': {('session', 'hand_index')},
            },
        ),
        migrations.CreateModel(
            name='BetTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('bet', 'Bet'), ('double', 'Double'), ('split', 'Split'), ('payout', 'Payout'), ('refund', 'Refund')], max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('note', models.CharField(blank=True, max_length=120)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('hand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bet_transactions', to='blackjack.hand')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bet_transactions', to='blackjack.gamesession')),
            ],
            options={
                'ordering': ['created_at', 'id'],
            },
        ),
        migrations.CreateModel(
            name='ActionLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('start', 'Start'), ('hit', 'Hit'), ('stand', 'Stand'), ('double', 'Double'), ('split', 'Split'), ('dealer_play', 'Dealer Play'), ('settle', 'Settle')], max_length=20)),
                ('payload', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('hand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='action_logs', to='blackjack.hand')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='action_logs', to='blackjack.gamesession')),
            ],
            options={
                'ordering': ['created_at', 'id'],
            },
        ),
    ]
