import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../core/services/api.service';
import { BlackjackSession } from '../../core/interfaces/api.models';

@Component({
  selector: 'app-blackjack-page',
  imports: [FormsModule, RouterLink],
  templateUrl: './blackjack.page.html',
  styleUrl: './blackjack.page.scss'
})
export class BlackjackPageComponent implements OnInit {
  private readonly api = inject(ApiService);

  protected betAmount = '50.00';
  protected clientSeed = '';
  protected session: BlackjackSession | null = null;
  protected loading = false;
  protected errorMessage = '';

  protected get isAuthenticated(): boolean {
    return this.api.isAuthenticated();
  }

  ngOnInit(): void {
    if (this.isAuthenticated) {
      this.refreshTable();
      this.api.getWallet().subscribe({ error: () => undefined });
    }
  }

  protected refreshTable(): void {
    this.loading = true;
    this.errorMessage = '';

    this.api.getCurrentBlackjack().subscribe({
      next: (session) => {
        this.session = session;
        this.loading = false;
      },
      error: (error: Error) => {
        this.errorMessage = error.message;
        this.loading = false;
      }
    });
  }

  protected startHand(): void {
    this.loading = true;
    this.errorMessage = '';

    this.api.startBlackjack(this.betAmount, this.clientSeed).subscribe({
      next: (session) => {
        this.session = session;
        this.api.getWallet().subscribe({ error: () => undefined });
        this.loading = false;
      },
      error: (error: Error) => {
        this.errorMessage = error.message;
        this.loading = false;
      }
    });
  }

  protected sendAction(action: 'hit' | 'stand' | 'double' | 'split'): void {
    this.loading = true;
    this.errorMessage = '';

    this.api.actOnBlackjack(action).subscribe({
      next: (session) => {
        this.session = session;
        this.api.getWallet().subscribe({ error: () => undefined });
        this.loading = false;
      },
      error: (error: Error) => {
        this.errorMessage = error.message;
        this.loading = false;
      }
    });
  }

  protected handTotal(cards: string[]): number {
    let total = 0;
    let aces = 0;

    for (const card of cards) {
      const rank = card.slice(0, -1);
      if (['J', 'Q', 'K'].includes(rank)) {
        total += 10;
      } else if (rank === 'A') {
        total += 11;
        aces += 1;
      } else {
        total += Number(rank);
      }
    }

    while (total > 21 && aces > 0) {
      total -= 10;
      aces -= 1;
    }

    return total;
  }

  protected formatOutcome(outcome: string): string {
    return outcome ? outcome.replace('_', ' ') : 'In play';
  }
}
