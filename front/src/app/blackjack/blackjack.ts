import { AsyncPipe, CommonModule, TitleCasePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit, inject } from '@angular/core';
import { RouterLink } from '@angular/router';

import {
  BlackjackHandState,
  BlackjackService,
  BlackjackState,
} from '../services/blackjack.service';
import { BlackjackBetComponent } from './blackjack-bet.component';
import { BlackjackControlsComponent } from './blackjack-controls.component';
import { BlackjackHandComponent } from './blackjack-hand.component';

@Component({
  selector: 'app-blackjack',
  standalone: true,
  imports: [
    AsyncPipe,
    CommonModule,
    RouterLink,
    TitleCasePipe,
    BlackjackBetComponent,
    BlackjackControlsComponent,
    BlackjackHandComponent,
  ],
  templateUrl: './blackjack.html',
  styleUrl: './blackjack.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Blackjack implements OnInit {
  private readonly blackjackService = inject(BlackjackService);

  protected readonly state$ = this.blackjackService.state$;
  protected readonly loading$ = this.blackjackService.loading$;
  protected readonly error$ = this.blackjackService.error$;

  betAmount = 25;

  ngOnInit() {
    this.blackjackService.loadState().subscribe({
      error: () => {
        // Render the table even if no active round exists yet.
      },
    });
  }

  startRound(bet: number) {
    this.betAmount = bet;
    this.blackjackService.start(bet).subscribe();
  }

  hit() {
    this.blackjackService.hit().subscribe();
  }

  stand() {
    this.blackjackService.stand().subscribe();
  }

  double() {
    this.blackjackService.double().subscribe();
  }

  split() {
    this.blackjackService.split().subscribe();
  }

  activeHand(state: BlackjackState | null): BlackjackHandState | null {
    return state?.hands.find((hand) => hand.is_active) ?? null;
  }

  controlsLabel(state: BlackjackState | null) {
    if (!state) {
      return 'Open Table';
    }
    if (state.status === 'completed') {
      return 'Round Closed';
    }
    if (state.status === 'dealer_turn') {
      return 'Dealer Turn';
    }
    const hand = this.activeHand(state);
    return hand ? `Hand ${hand.hand_index + 1}` : 'Player Turn';
  }

  roundInProgress(state: BlackjackState | null) {
    return !!state && state.status !== 'completed';
  }

  outcomeTone(outcome: string | undefined) {
    if (!outcome || outcome === 'pending') {
      return '';
    }
    if (outcome === 'win' || outcome === 'blackjack' || outcome === 'push') {
      return 'round-summary__item--positive';
    }
    return 'round-summary__item--negative';
  }
}
