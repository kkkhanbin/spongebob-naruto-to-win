import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, of, throwError } from 'rxjs';
import { catchError, finalize, tap } from 'rxjs/operators';

export interface BlackjackCard {
  rank: string;
  suit: string;
  value: number;
  hidden?: boolean;
}

export interface BlackjackHandState {
  id: number;
  hand_index: number;
  cards: BlackjackCard[];
  wager: string;
  total: number;
  is_soft: boolean;
  is_active: boolean;
  is_finished: boolean;
  is_doubled: boolean;
  is_split_hand: boolean;
  can_hit: boolean;
  can_stand: boolean;
  can_double: boolean;
  can_split: boolean;
  outcome: string;
  payout: string;
}

export interface BlackjackState {
  session_id: number;
  status: 'player_turn' | 'dealer_turn' | 'completed';
  balance: string;
  balance_before: string;
  balance_after: string | null;
  current_hand_index: number;
  dealer_hidden_revealed: boolean;
  dealer_cards: BlackjackCard[];
  dealer_total: number | null;
  hands: BlackjackHandState[];
  available_actions: Array<'hit' | 'stand' | 'double' | 'split'>;
  message: string;
  action_nonce: number;
  created_at: string;
  updated_at: string;
}

@Injectable({
  providedIn: 'root',
})
export class BlackjackService {
  private readonly baseUrl = 'http://127.0.0.1:8000/api/blackjack';

  private readonly stateSubject = new BehaviorSubject<BlackjackState | null>(null);
  private readonly loadingSubject = new BehaviorSubject<boolean>(false);
  private readonly errorSubject = new BehaviorSubject<string>('');

  readonly state$ = this.stateSubject.asObservable();
  readonly loading$ = this.loadingSubject.asObservable();
  readonly error$ = this.errorSubject.asObservable();

  constructor(private readonly http: HttpClient) {}

  get snapshot(): BlackjackState | null {
    return this.stateSubject.value;
  }

  start(bet: number): Observable<BlackjackState> {
    return this.performRequest(this.http.post<BlackjackState>(`${this.baseUrl}/start/`, { bet }));
  }

  loadState(): Observable<BlackjackState | null> {
    this.loadingSubject.next(true);
    this.errorSubject.next('');

    return this.http.get<BlackjackState>(`${this.baseUrl}/state/`).pipe(
      tap((state) => this.stateSubject.next(state)),
      catchError((error: HttpErrorResponse) => {
        if (error.status === 404) {
          this.stateSubject.next(null);
          this.errorSubject.next('');
          return of(null);
        }

        return this.handleError(error);
      }),
      finalize(() => this.loadingSubject.next(false)),
    );
  }

  hit(): Observable<BlackjackState> {
    return this.performAction('hit');
  }

  stand(): Observable<BlackjackState> {
    return this.performAction('stand');
  }

  double(): Observable<BlackjackState> {
    return this.performAction('double');
  }

  split(): Observable<BlackjackState> {
    return this.performAction('split');
  }

  private performAction(action: 'hit' | 'stand' | 'double' | 'split'): Observable<BlackjackState> {
    const state = this.snapshot;
    if (!state) {
      return throwError(() => new Error('Start a blackjack round before taking actions.'));
    }

    return this.performRequest(
      this.http.post<BlackjackState>(`${this.baseUrl}/${action}/`, {
        action_nonce: state.action_nonce,
      }),
    );
  }

  private performRequest(request$: Observable<BlackjackState>): Observable<BlackjackState> {
    this.loadingSubject.next(true);
    this.errorSubject.next('');

    return request$.pipe(
      tap((state) => this.stateSubject.next(state)),
      catchError((error) => this.handleError(error)),
      finalize(() => this.loadingSubject.next(false)),
    );
  }

  private handleError(error: HttpErrorResponse) {
    const message = this.resolveErrorMessage(error);
    this.errorSubject.next(message);
    return throwError(() => new Error(message));
  }

  private resolveErrorMessage(error: HttpErrorResponse): string {
    if (error.error?.detail) {
      return error.error.detail;
    }

    if (typeof error.error === 'object' && error.error !== null) {
      const firstMessage = Object.values(error.error).flat()[0];
      if (typeof firstMessage === 'string') {
        return firstMessage;
      }
    }

    if (error.status === 0) {
      return 'Backend is unavailable. Start Django on port 8000.';
    }

    if (error.status === 404) {
      return 'No active blackjack session found. Start a new round.';
    }

    return `Request failed (${error.status}). Please try again.`;
  }
}
