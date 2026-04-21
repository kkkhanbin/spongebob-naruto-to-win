import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';

import { ApiService, GameHistory, Wallet } from '../services/api.service';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './home.html',
  styleUrl: './home.scss',
})
export class Home implements OnInit {
  wallet: Wallet | null = null;
  recentGames: GameHistory[] = [];
  loading = false;
  errorMessage = '';

  readonly features = [
    'JWT авторизация и HTTP interceptor',
    'Роутинг между 4 страницами приложения',
    'API-интеграция через единый Angular Service',
    'Управление кошельком и история игр',
  ];

  constructor(
    public readonly authService: AuthService,
    private readonly apiService: ApiService,
    private readonly router: Router,
  ) {}

  ngOnInit() {
    if (this.authService.isLoggedIn()) {
      this.loadDashboard();
    }
  }

  loadDashboard() {
    this.loading = true;
    this.errorMessage = '';

    this.apiService.getWallet().subscribe({
      next: (wallet) => {
        this.wallet = wallet;
      },
      error: (error: Error) => {
        this.errorMessage = error.message;
      },
    });

    this.apiService.getGameHistory().subscribe({
      next: (history) => {
        this.recentGames = history.slice(0, 3);
        this.loading = false;
      },
      error: (error: Error) => {
        this.errorMessage = error.message;
        this.loading = false;
      },
    });
  }

  openProfile() {
    this.router.navigate(['/profile']);
  }

  openRoulette() {
    this.router.navigate(['/roulette']);
  }

  openLotto() {
    this.router.navigate(['/lotto']);
  }
}
