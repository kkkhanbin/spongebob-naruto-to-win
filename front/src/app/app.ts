import { Component, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { ApiService } from './core/services/api.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly api = inject(ApiService);
  private readonly router = inject(Router);

  protected readonly navigation = [
    { label: 'Lobby', path: '/' },
    { label: 'Blackjack', path: '/blackjack' },
    { label: 'Cashier', path: '/cashier' }
  ];

  constructor() {
    this.api.hydrateSession();
  }

  protected logout(): void {
    this.api.clearTokens();
    void this.router.navigateByUrl('/login');
  }
}
