import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { ApiService } from '../../core/services/api.service';
import { Wallet } from '../../core/interfaces/api.models';

@Component({
  selector: 'app-dashboard-page',
  templateUrl: './dashboard.page.html',
  styleUrl: './dashboard.page.scss'
})
export class DashboardPageComponent {
  private readonly api = inject(ApiService);
  private readonly router = inject(Router);

  protected wallet: Wallet | null = null;
  protected errorMessage = '';
  protected successMessage = '';
  protected loading = false;

  protected readonly requestButtons = [
    {
      label: 'Load wallet',
      description: 'Protected GET /api/wallet/ request.'
    },
    {
      label: 'Refresh wallet',
      description: 'Another click event that triggers the same protected API.'
    }
  ];

  protected get hasToken(): boolean {
    return this.api.isAuthenticated();
  }

  protected loadWallet(source: string): void {
    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.api.getWallet().subscribe({
      next: (wallet) => {
        this.wallet = wallet;
        this.successMessage = `${source} completed successfully.`;
        this.loading = false;
      },
      error: (error: Error) => {
        this.wallet = null;
        this.errorMessage = error.message;
        this.loading = false;
      }
    });
  }

  protected logout(): void {
    this.api.clearTokens();
    this.wallet = null;
    this.successMessage = 'You have been logged out locally.';
    this.errorMessage = '';
    void this.router.navigateByUrl('/login');
  }
}
