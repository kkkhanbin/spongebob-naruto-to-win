from django.contrib import admin

from games.models import BlackjackSession, Transaction


@admin.register(BlackjackSession)
class BlackjackSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'outcome', 'bet_amount', 'payout_amount', 'created_at')
    list_filter = ('status', 'outcome')
    search_fields = ('user__username', 'user__email')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'kind', 'amount', 'balance_after', 'created_at')
    list_filter = ('kind', 'game_type')
    search_fields = ('user__username', 'description')
