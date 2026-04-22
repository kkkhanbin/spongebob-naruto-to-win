import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-blackjack-bet',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="card panel">
      <div class="panel__header">
        <div>
          <p class="eyebrow">Buy In</p>
          <h2>Open a New Round</h2>
        </div>
        <span class="panel__tag">3:2 blackjack payout</span>
      </div>

      <form class="bet-form" (ngSubmit)="submitBet()">
        <label>
          Bet Amount
          <input
            type="number"
            name="betAmount"
            min="1"
            step="1"
            [(ngModel)]="betAmount"
            [disabled]="disabled"
            required />
        </label>

        <button class="submit" type="submit" [disabled]="disabled || betAmount < 1">
          {{ disabled ? 'Round In Progress' : 'Deal Cards' }}
        </button>
      </form>
    </section>
  `,
  styles: `
    .panel {
      padding: 1.4rem;
    }

    .panel__header {
      display: flex;
      justify-content: space-between;
      gap: 1rem;
      align-items: start;
      margin-bottom: 1rem;
    }

    .panel__header h2 {
      margin: 0.35rem 0 0;
    }

    .panel__tag {
      padding: 0.45rem 0.8rem;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.09);
      font-size: 0.78rem;
      font-weight: 800;
      color: #ffe7a2;
    }

    .bet-form {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 0.9rem;
      align-items: end;
    }

    label {
      display: grid;
      gap: 0.45rem;
      color: var(--muted);
      font-weight: 700;
    }

    input {
      border: 1px solid var(--line);
      border-radius: 1rem;
      padding: 0.9rem 1rem;
      background: rgba(255, 255, 255, 0.04);
      color: var(--text);
    }

    .submit {
      border: 0;
      border-radius: 1rem;
      padding: 0.95rem 1.2rem;
      font-weight: 900;
      cursor: pointer;
      color: #160b14;
      background: linear-gradient(135deg, #ffe066, #ff8c42 58%, #ff4d6d);
      box-shadow: 0 18px 36px rgba(255, 123, 80, 0.22);
    }

    .submit:disabled {
      cursor: not-allowed;
      opacity: 0.6;
    }

    @media (max-width: 640px) {
      .bet-form {
        grid-template-columns: 1fr;
      }
    }
  `,
})
export class BlackjackBetComponent {
  @Input() disabled = false;
  @Input() betAmount = 25;
  @Output() readonly betAmountChange = new EventEmitter<number>();
  @Output() readonly startRound = new EventEmitter<number>();

  submitBet() {
    this.betAmountChange.emit(this.betAmount);
    this.startRound.emit(this.betAmount);
  }
}
