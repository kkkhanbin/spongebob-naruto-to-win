import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, delay } from 'rxjs/operators';

export interface User {
  id: number;
  username: string;
  email: string;
  birth_date?: string | null;
  is_verified: boolean;
}

export interface Wallet {
  balance: string;
  updated_at: string;
}

export interface GameHistory {
  id: number;
  game: 'roulette' | 'lotto';
  result: string;
  amount: string;
  payout: string;
  date: string;
  details: Record<string, unknown>;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  birth_date?: string | null;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
}

export interface RouletteBet {
  bet_type: 'red' | 'black' | 'even' | 'odd';
  amount: number;
}

export interface RouletteResult {
  result: number;
  win: boolean;
  payout: string;
  balance: string;
}

export interface LottoBet {
  numbers: number[];
  amount: number;
}

export interface LottoResult {
  winning_numbers: number[];
  matches: number;
  win: boolean;
  payout: string;
  balance: string;
}

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private readonly baseUrl = 'http://127.0.0.1:8000/api';
  private readonly gameResultDelayMs = 2000;

  constructor(private readonly http: HttpClient) {}

  private handleError(error: HttpErrorResponse) {
    if (error.error?.detail) {
      return throwError(() => new Error(error.error.detail));
    }

    if (typeof error.error === 'object' && error.error !== null) {
      const firstMessage = Object.values(error.error).flat()[0];
      if (typeof firstMessage === 'string') {
        return throwError(() => new Error(firstMessage));
      }
    }

    if (error.status === 0) {
      return throwError(() => new Error('Backend is unavailable. Start Django on port 8000.'));
    }

    return throwError(() => new Error(`Request failed (${error.status}). Please try again.`));
  }

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(`${this.baseUrl}/auth/login/`, credentials)
      .pipe(catchError((error) => this.handleError(error)));
  }

  refreshToken(refresh: string): Observable<LoginResponse | { access: string }> {
    return this.http
      .post<LoginResponse | { access: string }>(`${this.baseUrl}/auth/refresh/`, { refresh })
      .pipe(catchError((error) => this.handleError(error)));
  }

  register(payload: RegisterRequest): Observable<User> {
    return this.http
      .post<User>(`${this.baseUrl}/users/register/`, payload)
      .pipe(catchError((error) => this.handleError(error)));
  }

  getProfile(): Observable<User> {
    return this.http
      .get<User>(`${this.baseUrl}/users/me/`)
      .pipe(catchError((error) => this.handleError(error)));
  }

  updateProfile(payload: Partial<Pick<User, 'birth_date'>>): Observable<User> {
    return this.http
      .patch<User>(`${this.baseUrl}/users/me/`, payload)
      .pipe(catchError((error) => this.handleError(error)));
  }

  getWallet(): Observable<Wallet> {
    return this.http
      .get<Wallet>(`${this.baseUrl}/wallet/`)
      .pipe(catchError((error) => this.handleError(error)));
  }

  deposit(amount: number): Observable<Wallet> {
    return this.http
      .post<Wallet>(`${this.baseUrl}/wallet/deposit/`, { amount })
      .pipe(catchError((error) => this.handleError(error)));
  }

  getGameHistory(): Observable<GameHistory[]> {
    return this.http
      .get<GameHistory[]>(`${this.baseUrl}/games/history/`)
      .pipe(catchError((error) => this.handleError(error)));
  }

  playRoulette(bet: RouletteBet): Observable<RouletteResult> {
    return this.http
      .post<RouletteResult>(`${this.baseUrl}/games/roulette/`, bet)
      .pipe(delay(this.gameResultDelayMs))
      .pipe(catchError((error) => this.handleError(error)));
  }

  playLotto(bet: LottoBet): Observable<LottoResult> {
    return this.http
      .post<LottoResult>(`${this.baseUrl}/games/lotto/`, bet)
      .pipe(delay(this.gameResultDelayMs))
      .pipe(catchError((error) => this.handleError(error)));
  }
}
