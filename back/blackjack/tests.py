from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from games.models import GameRecord
from wallet.models import Wallet

from .services import calculate_hand_value

User = get_user_model()


class BlackjackFlowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='dealerproof',
            email='dealerproof@example.com',
            password='strong-pass-123',
        )
        self.client.force_authenticate(self.user)
        Wallet.objects.filter(user=self.user).update(balance=Decimal('1000.00'))

    def _deck(self, cards):
        filler = []
        for index in range(80):
            filler.append({'rank': '2', 'suit': f'filler-{index}', 'value': 2})
        return filler + list(reversed(cards))

    @patch('blackjack.services._build_shuffled_deck')
    def test_blackjack_start_and_stand_round(self, build_shuffled_deck):
        build_shuffled_deck.return_value = self._deck(
            [
                {'rank': '9', 'suit': 'hearts', 'value': 9},
                {'rank': '8', 'suit': 'diamonds', 'value': 8},
                {'rank': '10', 'suit': 'spades', 'value': 10},
                {'rank': '6', 'suit': 'clubs', 'value': 6},
                {'rank': '8', 'suit': 'hearts', 'value': 8},
            ]
        )

        start_response = self.client.post(reverse('blackjack-start'), {'bet': '50.00'}, format='json')
        self.assertEqual(start_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(start_response.data['status'], 'player_turn')
        self.assertEqual(start_response.data['hands'][0]['total'], 17)

        stand_response = self.client.post(
            reverse('blackjack-stand'),
            {'action_nonce': start_response.data['action_nonce']},
            format='json',
        )
        self.assertEqual(stand_response.status_code, status.HTTP_200_OK)
        self.assertEqual(stand_response.data['status'], 'completed')
        self.assertEqual(stand_response.data['hands'][0]['outcome'], 'win')
        self.assertEqual(Decimal(stand_response.data['balance']), Decimal('1050.00'))
        self.assertTrue(GameRecord.objects.filter(user=self.user, game='blackjack').exists())

    @patch('blackjack.services._build_shuffled_deck')
    def test_double_down_updates_wager_and_balance(self, build_shuffled_deck):
        build_shuffled_deck.return_value = self._deck(
            [
                {'rank': '5', 'suit': 'hearts', 'value': 5},
                {'rank': '6', 'suit': 'diamonds', 'value': 6},
                {'rank': '9', 'suit': 'spades', 'value': 9},
                {'rank': '7', 'suit': 'clubs', 'value': 7},
                {'rank': '10', 'suit': 'hearts', 'value': 10},
                {'rank': '6', 'suit': 'clubs', 'value': 6},
            ]
        )

        start_response = self.client.post(reverse('blackjack-start'), {'bet': '40.00'}, format='json')
        double_response = self.client.post(
            reverse('blackjack-double'),
            {'action_nonce': start_response.data['action_nonce']},
            format='json',
        )

        self.assertEqual(double_response.status_code, status.HTTP_200_OK)
        self.assertEqual(double_response.data['status'], 'completed')
        self.assertTrue(double_response.data['hands'][0]['is_doubled'])
        self.assertEqual(Decimal(double_response.data['hands'][0]['wager']), Decimal('80.00'))

    @patch('blackjack.services._build_shuffled_deck')
    def test_split_creates_second_hand(self, build_shuffled_deck):
        build_shuffled_deck.return_value = self._deck(
            [
                {'rank': '8', 'suit': 'hearts', 'value': 8},
                {'rank': '8', 'suit': 'spades', 'value': 8},
                {'rank': '6', 'suit': 'diamonds', 'value': 6},
                {'rank': '9', 'suit': 'clubs', 'value': 9},
                {'rank': '3', 'suit': 'hearts', 'value': 3},
                {'rank': '4', 'suit': 'clubs', 'value': 4},
            ]
        )

        start_response = self.client.post(reverse('blackjack-start'), {'bet': '25.00'}, format='json')
        split_response = self.client.post(
            reverse('blackjack-split'),
            {'action_nonce': start_response.data['action_nonce']},
            format='json',
        )

        self.assertEqual(split_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(split_response.data['hands']), 2)
        self.assertTrue(split_response.data['hands'][0]['is_split_hand'])
        self.assertTrue(split_response.data['hands'][1]['is_split_hand'])

    def test_state_endpoint_returns_not_found_without_active_round(self):
        state_response = self.client.get(reverse('blackjack-state'))

        self.assertEqual(state_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(state_response.data['detail'], 'No active blackjack session found.')

    @patch('blackjack.services._build_shuffled_deck')
    def test_rejects_second_round_while_first_is_active(self, build_shuffled_deck):
        build_shuffled_deck.return_value = self._deck(
            [
                {'rank': '10', 'suit': 'hearts', 'value': 10},
                {'rank': '7', 'suit': 'diamonds', 'value': 7},
                {'rank': '6', 'suit': 'spades', 'value': 6},
                {'rank': '8', 'suit': 'clubs', 'value': 8},
            ]
        )

        first_response = self.client.post(reverse('blackjack-start'), {'bet': '20.00'}, format='json')
        second_response = self.client.post(reverse('blackjack-start'), {'bet': '30.00'}, format='json')

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Finish the current blackjack round', str(second_response.data))

    @patch('blackjack.services._build_shuffled_deck')
    def test_state_endpoint_returns_active_round(self, build_shuffled_deck):
        build_shuffled_deck.return_value = self._deck(
            [
                {'rank': '10', 'suit': 'hearts', 'value': 10},
                {'rank': '7', 'suit': 'diamonds', 'value': 7},
                {'rank': '6', 'suit': 'spades', 'value': 6},
                {'rank': '8', 'suit': 'clubs', 'value': 8},
            ]
        )

        self.client.post(reverse('blackjack-start'), {'bet': '20.00'}, format='json')
        state_response = self.client.get(reverse('blackjack-state'))

        self.assertEqual(state_response.status_code, status.HTTP_200_OK)
        self.assertEqual(state_response.data['status'], 'player_turn')
        self.assertEqual(len(state_response.data['dealer_cards']), 2)

    @patch('blackjack.services._build_shuffled_deck')
    def test_rejects_replayed_action_nonce(self, build_shuffled_deck):
        build_shuffled_deck.return_value = self._deck(
            [
                {'rank': '9', 'suit': 'hearts', 'value': 9},
                {'rank': '5', 'suit': 'diamonds', 'value': 5},
                {'rank': '7', 'suit': 'spades', 'value': 7},
                {'rank': '8', 'suit': 'clubs', 'value': 8},
                {'rank': '2', 'suit': 'hearts', 'value': 2},
            ]
        )

        start_response = self.client.post(reverse('blackjack-start'), {'bet': '20.00'}, format='json')
        first_hit = self.client.post(
            reverse('blackjack-hit'),
            {'action_nonce': start_response.data['action_nonce']},
            format='json',
        )
        replayed_hit = self.client.post(
            reverse('blackjack-hit'),
            {'action_nonce': start_response.data['action_nonce']},
            format='json',
        )

        self.assertEqual(first_hit.status_code, status.HTTP_200_OK)
        self.assertEqual(replayed_hit.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Out-of-date action request', str(replayed_hit.data))


class BlackjackScoringTests(APITestCase):
    def test_ace_scoring_switches_between_soft_and_hard(self):
        result = calculate_hand_value(
            [
                {'rank': 'A', 'suit': 'spades', 'value': 11},
                {'rank': '9', 'suit': 'hearts', 'value': 9},
                {'rank': '5', 'suit': 'clubs', 'value': 5},
            ]
        )
        self.assertEqual(result.total, 15)
        self.assertFalse(result.is_soft)
