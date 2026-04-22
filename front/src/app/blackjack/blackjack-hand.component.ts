import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

import { BlackjackCard, BlackjackHandState } from '../services/blackjack.service';

@Component({
  selector: 'app-blackjack-hand',
  standalone: true,
  imports: [CommonModule],
  template: `
    <section class="card hand-panel" [class.hand-panel--dealer]="dealer">
      <div class="hand-panel__header">
        <div>
          <p class="eyebrow">{{ title }}</p>
          <h3>{{ subtitle }}</h3>
        </div>
        <div class="hand-panel__meta">
          @if (total !== null) {
            <strong>{{ total }}</strong>
          } @else {
            <strong>Hidden</strong>
          }

          @if (hand) {
            <span>\${{ hand.wager }}</span>
          }
        </div>
      </div>

      <div class="card-row">
        @for (card of cards; track trackCard($index, card)) {
          <article class="playing-card" [class.playing-card--hidden]="card.hidden">
            @if (card.hidden) {
              <div class="playing-card__back"></div>
            } @else {
              <div class="playing-card__rank">{{ card.rank }}</div>
              <div class="playing-card__suit" [class.playing-card__suit--red]="isRed(card.suit)">
                {{ suitIcon(card.suit) }}
              </div>
            }
          </article>
        }
      </div>

      @if (hand) {
        <div class="hand-status">
          <span [class.hand-status__pill--active]="hand.is_active">
            {{ hand.is_active ? 'Active Hand' : hand.outcome === 'pending' ? 'Waiting' : hand.outcome }}
          </span>
          @if (hand.is_split_hand) {
            <span>Split</span>
          }
          @if (hand.is_doubled) {
            <span>Doubled</span>
          }
          @if (hand.is_soft) {
            <span>Soft {{ hand.total }}</span>
          }
        </div>
      }
    </section>
  `,
  styles: `
    .hand-panel {
      padding: 1.35rem;
      display: grid;
      gap: 1rem;
    }

    .hand-panel--dealer {
      background:
        radial-gradient(circle at top right, rgba(103, 232, 249, 0.12), transparent 34%),
        var(--panel);
    }

    .hand-panel__header {
      display: flex;
      justify-content: space-between;
      gap: 1rem;
      align-items: center;
    }

    .hand-panel__header h3 {
      margin: 0.3rem 0 0;
      font-size: 1.4rem;
    }

    .hand-panel__meta {
      display: grid;
      justify-items: end;
      gap: 0.25rem;
    }

    .hand-panel__meta strong {
      font-size: 1.6rem;
      color: #fff2bf;
    }

    .hand-panel__meta span {
      color: var(--muted);
      font-weight: 700;
    }

    .card-row {
      display: flex;
      flex-wrap: wrap;
      gap: 0.85rem;
      min-height: 8.5rem;
    }

    .playing-card {
      width: 5.4rem;
      aspect-ratio: 5 / 7;
      padding: 0.7rem;
      border-radius: 1rem;
      display: grid;
      align-content: space-between;
      color: #111827;
      background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(240, 242, 245, 0.98));
      box-shadow:
        0 18px 36px rgba(0, 0, 0, 0.28),
        inset 0 1px 0 rgba(255, 255, 255, 0.9);
      transform-origin: center bottom;
      animation: card-in 220ms ease both;
    }

    .playing-card--hidden {
      background:
        linear-gradient(135deg, rgba(255, 77, 109, 0.3), rgba(103, 232, 249, 0.3)),
        linear-gradient(180deg, #15253f, #0c1528);
      border: 1px solid rgba(255, 255, 255, 0.12);
    }

    .playing-card__back {
      border-radius: 0.7rem;
      border: 1px dashed rgba(255, 255, 255, 0.28);
      background:
        repeating-linear-gradient(
          45deg,
          rgba(255, 255, 255, 0.12),
          rgba(255, 255, 255, 0.12) 6px,
          transparent 6px,
          transparent 12px
        );
    }

    .playing-card__rank {
      font-size: 1.25rem;
      font-weight: 900;
    }

    .playing-card__suit {
      align-self: end;
      justify-self: end;
      font-size: 1.8rem;
      color: #111827;
    }

    .playing-card__suit--red {
      color: #b91c1c;
    }

    .hand-status {
      display: flex;
      flex-wrap: wrap;
      gap: 0.6rem;
    }

    .hand-status span {
      padding: 0.45rem 0.75rem;
      border-radius: 999px;
      font-size: 0.78rem;
      font-weight: 800;
      color: #d5e3fb;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .hand-status__pill--active {
      color: #160b14;
      background: linear-gradient(135deg, #ffe066, #ff8c42);
      border-color: transparent;
    }

    @keyframes card-in {
      from {
        opacity: 0;
        transform: translateY(8px) rotate(-4deg);
      }

      to {
        opacity: 1;
        transform: translateY(0) rotate(0deg);
      }
    }
  `,
})
export class BlackjackHandComponent {
  @Input({ required: true }) title = '';
  @Input({ required: true }) subtitle = '';
  @Input({ required: true }) cards: BlackjackCard[] = [];
  @Input() total: number | null = null;
  @Input() hand: BlackjackHandState | null = null;
  @Input() dealer = false;

  suitIcon(suit: string) {
    return (
      {
        hearts: '\u2665',
        diamonds: '\u2666',
        clubs: '\u2663',
        spades: '\u2660',
      }[suit] ?? '?'
    );
  }

  isRed(suit: string) {
    return suit === 'hearts' || suit === 'diamonds';
  }

  trackCard(index: number, card: BlackjackCard) {
    return `${index}-${card.rank}-${card.suit}-${card.hidden ? 'hidden' : 'face'}`;
  }
}
