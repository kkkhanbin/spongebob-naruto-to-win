import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { ApiService, LoginRequest, LoginResponse } from './api.service';
import { BehaviorSubject, Observable } from 'rxjs';

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

  setTokens(tokens: LoginResponse): void {
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
    this.isAuthenticatedSubject.next(true);
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.isAuthenticatedSubject.next(false);
    this.router.navigate(['/login']);
  }

  isLoggedIn(): boolean {
    return this.hasToken();
  }
}
