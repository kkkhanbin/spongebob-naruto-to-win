import { Component, OnInit, inject } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { ApiService } from '../../core/services/api.service';
import { BlackjackSession, TransactionItem, UserProfile, Wallet } from '../../core/interfaces/api.models';

@Component({
  selector: 'app-cashier-page',
  imports: [FormsModule, RouterLink, DatePipe],
  templateUrl: './cashier.page.html',
  styleUrl: './cashier.page.scss'
})
export class CashierPageComponent implements OnInit {
  private readonly api = inject(ApiService);

  protected profile: UserProfile | null = null;
  protected wallet: Wallet | null = null;
  protected transactions: TransactionItem[] = [];
  protected history: BlackjackSession[] = [];
  protected topUpAmount = '1000.00';
  protected loading = false;
  protected errorMessage = '';
  protected successMessage = '';

  protected get isAuthenticated(): boolean {
    return this.api.isAuthenticated();
  }

  ngOnInit(): void {
    if (this.isAuthenticated) {
      this.loadCashier();
    }
  }

  protected loadCashier(): void {
    this.loading = true;
    this.errorMessage = '';

    forkJoin({
      profile: this.api.getCurrentUser(),
      wallet: this.api.getWallet(),
      transactions: this.api.getTransactions(),
      history: this.api.getBlackjackHistory()
    }).subscribe({
      next: ({ profile, wallet, transactions, history }) => {
        this.profile = profile;
        this.wallet = wallet;
        this.transactions = transactions;
        this.history = history;
        this.loading = false;
      },
      error: (error: Error) => {
        this.errorMessage = error.message;
        this.loading = false;
      }
    });
  }

  protected topUp(): void {
    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.api.topUpWallet(this.topUpAmount).subscribe({
      next: () => {
        this.successMessage = 'Chips added to your wallet.';
        this.loadCashier();
      },
      error: (error: Error) => {
        this.errorMessage = error.message;
        this.loading = false;
      }
    });
  }
}
