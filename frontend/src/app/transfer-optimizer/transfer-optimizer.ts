// Transfer optimizer component
import { Component, Input, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subject, takeUntil } from 'rxjs';

import { TeamService } from '../services/implementations/team.service';
import { TransferPlanData, WeeklyTransferSolution } from '../object-interfaces/team.interface';

@Component({
  selector: 'app-transfer-optimizer',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './transfer-optimizer.html',
  styleUrl: './transfer-optimizer.css'
})
export class TransferOptimizer implements OnDestroy {
  @Input() teamId!: number;

  // Solver parameters
  numGameweeks: number = 5;
  freeTransfers: number = 3;
  discountFactor: number = 0.9;

  // State
  isLoading = false;
  error: string | null = null;
  transferPlan: TransferPlanData | null = null;
  showSettings = false;

  // Cleanup
  private destroy$ = new Subject<void>();

  constructor(private teamService: TeamService) {}

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Generate transfer plan
   */
  generatePlan(): void {
    if (!this.teamId) {
      this.error = 'Team ID is required';
      return;
    }

    this.isLoading = true;
    this.error = null;
    this.transferPlan = null;

    this.teamService
      .generateTransferPlan(
        this.teamId,
        this.numGameweeks,
        this.freeTransfers,
        this.discountFactor
      )
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.isLoading = false;
          if (response.success && response.data) {
            this.transferPlan = response.data;
          } else {
            this.error = response.message || 'Failed to generate transfer plan';
          }
        },
        error: (err) => {
          this.isLoading = false;
          this.error = err.message || 'Failed to generate transfer plan';
        }
      });
  }

  /**
   * Clear the current plan
   */
  clearPlan(): void {
    this.transferPlan = null;
    this.error = null;
  }

  /**
   * Toggle settings panel
   */
  toggleSettings(): void {
    this.showSettings = !this.showSettings;
  }

  /**
   * Get gameweek label
   */
  getGameweekLabel(solution: WeeklyTransferSolution): string {
    if (!this.transferPlan) {
      return `GW ${solution.gameweek}`;
    }
    const actualGameweek = this.transferPlan.current_gameweek + solution.gameweek;
    return `GW ${actualGameweek}`;
  }

  /**
   * Check if a gameweek has transfers
   */
  hasTransfers(solution: WeeklyTransferSolution): boolean {
    return solution.transfers_in.length > 0;
  }

  /**
   * Format number with commas
   */
  formatNumber(num: number): string {
    return num.toFixed(1);
  }
}
