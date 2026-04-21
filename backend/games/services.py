import hashlib
import secrets
from decimal import Decimal, ROUND_HALF_UP
from random import Random

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from games.models import BlackjackSession, Transaction
from wallet.models import Wallet


DECIMAL_ZERO = Decimal('0.00')
BLACKJACK_PAYOUT = Decimal('2.50')
STANDARD_PAYOUT = Decimal('2.00')
PUSH_PAYOUT = Decimal('1.00')

SUITS = ['S', 'H', 'D', 'C']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']


def money(value: Decimal | str | int | float) -> Decimal:
    return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def rank_of(card: str) -> str:
    return card[:-1]


def create_deck(seed: str) -> list[str]:
    deck = [f'{rank}{suit}' for suit in SUITS for rank in RANKS]
    Random(seed).shuffle(deck)
    return deck


def draw_card(deck: list[str]) -> str:
    if not deck:
        raise ValidationError('The shoe is empty.')
    return deck.pop()


def hand_value(cards: list[str]) -> tuple[int, bool]:
    total = 0
    aces = 0

    for card in cards:
        rank = rank_of(card)
        if rank in {'J', 'Q', 'K'}:
            total += 10
        elif rank == 'A':
            total += 11
            aces += 1
        else:
            total += int(rank)

    while total > 21 and aces:
        total -= 10
        aces -= 1

    return total, aces > 0


def is_blackjack(hand: dict) -> bool:
    total, _ = hand_value(hand['cards'])
    return len(hand['cards']) == 2 and total == 21 and not hand.get('is_split', False)


def serialize_hand(cards: list[str], bet_amount: Decimal, *, is_split: bool = False) -> dict:
    total, _ = hand_value(cards)
    status = 'playing'
    if total > 21:
        status = 'bust'
    elif total == 21 and len(cards) == 2 and not is_split:
        status = 'blackjack'

    return {
        'cards': cards,
        'bet_amount': f'{money(bet_amount):.2f}',
        'status': status,
        'result': '',
        'payout': '0.00',
        'doubled': False,
        'is_split': is_split
    }


def active_hand(session: BlackjackSession) -> dict:
    return session.player_hands[session.current_hand_index]


def hand_is_finished(hand: dict) -> bool:
    return hand['status'] in {'stood', 'bust', 'blackjack', 'resolved'}


def available_actions(session: BlackjackSession) -> list[str]:
    if session.status != 'player_turn':
        return []

    hand = active_hand(session)
    if hand_is_finished(hand):
        return []

    actions = ['hit', 'stand']
    hand_bet = money(hand['bet_amount'])
    wallet_balance = session.user.wallet.balance

    if len(hand['cards']) == 2 and not hand['doubled'] and wallet_balance >= hand_bet:
        actions.append('double')

    same_rank = len(hand['cards']) == 2 and rank_of(hand['cards'][0]) == rank_of(hand['cards'][1])
    if same_rank and wallet_balance >= hand_bet and len(session.player_hands) < 4:
        actions.append('split')

    return actions


@transaction.atomic
def record_transaction(
    *,
    user,
    kind: str,
    amount: Decimal,
    description: str,
    session: BlackjackSession | None = None,
    game_type: str = ''
) -> Wallet:
    wallet = Wallet.objects.select_for_update().get(user=user)
    new_balance = money(wallet.balance + amount)
    if new_balance < DECIMAL_ZERO:
        raise ValidationError('Insufficient balance.')

    wallet.balance = new_balance
    wallet.save(update_fields=['balance', 'updated_at'])

    Transaction.objects.create(
        user=user,
        session=session,
        kind=kind,
        amount=money(amount),
        balance_after=wallet.balance,
        description=description,
        game_type=game_type
    )

    return wallet


def credit_wallet(*, user, amount: Decimal, kind: str, description: str) -> Wallet:
    return record_transaction(
        user=user,
        kind=kind,
        amount=money(amount),
        description=description
    )


@transaction.atomic
def start_blackjack_session(*, user, bet_amount: Decimal, client_seed: str = '') -> BlackjackSession:
    if BlackjackSession.objects.filter(user=user, status__in=['player_turn', 'dealer_turn']).exists():
        raise ValidationError('Finish your current blackjack hand before starting a new one.')

    wager = money(bet_amount)
    if wager <= DECIMAL_ZERO:
        raise ValidationError('Bet amount must be positive.')

    record_transaction(
        user=user,
        kind='bet',
        amount=-wager,
        description='Blackjack opening bet',
        game_type=BlackjackSession.GAME_TYPE
    )

    server_seed = secrets.token_hex(16)
    deck = create_deck(server_seed + client_seed)

    player_cards = [draw_card(deck), draw_card(deck)]
    dealer_cards = [draw_card(deck), draw_card(deck)]
    hand = serialize_hand(player_cards, wager)

    session = BlackjackSession.objects.create(
        user=user,
        bet_amount=wager,
        total_wagered=wager,
        player_hands=[hand],
        dealer_cards=dealer_cards,
        deck=deck,
        client_seed=client_seed,
        server_seed=server_seed,
        server_seed_hash=hashlib.sha256(server_seed.encode()).hexdigest(),
        status='player_turn',
        outcome='pending'
    )

    if hand['status'] == 'blackjack':
        hand['status'] = 'blackjack'
        session.player_hands = [hand]
        resolve_blackjack_session(session)

    return session


def save_session(session: BlackjackSession) -> BlackjackSession:
    session.save()
    return session


def advance_to_next_hand(session: BlackjackSession) -> None:
    for index, hand in enumerate(session.player_hands):
        if not hand_is_finished(hand):
            session.current_hand_index = index
            session.status = 'player_turn'
            return

    session.status = 'dealer_turn'


def settle_bet_delta(*, user, session: BlackjackSession, amount: Decimal, description: str) -> None:
    record_transaction(
        user=user,
        session=session,
        kind='bet',
        amount=-money(amount),
        description=description,
        game_type=BlackjackSession.GAME_TYPE
    )


@transaction.atomic
def apply_blackjack_action(*, user, action: str) -> BlackjackSession:
    try:
        session = BlackjackSession.objects.select_for_update().get(
            user=user,
            status__in=['player_turn', 'dealer_turn']
        )
    except BlackjackSession.DoesNotExist as exc:
        raise ValidationError('There is no active blackjack hand.') from exc

    if session.status != 'player_turn':
        raise ValidationError('The dealer is resolving the current hand.')

    hand = active_hand(session)
    allowed = available_actions(session)
    if action not in allowed:
        raise ValidationError(f'Action "{action}" is not available right now.')

    deck = session.deck

    if action == 'hit':
        hand['cards'].append(draw_card(deck))
        total, _ = hand_value(hand['cards'])
        if total > 21:
            hand['status'] = 'bust'
            advance_to_next_hand(session)
        elif total == 21:
            hand['status'] = 'stood'
            advance_to_next_hand(session)
    elif action == 'stand':
        hand['status'] = 'stood'
        advance_to_next_hand(session)
    elif action == 'double':
        extra_bet = money(hand['bet_amount'])
        settle_bet_delta(
            user=user,
            session=session,
            amount=extra_bet,
            description='Blackjack double down'
        )
        session.total_wagered = money(session.total_wagered + extra_bet)
        hand['bet_amount'] = f'{money(hand["bet_amount"]) + extra_bet:.2f}'
        hand['doubled'] = True
        hand['cards'].append(draw_card(deck))
        total, _ = hand_value(hand['cards'])
        hand['status'] = 'bust' if total > 21 else 'stood'
        advance_to_next_hand(session)
    elif action == 'split':
        extra_bet = money(hand['bet_amount'])
        settle_bet_delta(
            user=user,
            session=session,
            amount=extra_bet,
            description='Blackjack split bet'
        )
        session.total_wagered = money(session.total_wagered + extra_bet)

        first_cards = [hand['cards'][0], draw_card(deck)]
        second_cards = [hand['cards'][1], draw_card(deck)]
        first_hand = serialize_hand(first_cards, extra_bet, is_split=True)
        second_hand = serialize_hand(second_cards, extra_bet, is_split=True)

        if hand_value(first_hand['cards'])[0] == 21:
            first_hand['status'] = 'stood'
        if hand_value(second_hand['cards'])[0] == 21:
            second_hand['status'] = 'stood'

        hands = session.player_hands
        hands[session.current_hand_index:session.current_hand_index + 1] = [first_hand, second_hand]
        session.player_hands = hands
        session.current_hand_index = min(session.current_hand_index, len(session.player_hands) - 1)
        advance_to_next_hand(session)
        if session.status == 'player_turn':
            for index, candidate in enumerate(session.player_hands):
                if not hand_is_finished(candidate):
                    session.current_hand_index = index
                    break

    session.deck = deck

    if session.status == 'dealer_turn':
        resolve_blackjack_session(session)
    else:
        save_session(session)

    return session


def dealer_should_hit(cards: list[str]) -> bool:
    total, _ = hand_value(cards)
    return total < 17


@transaction.atomic
def resolve_blackjack_session(session: BlackjackSession) -> BlackjackSession:
    dealer_cards = session.dealer_cards
    dealer_total, _ = hand_value(dealer_cards)
    dealer_blackjack = len(dealer_cards) == 2 and dealer_total == 21
    player_has_natural_blackjack = any(is_blackjack(hand) for hand in session.player_hands)

    if not player_has_natural_blackjack:
        while dealer_should_hit(dealer_cards):
            dealer_cards.append(draw_card(session.deck))

        dealer_total, _ = hand_value(dealer_cards)
        dealer_blackjack = len(dealer_cards) == 2 and dealer_total == 21

    total_payout = DECIMAL_ZERO
    hand_results = []

    for hand in session.player_hands:
        bet = money(hand['bet_amount'])
        total, _ = hand_value(hand['cards'])
        result = 'loss'
        payout = DECIMAL_ZERO

        if total > 21:
            hand['status'] = 'resolved'
            result = 'loss'
        elif is_blackjack(hand) and not dealer_blackjack:
            hand['status'] = 'resolved'
            result = 'blackjack'
            payout = money(bet * BLACKJACK_PAYOUT)
        elif dealer_total > 21:
            hand['status'] = 'resolved'
            result = 'win'
            payout = money(bet * STANDARD_PAYOUT)
        elif dealer_blackjack and not is_blackjack(hand):
            hand['status'] = 'resolved'
            result = 'loss'
        else:
            if total > dealer_total:
                result = 'win'
                payout = money(bet * STANDARD_PAYOUT)
            elif total == dealer_total:
                result = 'push'
                payout = money(bet * PUSH_PAYOUT)
            else:
                result = 'loss'
            hand['status'] = 'resolved'

        hand['result'] = result
        hand['payout'] = f'{payout:.2f}'
        total_payout += payout
        hand_results.append(result)

    outcome = 'loss'
    unique_results = set(hand_results)
    if unique_results == {'blackjack'}:
        outcome = 'blackjack'
    elif unique_results <= {'win', 'blackjack'}:
        outcome = 'win'
    elif unique_results == {'push'}:
        outcome = 'push'
    elif 'win' in unique_results or 'blackjack' in unique_results or 'push' in unique_results:
        outcome = 'mixed'

    if total_payout > DECIMAL_ZERO:
        record_transaction(
            user=session.user,
            session=session,
            kind='payout',
            amount=total_payout,
            description='Blackjack payout',
            game_type=BlackjackSession.GAME_TYPE
        )

    session.dealer_cards = dealer_cards
    session.status = 'finished'
    session.outcome = outcome
    session.payout_amount = money(total_payout)
    session.net_result = money(total_payout - session.total_wagered)
    session.finished_at = timezone.now()
    session.result_message = build_result_message(session)
    session.save()
    return session


def build_result_message(session: BlackjackSession) -> str:
    net = money(session.net_result)
    if session.outcome == 'blackjack':
        return f'Blackjack pays {session.payout_amount:.2f}.'
    if session.outcome == 'win':
        return f'You won {net:.2f}.'
    if session.outcome == 'push':
        return 'Push. Your stake was returned.'
    if session.outcome == 'mixed':
        return f'Mixed result across split hands. Net {net:.2f}.'
    return f'Hand lost. Net {net:.2f}.'
