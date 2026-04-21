from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from games.models import BlackjackSession, Transaction
from games.serializers import (
    BlackjackActionSerializer,
    BlackjackSessionSerializer,
    BlackjackStartSerializer,
    TransactionSerializer,
)
from games.services import apply_blackjack_action, start_blackjack_session


class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)[:20]


class BlackjackSessionListView(generics.ListAPIView):
    serializer_class = BlackjackSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BlackjackSession.objects.filter(user=self.request.user)[:12]


class CurrentBlackjackSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        session = (
            BlackjackSession.objects.filter(user=request.user)
            .order_by('-created_at')
            .first()
        )
        if session is None:
            return Response({'session': None}, status=status.HTTP_200_OK)

        return Response(BlackjackSessionSerializer(session).data, status=status.HTTP_200_OK)


class StartBlackjackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BlackjackStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = start_blackjack_session(
            user=request.user,
            bet_amount=serializer.validated_data['bet_amount'],
            client_seed=serializer.validated_data.get('client_seed', '')
        )

        return Response(BlackjackSessionSerializer(session).data, status=status.HTTP_201_CREATED)


class BlackjackActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BlackjackActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = apply_blackjack_action(
            user=request.user,
            action=serializer.validated_data['action']
        )

        return Response(BlackjackSessionSerializer(session).data, status=status.HTTP_200_OK)
