import { Routes } from '@angular/router';

import { Home } from './home/home';
import { Login } from './login/login';
import { Lotto } from './lotto/lotto';
import { Profile } from './profile/profile';
import { Roulette } from './roulette/roulette';
import { authGuard } from './services/auth.guard';

export const routes: Routes = [
  { path: '', component: Home },
  { path: 'login', component: Login },
  { path: 'profile', component: Profile, canActivate: [authGuard] },
  { path: 'roulette', component: Roulette, canActivate: [authGuard] },
  { path: 'lotto', component: Lotto, canActivate: [authGuard] },
  { path: '**', redirectTo: '' },
];
