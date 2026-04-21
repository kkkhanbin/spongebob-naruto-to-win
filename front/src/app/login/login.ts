import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { ApiService, LoginRequest, RegisterRequest } from '../services/api.service';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {
  loginForm: LoginRequest = { username: '', password: '' };
  registerForm: RegisterRequest = { username: '', email: '', birth_date: null, password: '' };
  activePanel: 'login' | 'register' = 'login';
  loginError = '';
  registerError = '';
  registerSuccess = '';
  isSubmittingLogin = false;
  isSubmittingRegister = false;

  constructor(
    private readonly authService: AuthService,
    private readonly apiService: ApiService,
    private readonly router: Router,
  ) {}

  switchPanel(panel: 'login' | 'register', clearSuccess = true) {
    this.activePanel = panel;
    this.loginError = '';
    this.registerError = '';
    if (clearSuccess) {
      this.registerSuccess = '';
    }
  }

  submitLogin() {
    this.isSubmittingLogin = true;
    this.loginError = '';

    this.authService.login(this.loginForm).subscribe({
      next: (response) => {
        this.authService.setTokens(response);
        this.router.navigate(['/profile']);
      },
      error: (error: Error) => {
        this.loginError = error.message;
        this.isSubmittingLogin = false;
      },
      complete: () => {
        this.isSubmittingLogin = false;
      },
    });
  }

  submitRegister() {
    this.isSubmittingRegister = true;
    this.registerError = '';
    this.registerSuccess = '';

    const payload: RegisterRequest = {
      ...this.registerForm,
      birth_date: this.registerForm.birth_date || null,
    };

    this.apiService.register(payload).subscribe({
      next: () => {
        this.switchPanel('login', false);
        this.registerSuccess = 'Account created';
        this.loginForm.username = this.registerForm.username;
        this.registerForm = { username: '', email: '', birth_date: null, password: '' };
      },
      error: (error: Error) => {
        this.registerError = error.message;
        this.isSubmittingRegister = false;
      },
      complete: () => {
        this.isSubmittingRegister = false;
      },
    });
  }
}
