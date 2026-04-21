from django.urls import path

from .views import GameHistoryView, LottoPlayView, RoulettePlayView

urlpatterns = [
    path('history/', GameHistoryView.as_view(), name='game-history'),
    path('roulette/', RoulettePlayView.as_view(), name='roulette-play'),
    path('lotto/', LottoPlayView.as_view(), name='lotto-play'),
]
