import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { ApiService, LoginRequest, LoginResponse } from './api.service';
import { BehaviorSubject, map, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private isAuthenticatedSubject = new BehaviorSubject<boolean>(this.hasToken());
  readonly isAuthenticated$ = this.isAuthenticatedSubject.asObservable();

  constructor(
    private readonly apiService: ApiService,
    private readonly router: Router,
  ) {}

  private hasToken(): boolean {
    return !!localStorage.getItem('access_token');
  }

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.apiService.login(credentials);
  }

  refreshAccessToken(): Observable<string> {
    const refresh = this.getRefreshToken();
    if (!refresh) {
      throw new Error('No refresh token found');
    }

    return this.apiService.refreshToken(refresh).pipe(
      map((response) => {
        const access = response.access;
        localStorage.setItem('access_token', access);

        if ('refresh' in response && response.refresh) {
          localStorage.setItem('refresh_token', response.refresh);
        }

        this.isAuthenticatedSubject.next(true);
        return access;
      }),
    );
  }

  setTokens(tokens: LoginResponse): void {
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
    this.isAuthenticatedSubject.next(true);
  }

  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  clearTokens(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.isAuthenticatedSubject.next(false);
  }

  logout(): void {
    this.clearTokens();
    this.router.navigate(['/login']);
  }

  isLoggedIn(): boolean {
    return this.hasToken();
  }
}
