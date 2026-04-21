import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiService } from '../../core/services/api.service';

@Component({
  selector: 'app-register-page',
  imports: [FormsModule, RouterLink],
  templateUrl: './register.page.html',
  styleUrl: './register.page.scss'
})
export class RegisterPageComponent {
  private readonly api = inject(ApiService);
  private readonly router = inject(Router);

  protected username = '';
  protected email = '';
  protected password = '';
  protected confirmPassword = '';
  protected errorMessage = '';
  protected successMessage = '';
  protected loading = false;

  protected register(): void {
    if (this.password !== this.confirmPassword) {
      this.errorMessage = 'Passwords do not match.';
      this.successMessage = '';
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.api
      .register({
        username: this.username,
        email: this.email,
        password: this.password
      })
      .subscribe({
        next: () => {
          this.successMessage = 'Account created successfully.';
          this.loading = false;
          void this.router.navigateByUrl('/login');
        },
        error: (error: Error) => {
          this.errorMessage = error.message;
          this.loading = false;
        }
      });
  }
}
