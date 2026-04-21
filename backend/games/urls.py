from django.urls import path

from games.views import (
    BlackjackActionView,
    BlackjackSessionListView,
    CurrentBlackjackSessionView,
    StartBlackjackView,
    TransactionListView,
)

urlpatterns = [
    path('transactions/', TransactionListView.as_view(), name='transactions'),
    path('blackjack/current/', CurrentBlackjackSessionView.as_view(), name='blackjack-current'),
    path('blackjack/start/', StartBlackjackView.as_view(), name='blackjack-start'),
    path('blackjack/action/', BlackjackActionView.as_view(), name='blackjack-action'),
    path('blackjack/history/', BlackjackSessionListView.as_view(), name='blackjack-history'),
]
