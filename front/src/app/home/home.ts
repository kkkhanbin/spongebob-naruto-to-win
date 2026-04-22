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
  walletLoading = false;
  historyLoading = false;
  errorMessage = '';

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
    this.errorMessage = '';
    this.loadWallet();
    this.loadGameHistory();
  }

  loadWallet() {
    this.walletLoading = true;

    this.apiService.getWallet().subscribe({
      next: (wallet) => {
        this.wallet = wallet;
        this.walletLoading = false;
      },
      error: (error: Error) => {
        this.errorMessage = error.message;
        this.walletLoading = false;
      },
    });
  }

  loadGameHistory() {
    this.historyLoading = true;

    this.apiService.getGameHistory().subscribe({
      next: (history) => {
        this.recentGames = history.slice(0, 3);
        this.historyLoading = false;
      },
      error: (error: Error) => {
        this.errorMessage = error.message;
        this.historyLoading = false;
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
