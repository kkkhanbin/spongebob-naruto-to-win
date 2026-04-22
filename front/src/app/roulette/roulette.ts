import { ChangeDetectorRef, Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { finalize } from 'rxjs/operators';

import { ApiService, RouletteBet, RouletteResult } from '../services/api.service';

@Component({
  selector: 'app-roulette',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './roulette.html',
  styleUrl: './roulette.scss',
})
export class Roulette {
  bet: RouletteBet = { bet_type: 'red', amount: 50 };
  result: RouletteResult | null = null;
  spinning = false;
  errorMessage = '';

  readonly betTypes: Array<RouletteBet['bet_type']> = ['red', 'black', 'even', 'odd'];

  constructor(
    private readonly apiService: ApiService,
    private readonly cdr: ChangeDetectorRef,
  ) {}

  play() {
    this.spinning = true;
    this.errorMessage = '';
    this.result = null;

    this.apiService
      .playRoulette(this.bet)
      .pipe(
        finalize(() => {
          this.spinning = false;
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
