from django.urls import path

from .views import (
    BlackjackDoubleView,
    BlackjackHitView,
    BlackjackSplitView,
    BlackjackStandView,
    BlackjackStartView,
    BlackjackStateView,
)

urlpatterns = [
    path('start/', BlackjackStartView.as_view(), name='blackjack-start'),
    path('hit/', BlackjackHitView.as_view(), name='blackjack-hit'),
    path('stand/', BlackjackStandView.as_view(), name='blackjack-stand'),
    path('double/', BlackjackDoubleView.as_view(), name='blackjack-double'),
    path('split/', BlackjackSplitView.as_view(), name='blackjack-split'),
    path('state/', BlackjackStateView.as_view(), name='blackjack-state'),
]
