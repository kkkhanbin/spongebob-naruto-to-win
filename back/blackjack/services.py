from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from secrets import SystemRandom
from typing import Iterable

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import NotFound

from games.models import GameRecord
from wallet.views import get_wallet_for_user

from .models import ActionLog, BetTransaction, GameSession, Hand

SUITS = ['hearts', 'diamonds', 'clubs', 'spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
FACE_CARD_VALUE = 10
BLACKJACK_TOTAL = 21
DEALER_STAND_TOTAL = 17
DECK_COUNT = 6
SHUFFLE_BUFFER = 52
BLACKJACK_PAYOUT_MULTIPLIER = Decimal('1.50')


@dataclass
class HandValue:
    total: int
    is_soft: bool


def _build_shuffled_deck() -> list[dict[str, object]]:
    deck = []
    for _ in range(DECK_COUNT):
        for suit in SUITS:
            for rank in RANKS:
                deck.append(
                    {
                        'rank': rank,
                        'suit': suit,
                        'value': _card_numeric_value(rank),
                    }
                )
    SystemRandom().shuffle(deck)
    return deck


def _card_numeric_value(rank: str) -> int:
    if rank == 'A':
        return 11
    if rank in {'J', 'Q', 'K'}:
        return FACE_CARD_VALUE
    return int(rank)


def calculate_hand_value(cards: Iterable[dict[str, object]]) -> HandValue:
    total = 0
    aces = 0
    for card in cards:
        total += int(card['value'])
        if card['rank'] == 'A':
            aces += 1

    while total > BLACKJACK_TOTAL and aces:
        total -= 10
        aces -= 1

    return HandValue(total=total, is_soft=aces > 0)


def masked_dealer_cards(cards: list[dict[str, object]], reveal_hidden: bool) -> list[dict[str, object]]:
    if reveal_hidden or len(cards) < 2:
        return cards

    hidden = {'rank': '?', 'suit': 'hidden', 'value': 0, 'hidden': True}
    return [cards[0], hidden]


def ensure_fresh_deck(deck_state: list[dict[str, object]]) -> list[dict[str, object]]:
    if len(deck_state) < SHUFFLE_BUFFER:
        return _build_shuffled_deck()
    return deck_state


def draw_card(session: GameSession) -> dict[str, object]:
    session.deck_state = ensure_fresh_deck(session.deck_state)
    if not session.deck_state:
        session.deck_state = _build_shuffled_deck()

    card = session.deck_state.pop()
    session.save(update_fields=['deck_state', 'updated_at'])
    return card


def active_hands(session: GameSession) -> list[Hand]:
    return list(session.hands.order_by('hand_index'))


def get_active_hand(session: GameSession) -> Hand:
    hands = active_hands(session)
    try:
        return hands[session.current_hand_index]
    except IndexError as exc:
        raise ValidationError('Active hand is unavailable.') from exc


def can_split(hand: Hand) -> bool:
    if hand.is_finished or hand.is_doubled or len(hand.cards) != 2:
        return False
    ranks = [card['rank'] for card in hand.cards]
    return ranks[0] == ranks[1]


def can_double(hand: Hand) -> bool:
    return not hand.is_finished and not hand.is_doubled and len(hand.cards) == 2


def is_blackjack(cards: list[dict[str, object]]) -> bool:
    return len(cards) == 2 and calculate_hand_value(cards).total == BLACKJACK_TOTAL


def next_unfinished_hand_index(session: GameSession) -> int | None:
    for hand in active_hands(session):
        if not hand.is_finished:
            return hand.hand_index
    return None


def log_action(session: GameSession, action: str, hand: Hand | None = None, payload: dict | None = None) -> None:
    ActionLog.objects.create(
        session=session,
        hand=hand,
        action=action,
        payload=payload or {},
    )


def verify_action_nonce(session: GameSession, action_nonce: int) -> None:
    if action_nonce != session.action_nonce:
        raise ValidationError('Out-of-date action request. Refresh the table state and try again.')


def ensure_session_open(session: GameSession) -> None:
    if session.status == 'completed':
        raise ValidationError('This blackjack round is already completed.')


def ensure_player_turn(session: GameSession) -> None:
    if session.status != 'player_turn':
        raise ValidationError('Player actions are unavailable right now.')


def move_to_next_hand_or_dealer(session: GameSession) -> None:
    next_index = next_unfinished_hand_index(session)
    if next_index is None:
        session.status = 'dealer_turn'
    else:
        session.current_hand_index = next_index
        session.status = 'player_turn'

    session.action_nonce += 1
    session.save(update_fields=['current_hand_index', 'status', 'action_nonce', 'updated_at'])


def serialize_hand_state(session: GameSession, hand: Hand) -> dict[str, object]:
    hand_value = calculate_hand_value(hand.cards)
    is_active = session.status == 'player_turn' and session.current_hand_index == hand.hand_index and not hand.is_finished
    return {
        'id': hand.id,
        'hand_index': hand.hand_index,
        'cards': hand.cards,
        'wager': hand.wager,
        'total': hand_value.total,
        'is_soft': hand_value.is_soft,
        'is_active': is_active,
        'is_finished': hand.is_finished,
        'is_doubled': hand.is_doubled,
        'is_split_hand': hand.is_split_hand,
        'can_hit': is_active,
        'can_stand': is_active,
        'can_double': is_active and can_double(hand),
        'can_split': is_active and can_split(hand),
        'outcome': hand.outcome,
        'payout': hand.payout,
    }


def available_actions(session: GameSession) -> list[str]:
    if session.status != 'player_turn':
        return []

    hand = get_active_hand(session)
    actions = []
    if not hand.is_finished:
        actions.extend(['hit', 'stand'])
        if can_double(hand):
            actions.append('double')
        if can_split(hand):
            actions.append('split')
    return actions


def session_message(session: GameSession) -> str:
    if session.status == 'completed':
        return 'Blackjack round settled.'
    if session.status == 'dealer_turn':
        return 'Dealer is playing out the table.'
    hand = get_active_hand(session)
    return f'Waiting for action on hand {hand.hand_index + 1}.'


def session_state(session: GameSession) -> dict[str, object]:
    wallet = get_wallet_for_user(session.user)
    dealer_total = calculate_hand_value(session.dealer_cards).total if session.dealer_hidden_revealed else None
    return {
        'session_id': session.id,
        'status': session.status,
        'balance': wallet.balance,
        'balance_before': session.balance_before,
        'balance_after': session.balance_after,
        'current_hand_index': session.current_hand_index,
        'dealer_hidden_revealed': session.dealer_hidden_revealed,
        'dealer_cards': masked_dealer_cards(session.dealer_cards, session.dealer_hidden_revealed),
        'dealer_total': dealer_total,
        'hands': [serialize_hand_state(session, hand) for hand in active_hands(session)],
        'available_actions': available_actions(session),
        'message': session_message(session),
        'action_nonce': session.action_nonce,
        'created_at': session.created_at,
        'updated_at': session.updated_at,
    }


def _apply_wallet_delta(session: GameSession, amount: Decimal) -> Decimal:
    wallet = get_wallet_for_user(session.user)
    wallet.balance += amount
    wallet.save(update_fields=['balance', 'updated_at'])
    session.balance_after = wallet.balance
    session.save(update_fields=['balance_after', 'updated_at'])
    return wallet.balance


def _deduct_balance(session: GameSession, amount: Decimal, transaction_type: str, hand: Hand | None, note: str) -> None:
    wallet = get_wallet_for_user(session.user)
    if wallet.balance < amount:
        raise ValidationError('Insufficient balance.')

    wallet.balance -= amount
    wallet.save(update_fields=['balance', 'updated_at'])
    BetTransaction.objects.create(
        session=session,
        hand=hand,
        transaction_type=transaction_type,
        amount=amount,
        note=note,
    )


def _finalize_game_record(session: GameSession, dealer_value: int) -> None:
    summary_parts = []
    for hand in active_hands(session):
        summary_parts.append(f'H{hand.hand_index + 1}: {hand.outcome}')

    total_payout = sum((hand.payout for hand in active_hands(session)), Decimal('0.00'))
    GameRecord.objects.create(
        user=session.user,
        game='blackjack',
        bet_amount=session.initial_bet,
        payout=total_payout,
        result='; '.join(summary_parts),
        details={
            'dealer_cards': session.dealer_cards,
            'dealer_total': dealer_value,
            'hands': [
                {
                    'hand_index': hand.hand_index,
                    'cards': hand.cards,
                    'wager': str(hand.wager),
                    'outcome': hand.outcome,
                    'payout': str(hand.payout),
                    'is_doubled': hand.is_doubled,
                    'is_split_hand': hand.is_split_hand,
                }
                for hand in active_hands(session)
            ],
            'audit_log_entries': session.action_logs.count(),
        },
    )


def settle_session(session: GameSession) -> GameSession:
    dealer_value = calculate_hand_value(session.dealer_cards)
    while dealer_value.total < DEALER_STAND_TOTAL:
        session.dealer_cards = [*session.dealer_cards, draw_card(session)]
        dealer_value = calculate_hand_value(session.dealer_cards)

    session.dealer_hidden_revealed = True
    session.status = 'completed'
    session.settled_at = timezone.now()
    session.action_nonce += 1
    session.save(update_fields=['dealer_cards', 'dealer_hidden_revealed', 'status', 'settled_at', 'action_nonce', 'updated_at'])
    log_action(session, 'dealer_play', payload={'dealer_cards': session.dealer_cards, 'dealer_total': dealer_value.total})

    total_return = Decimal('0.00')
    dealer_total = dealer_value.total
    dealer_bust = dealer_total > BLACKJACK_TOTAL

    for hand in active_hands(session):
        hand_value = calculate_hand_value(hand.cards)
        if hand.outcome == 'bust':
            hand.payout = Decimal('0.00')
        elif hand.outcome == 'blackjack':
            hand.payout = hand.wager + (hand.wager * session.blackjack_payout_multiplier)
        elif dealer_bust or hand_value.total > dealer_total:
            hand.outcome = 'win'
            hand.payout = hand.wager * Decimal('2.00')
        elif hand_value.total == dealer_total:
            hand.outcome = 'push'
            hand.payout = hand.wager
        else:
            hand.outcome = 'lose'
            hand.payout = Decimal('0.00')

        hand.is_finished = True
        hand.save(update_fields=['outcome', 'payout', 'is_finished', 'updated_at'])
        total_return += hand.payout

    if total_return:
        _apply_wallet_delta(session, total_return)
        for hand in active_hands(session):
            if hand.payout:
                BetTransaction.objects.create(
                    session=session,
                    hand=hand,
                    transaction_type='payout' if hand.payout > hand.wager else 'refund',
                    amount=hand.payout,
                    note=f'Round settled for hand {hand.hand_index + 1}.',
                )
    else:
        wallet = get_wallet_for_user(session.user)
        session.balance_after = wallet.balance
        session.save(update_fields=['balance_after', 'updated_at'])

    log_action(session, 'settle', payload={'dealer_total': dealer_total, 'dealer_bust': dealer_bust})
    _finalize_game_record(session, dealer_total)
    return session


def settle_natural_blackjack(session: GameSession, dealer_blackjack: bool) -> GameSession:
    hand = active_hands(session)[0]
    session.dealer_hidden_revealed = True
    session.status = 'completed'
    session.settled_at = timezone.now()
    session.action_nonce += 1

    if dealer_blackjack and hand.outcome == 'blackjack':
        hand.outcome = 'push'
        hand.payout = hand.wager
    elif dealer_blackjack:
        hand.outcome = 'lose'
        hand.payout = Decimal('0.00')
    else:
        hand.outcome = 'blackjack'
        hand.payout = hand.wager + (hand.wager * session.blackjack_payout_multiplier)

    hand.is_finished = True
    hand.save(update_fields=['outcome', 'payout', 'is_finished', 'updated_at'])
    session.save(update_fields=['dealer_hidden_revealed', 'status', 'settled_at', 'action_nonce', 'updated_at'])

    if hand.payout:
        _apply_wallet_delta(session, hand.payout)
        BetTransaction.objects.create(
            session=session,
            hand=hand,
            transaction_type='payout' if hand.payout > hand.wager else 'refund',
            amount=hand.payout,
            note='Natural blackjack settlement.',
        )
    else:
        wallet = get_wallet_for_user(session.user)
        session.balance_after = wallet.balance
        session.save(update_fields=['balance_after', 'updated_at'])

    log_action(
        session,
        'settle',
        hand=hand,
        payload={
            'dealer_total': calculate_hand_value(session.dealer_cards).total,
            'natural_blackjack': True,
            'dealer_blackjack': dealer_blackjack,
        },
    )
    _finalize_game_record(session, calculate_hand_value(session.dealer_cards).total)
    return session


@transaction.atomic
def start_session(*, user, bet: Decimal) -> GameSession:
    if GameSession.objects.filter(user=user).exclude(status='completed').exists():
        raise ValidationError('Finish the current blackjack round before starting a new one.')

    deck = _build_shuffled_deck()
    wallet = get_wallet_for_user(user)
    if wallet.balance < bet:
        raise ValidationError('Insufficient balance.')

    wallet.balance -= bet
    wallet.save(update_fields=['balance', 'updated_at'])

    session = GameSession.objects.create(
        user=user,
        deck_state=deck,
        initial_bet=bet,
        balance_before=wallet.balance + bet,
        blackjack_payout_multiplier=BLACKJACK_PAYOUT_MULTIPLIER,
    )

    player_cards = [draw_card(session), draw_card(session)]
    dealer_cards = [draw_card(session), draw_card(session)]
    session.dealer_cards = dealer_cards
    session.save(update_fields=['dealer_cards', 'updated_at'])

    hand = Hand.objects.create(
        session=session,
        hand_index=0,
        cards=player_cards,
        wager=bet,
    )
    BetTransaction.objects.create(
        session=session,
        hand=hand,
        transaction_type='bet',
        amount=bet,
        note='Initial blackjack stake.',
    )
    log_action(session, 'start', hand=hand, payload={'player_cards': player_cards, 'dealer_upcard': dealer_cards[0]})

    player_blackjack = is_blackjack(player_cards)
    dealer_blackjack = is_blackjack(dealer_cards)

    if player_blackjack:
        hand.outcome = 'blackjack'
        hand.is_finished = True
        hand.save(update_fields=['outcome', 'is_finished', 'updated_at'])

    if player_blackjack or dealer_blackjack:
        return settle_natural_blackjack(session, dealer_blackjack=dealer_blackjack)

    return session


@transaction.atomic
def perform_hit(*, session: GameSession, action_nonce: int) -> GameSession:
    session = GameSession.objects.select_for_update().get(pk=session.pk)
    ensure_session_open(session)
    ensure_player_turn(session)
    verify_action_nonce(session, action_nonce)

    hand = get_active_hand(session)
    if hand.is_finished:
        raise ValidationError('This hand is already finished.')

    hand.cards = [*hand.cards, draw_card(session)]
    hand_value = calculate_hand_value(hand.cards)
    if hand_value.total > BLACKJACK_TOTAL:
        hand.outcome = 'bust'
        hand.is_finished = True
    hand.save(update_fields=['cards', 'outcome', 'is_finished', 'updated_at'])
    log_action(session, 'hit', hand=hand, payload={'cards': hand.cards, 'total': hand_value.total})

    if hand.is_finished:
        move_to_next_hand_or_dealer(session)
        if session.status == 'dealer_turn':
            return settle_session(session)
        return session

    session.action_nonce += 1
    session.save(update_fields=['action_nonce', 'updated_at'])
    return session


@transaction.atomic
def perform_stand(*, session: GameSession, action_nonce: int) -> GameSession:
    session = GameSession.objects.select_for_update().get(pk=session.pk)
    ensure_session_open(session)
    ensure_player_turn(session)
    verify_action_nonce(session, action_nonce)

    hand = get_active_hand(session)
    if hand.is_finished:
        raise ValidationError('This hand is already finished.')

    hand.has_stood = True
    hand.is_finished = True
    hand.save(update_fields=['has_stood', 'is_finished', 'updated_at'])
    log_action(session, 'stand', hand=hand, payload={'cards': hand.cards})

    move_to_next_hand_or_dealer(session)
    if session.status == 'dealer_turn':
        return settle_session(session)
    return session


@transaction.atomic
def perform_double(*, session: GameSession, action_nonce: int) -> GameSession:
    session = GameSession.objects.select_for_update().get(pk=session.pk)
    ensure_session_open(session)
    ensure_player_turn(session)
    verify_action_nonce(session, action_nonce)

    hand = get_active_hand(session)
    if not can_double(hand):
        raise ValidationError('Double down is not available for this hand.')

    _deduct_balance(session, hand.wager, 'double', hand, 'Double down stake.')
    hand.wager += hand.wager
    hand.is_doubled = True
    hand.cards = [*hand.cards, draw_card(session)]
    hand_value = calculate_hand_value(hand.cards)
    if hand_value.total > BLACKJACK_TOTAL:
        hand.outcome = 'bust'
    hand.is_finished = True
    hand.save(update_fields=['wager', 'is_doubled', 'cards', 'outcome', 'is_finished', 'updated_at'])
    log_action(session, 'double', hand=hand, payload={'cards': hand.cards, 'total': hand_value.total})

    move_to_next_hand_or_dealer(session)
    if session.status == 'dealer_turn':
        return settle_session(session)
    return session


@transaction.atomic
def perform_split(*, session: GameSession, action_nonce: int) -> GameSession:
    session = GameSession.objects.select_for_update().get(pk=session.pk)
    ensure_session_open(session)
    ensure_player_turn(session)
    verify_action_nonce(session, action_nonce)

    hand = get_active_hand(session)
    if not can_split(hand):
        raise ValidationError('Split is not available for this hand.')

    _deduct_balance(session, hand.wager, 'split', hand, 'Split hand stake.')

    first_card, second_card = hand.cards
    hand.cards = [first_card, draw_card(session)]
    hand.is_split_hand = True
    hand.save(update_fields=['cards', 'is_split_hand', 'updated_at'])

    split_hand = Hand.objects.create(
        session=session,
        hand_index=session.hands.count(),
        cards=[second_card, draw_card(session)],
        wager=hand.wager,
        is_split_hand=True,
    )
    BetTransaction.objects.create(
        session=session,
        hand=split_hand,
        transaction_type='split',
        amount=split_hand.wager,
        note='Additional wager for split hand.',
    )
    log_action(
        session,
        'split',
        hand=hand,
        payload={'left_hand': hand.cards, 'right_hand': split_hand.cards},
    )

    session.action_nonce += 1
    session.save(update_fields=['action_nonce', 'updated_at'])
    return session


def current_session_for_user(user) -> GameSession:
    session = (
        GameSession.objects.filter(user=user)
        .exclude(status='completed')
        .order_by('-created_at')
        .first()
    )
    if not session:
        raise NotFound('No active blackjack session found.')
    return session
