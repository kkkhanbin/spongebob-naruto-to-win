import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  protected readonly title = signal('Spongebob Naruto to Win');

  headerLinks = [
    { path: '/', label: 'Lobby' },
    { path: '/profile', label: 'Profile' },
  ];

  promoStats = [
    { value: '$1.24M', label: 'Live Jackpot' },
    { value: '15%', label: 'VIP Cashback' },
    { value: '24/7', label: 'Host Desk' },
  ];

  constructor(public readonly authService: AuthService) {}

  logout() {
    this.authService.logout();
  }
}
