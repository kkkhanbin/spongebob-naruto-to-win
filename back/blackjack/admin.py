from django.contrib import admin

from .models import ActionLog, BetTransaction, GameSession, Hand


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'initial_bet', 'created_at', 'settled_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)


@admin.register(Hand)
class HandAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'hand_index', 'wager', 'outcome', 'is_finished')
    list_filter = ('outcome', 'is_finished', 'is_split_hand', 'is_doubled')


@admin.register(BetTransaction)
class BetTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'hand', 'transaction_type', 'amount', 'created_at')
    list_filter = ('transaction_type',)


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'hand', 'action', 'created_at')
    list_filter = ('action',)
