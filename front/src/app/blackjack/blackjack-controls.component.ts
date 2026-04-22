import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-blackjack-controls',
  standalone: true,
  imports: [CommonModule],
  template: `
    <section class="card controls-panel">
      <div class="controls-panel__header">
        <div>
          <p class="eyebrow">Decision Phase</p>
          <h2>Choose the Next Move</h2>
        </div>
        <span class="controls-panel__status">{{ statusLabel }}</span>
      </div>

      <div class="controls-grid">
        <button class="action action--primary" type="button" (click)="hit.emit()" [disabled]="disabled || !canHit">
          Hit
        </button>
        <button class="action" type="button" (click)="stand.emit()" [disabled]="disabled || !canStand">
          Stand
        </button>
        <button class="action" type="button" (click)="double.emit()" [disabled]="disabled || !canDouble">
          Double
        </button>
        <button class="action" type="button" (click)="split.emit()" [disabled]="disabled || !canSplit">
          Split
        </button>
      </div>
    </section>
  `,
  styles: `
    .controls-panel {
      padding: 1.4rem;
      display: grid;
      gap: 1rem;
    }

    .controls-panel__header {
      display: flex;
      justify-content: space-between;
      gap: 1rem;
      align-items: center;
    }

    .controls-panel__header h2 {
      margin: 0.35rem 0 0;
    }

    .controls-panel__status {
      padding: 0.45rem 0.75rem;
      border-radius: 999px;
      color: #c8fbff;
      background: rgba(103, 232, 249, 0.12);
      border: 1px solid rgba(103, 232, 249, 0.18);
      font-size: 0.78rem;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    .controls-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 0.85rem;
    }

    .action {
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 1rem;
      padding: 0.95rem 1rem;
      font-weight: 900;
      color: var(--text);
      background: rgba(255, 255, 255, 0.05);
      cursor: pointer;
    }

    .action--primary {
      color: #160b14;
      background: linear-gradient(135deg, #ffe066, #ff8c42 58%, #ff4d6d);
      border-color: transparent;
    }

    .action:disabled {
      cursor: not-allowed;
      opacity: 0.42;
    }

    @media (max-width: 760px) {
      .controls-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
    }
  `,
})
export class BlackjackControlsComponent {
  @Input() disabled = false;
  @Input() canHit = false;
  @Input() canStand = false;
  @Input() canDouble = false;
  @Input() canSplit = false;
  @Input() statusLabel = 'Waiting';

  @Output() readonly hit = new EventEmitter<void>();
  @Output() readonly stand = new EventEmitter<void>();
  @Output() readonly double = new EventEmitter<void>();
  @Output() readonly split = new EventEmitter<void>();
}
