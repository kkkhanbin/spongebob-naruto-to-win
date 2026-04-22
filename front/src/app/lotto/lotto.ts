import { ChangeDetectorRef, Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { finalize } from 'rxjs/operators';

import { ApiService, LottoBet, LottoResult } from '../services/api.service';

@Component({
  selector: 'app-lotto',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './lotto.html',
  styleUrl: './lotto.scss',
})
export class Lotto {
  bet: LottoBet = { numbers: [], amount: 25 };
  result: LottoResult | null = null;
  drawing = false;
  errorMessage = '';
  readonly numbers = Array.from({ length: 49 }, (_, index) => index + 1);

  constructor(
    private readonly apiService: ApiService,
    private readonly cdr: ChangeDetectorRef,
  ) {}

  toggleNumber(num: number) {
    if (this.bet.numbers.includes(num)) {
      this.bet.numbers = this.bet.numbers.filter((value) => value !== num);
      return;
    }

    if (this.bet.numbers.length === 6) {
      this.errorMessage = 'You can only choose 6 numbers.';
      return;
    }

    this.errorMessage = '';
    this.bet.numbers = [...this.bet.numbers, num].sort((a, b) => a - b);
  }

  quickPick() {
    const selected = new Set<number>();
    while (selected.size < 6) {
      selected.add(Math.floor(Math.random() * 49) + 1);
    }
    this.bet.numbers = [...selected].sort((a, b) => a - b);
    this.errorMessage = '';
  }

  play() {
    if (this.bet.numbers.length !== 6) {
      this.errorMessage = 'Select exactly 6 numbers.';
      return;
    }

    this.drawing = true;
    this.errorMessage = '';
    this.result = null;

    this.apiService
      .playLotto(this.bet)
      .pipe(
        finalize(() => {
          this.drawing = false;
          this.cdr.detectChanges();
        }),
      )
      .subscribe({
        next: (res) => {
          this.result = res;
          this.cdr.detectChanges();
        },
        error: (error: Error) => {
          this.errorMessage = error.message;
          this.cdr.detectChanges();
        },
      });
  }
}
