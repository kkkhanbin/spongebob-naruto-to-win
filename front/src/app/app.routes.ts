import { Routes } from '@angular/router';
import { HomePageComponent } from './pages/home/home.page';
import { LoginPageComponent } from './pages/login/login.page';
import { RegisterPageComponent } from './pages/register/register.page';
import { BlackjackPageComponent } from './pages/blackjack/blackjack.page';
import { CashierPageComponent } from './pages/cashier/cashier.page';

export const routes: Routes = [
  { path: '', component: HomePageComponent, title: 'Lobby' },
  { path: 'login', component: LoginPageComponent, title: 'Sign In' },
  { path: 'register', component: RegisterPageComponent, title: 'Create Account' },
  { path: 'blackjack', component: BlackjackPageComponent, title: 'Blackjack' },
  { path: 'cashier', component: CashierPageComponent, title: 'Cashier' },
  { path: '**', redirectTo: '' }
];
