import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { ApiService, GameHistory, User, Wallet } from '../services/api.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, DatePipe],
  templateUrl: './profile.html',
  styleUrl: './profile.scss',
})
export class Profile implements OnInit {
  user: User | null = null;
  wallet: Wallet | null = null;
  gameHistory: GameHistory[] = [];
  errorMessage = '';
  successMessage = '';
  loading = false;
  depositAmount = 100;
  birthDateDraft = '';

  constructor(
    private readonly apiService: ApiService,
    private readonly cdr: ChangeDetectorRef,
  ) {}

  ngOnInit() {
    this.refreshAll();
  }

  refreshAll() {
    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';
    this.loadProfile();
    this.loadWallet();
    this.loadGameHistory();
  }

  loadProfile() {
    this.apiService.getProfile().subscribe({
      next: (user) => {
        this.user = user;
        this.birthDateDraft = user.birth_date ?? '';
        this.cdr.detectChanges();
      },
      error: (error: Error) => {
        this.errorMessage = error.message;
        this.loading = false;
        this.cdr.detectChanges();
      },
    });
  }

  loadWallet() {
    this.apiService.getWallet().subscribe({
      next: (wallet) => {
        this.wallet = wallet;
        this.cdr.detectChanges();
      },
      error: (error: Error) => {
        this.errorMessage = error.message;
        this.loading = false;
        this.cdr.detectChanges();
      },
    });
  }

  loadGameHistory() {
    this.apiService.getGameHistory().subscribe({
      next: (history) => {
        this.gameHistory = history;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (error: Error) => {
        this.errorMessage = error.message;
        this.loading = false;
        this.cdr.detectChanges();
      },
    });
  }

  depositFunds() {
    this.errorMessage = '';
    this.successMessage = '';

    this.apiService.deposit(this.depositAmount).subscribe({
      next: (wallet) => {
        this.wallet = wallet;
        this.successMessage = `Баланс пополнен на $${this.depositAmount}.`;
        this.cdr.detectChanges();
      },
      error: (error: Error) => {
        this.errorMessage = error.message;
        this.cdr.detectChanges();
      },
    });
  }

  updateBirthDate() {
    this.errorMessage = '';
    this.successMessage = '';

    this.apiService
      .updateProfile({
        birth_date: this.birthDateDraft || null,
      })
      .subscribe({
        next: (user) => {
          this.user = user;
          this.birthDateDraft = user.birth_date ?? '';
          this.successMessage = 'Дата рождения обновлена.';
          this.cdr.detectChanges();
        },
        error: (error: Error) => {
          this.errorMessage = error.message;
          this.cdr.detectChanges();
        },
      });
  }
}
