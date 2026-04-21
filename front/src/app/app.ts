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
  protected readonly title = signal('Lucky Orbit Casino');

  navItems = [
  { path: '/', label: 'Lobby' },
  { path: '/roulette', label: 'Roulette' },
  { path: '/lotto', label: 'Lotto' },
  { path: '/profile', label: 'Wallet' }
];

  constructor(public readonly authService: AuthService) {}

  logout() {
    this.authService.logout();
  }
}
