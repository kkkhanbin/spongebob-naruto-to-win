import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, map, tap, throwError } from 'rxjs';
import {
  ApiErrorResponse,
  BlackjackSession,
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  TransactionItem,
  UserProfile,
  Wallet
} from '../interfaces/api.models';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://127.0.0.1:8000/api';

  readonly currentUser = signal<UserProfile | null>(null);
  readonly currentWallet = signal<Wallet | null>(null);

  register(payload: RegisterRequest): Observable<unknown> {
    return this.http
      .post(`${this.apiUrl}/auth/register/`, payload)
      .pipe(catchError((error) => this.handleError(error.error)));
  }

  login(payload: LoginRequest): Observable<TokenResponse> {
    return this.http
      .post<TokenResponse>(`${this.apiUrl}/auth/login/`, payload)
      .pipe(catchError((error) => this.handleError(error.error)));
  }

  getCurrentUser(): Observable<UserProfile> {
    return this.http
      .get<UserProfile>(`${this.apiUrl}/auth/me/`)
      .pipe(
        tap((user) => this.currentUser.set(user)),
        catchError((error) => this.handleError(error.error))
      );
  }

  getWallet(): Observable<Wallet> {
    return this.http
      .get<Wallet>(`${this.apiUrl}/wallet/`)
      .pipe(
        tap((wallet) => this.currentWallet.set(wallet)),
        catchError((error) => this.handleError(error.error))
      );
  }

  topUpWallet(amount: string): Observable<Wallet> {
    return this.http
      .post<Wallet>(`${this.apiUrl}/wallet/top-up/`, { amount })
      .pipe(
        tap((wallet) => this.currentWallet.set(wallet)),
        catchError((error) => this.handleError(error.error))
      );
  }

  getTransactions(): Observable<TransactionItem[]> {
    return this.http
      .get<TransactionItem[]>(`${this.apiUrl}/transactions/`)
      .pipe(catchError((error) => this.handleError(error.error)));
  }

  getBlackjackHistory(): Observable<BlackjackSession[]> {
    return this.http
      .get<BlackjackSession[]>(`${this.apiUrl}/blackjack/history/`)
      .pipe(catchError((error) => this.handleError(error.error)));
  }

  getCurrentBlackjack(): Observable<BlackjackSession | null> {
    return this.http
      .get<BlackjackSession | { session: null }>(`${this.apiUrl}/blackjack/current/`)
      .pipe(
        map((response) => ('session' in response ? null : response)),
        catchError((error) => this.handleError(error.error))
      );
  }

  startBlackjack(betAmount: string, clientSeed: string): Observable<BlackjackSession> {
    return this.http
      .post<BlackjackSession>(`${this.apiUrl}/blackjack/start/`, {
        bet_amount: betAmount,
        client_seed: clientSeed
      })
      .pipe(catchError((error) => this.handleError(error.error)));
  }

  actOnBlackjack(action: 'hit' | 'stand' | 'double' | 'split'): Observable<BlackjackSession> {
    return this.http
      .post<BlackjackSession>(`${this.apiUrl}/blackjack/action/`, { action })
      .pipe(catchError((error) => this.handleError(error.error)));
  }

  hydrateSession(): void {
    if (!this.isAuthenticated()) {
      this.currentUser.set(null);
      this.currentWallet.set(null);
      return;
    }

    this.getCurrentUser().subscribe({
      error: () => {
        this.currentUser.set(null);
      }
    });

    this.getWallet().subscribe({
      error: () => {
        this.currentWallet.set(null);
      }
    });
  }

  setTokens(tokens: TokenResponse): void {
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
  }

  clearTokens(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.currentUser.set(null);
    this.currentWallet.set(null);
  }

  isAuthenticated(): boolean {
    return Boolean(localStorage.getItem('access_token'));
  }

  private handleError(error: ApiErrorResponse | null | undefined) {
    if (!error) {
      return throwError(() => new Error('The server is unavailable right now.'));
    }

    if (typeof error.detail === 'string') {
      return throwError(() => new Error(error.detail));
    }

    const fieldError = Object.entries(error)
      .map(([field, value]) => {
        const text = Array.isArray(value) ? value.join(', ') : String(value);
        return `${field}: ${text}`;
      })
      .join(' | ');

    return throwError(() => new Error(fieldError || 'Request failed.'));
  }
}
