from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import BlackjackStateSerializer, SessionActionSerializer, StartBlackjackSerializer
from .services import (
    current_session_for_user,
    perform_double,
    perform_hit,
    perform_split,
    perform_stand,
    session_state,
    start_session,
)


class BlackjackStartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StartBlackjackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = start_session(user=request.user, bet=serializer.validated_data['bet'])
        return Response(BlackjackStateSerializer(session_state(session)).data, status=status.HTTP_201_CREATED)


class BlackjackStateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        session = current_session_for_user(request.user)
        return Response(BlackjackStateSerializer(session_state(session)).data)


class BlackjackHitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SessionActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = perform_hit(
            session=current_session_for_user(request.user),
            action_nonce=serializer.validated_data['action_nonce'],
        )
        return Response(BlackjackStateSerializer(session_state(session)).data)


class BlackjackStandView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SessionActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = perform_stand(
            session=current_session_for_user(request.user),
            action_nonce=serializer.validated_data['action_nonce'],
        )
        return Response(BlackjackStateSerializer(session_state(session)).data)


class BlackjackDoubleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SessionActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = perform_double(
            session=current_session_for_user(request.user),
            action_nonce=serializer.validated_data['action_nonce'],
        )
        return Response(BlackjackStateSerializer(session_state(session)).data)


class BlackjackSplitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SessionActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = perform_split(
            session=current_session_for_user(request.user),
            action_nonce=serializer.validated_data['action_nonce'],
        )
        return Response(BlackjackStateSerializer(session_state(session)).data)
