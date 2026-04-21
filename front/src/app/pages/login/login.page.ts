import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiService } from '../../core/services/api.service';

@Component({
  selector: 'app-login-page',
  imports: [FormsModule, RouterLink],
  templateUrl: './login.page.html',
  styleUrl: './login.page.scss'
})
export class LoginPageComponent {
  private readonly api = inject(ApiService);
  private readonly router = inject(Router);

  protected username = '';
  protected password = '';
  protected errorMessage = '';
  protected successMessage = '';
  protected loading = false;

  protected login(): void {
    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.api.login({ username: this.username, password: this.password }).subscribe({
      next: (tokens) => {
        this.api.setTokens(tokens);
        this.api.hydrateSession();
        this.successMessage = 'Login successful.';
        this.loading = false;
        void this.router.navigateByUrl('/blackjack');
      },
      error: (error: Error) => {
        this.errorMessage = error.message;
        this.loading = false;
      }
    });
  }
}
