import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-home-page',
  imports: [RouterLink],
  templateUrl: './home.page.html',
  styleUrl: './home.page.scss'
})
export class HomePageComponent {
  protected readonly featuredGames = [
    {
      name: 'Royal Blackjack',
      accent: 'Live now',
      text: 'Server-shuffled cards, player actions in real time and seed-based fairness at the end of every hand.',
      route: '/blackjack'
    },
    {
      name: 'High Roller Cashier',
      accent: 'Wallet',
      text: 'Manage your balance, claim more chips and review every wager and payout in one place.',
      route: '/cashier'
    },
    {
      name: 'Player Lounge',
      accent: 'Account',
      text: 'Create your account, sign in instantly and keep your casino history attached to one profile.',
      route: '/register'
    }
  ];

  protected readonly highlights = [
    'Private wallet with a visible balance ledger',
    'Full blackjack hand history with payouts and outcomes',
    'Provably fair flow with server seed hash and reveal',
    'Responsive layout for desktop and mobile sessions'
  ];
}
