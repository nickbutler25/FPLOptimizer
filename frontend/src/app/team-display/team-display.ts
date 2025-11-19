import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { Subject, takeUntil, catchError, of, finalize } from 'rxjs';

import { TeamService } from '../services/implementations/team.service';
import { Team, TeamPick } from '../object-interfaces/team.interface';
import { ConfigService } from '../config/config.service';
import { TransferOptimizer } from '../transfer-optimizer/transfer-optimizer';

@Component({
  selector: 'app-team-display',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule, TransferOptimizer],
  providers: [TeamService],
  templateUrl: './team-display.html',
  styleUrl: './team-display.css'
})
export class TeamDisplay implements OnInit, OnDestroy {
  // Form inputs
  teamId: number | null = 1881344;  // Default team ID
  includePicks: boolean = true;

  // State
  isLoading = false;
  error: string | null = null;
  team: Team | null = null;

  // Cleanup
  private destroy$ = new Subject<void>();

  constructor(
    private teamService: TeamService,
    public config: ConfigService
  ) {}

  ngOnInit(): void {
    if (this.config.shouldLogToConsole) {
      console.log('🏆 Team Display component initialized');
    }
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Load team data from API
   */
  loadTeam(): void {
    if (!this.teamId || this.teamId <= 0) {
      this.error = 'Please enter a valid team ID';
      return;
    }

    this.isLoading = true;
    this.error = null;
    this.team = null;

    if (this.config.shouldLogToConsole) {
      console.log(`🔍 Loading team ${this.teamId}...`);
    }

    this.teamService.getTeamById(this.teamId, this.includePicks)
      .pipe(
        takeUntil(this.destroy$),
        finalize(() => {
          this.isLoading = false;
        }),
        catchError(error => {
          this.error = error.message || 'Failed to load team data';
          console.error('❌ Error loading team:', error);
          return of(null);
        })
      )
      .subscribe({
        next: (response) => {
          if (response && response.success) {
            this.team = response.data;
            // Automatically apply optimal team selection
            if (this.team?.picks) {
              this.applyOptimalTeam();
            }
            if (this.config.shouldLogToConsole) {
              console.log('✅ Team loaded successfully:', this.team);
            }
          } else if (response) {
            this.error = response.message || 'Failed to load team';
          }
        }
      });
  }

  /**
   * Clear current team data
   */
  clearTeam(): void {
    this.team = null;
    this.error = null;
    this.teamId = null;
  }

  /**
   * Get manager full name
   */
  get managerName(): string {
    if (!this.team) return '';
    return `${this.team.player_first_name} ${this.team.player_last_name}`;
  }

  /**
   * Get team value in millions
   */
  get teamValueInMillions(): number {
    if (!this.team) return 0;
    return this.team.team_value / 10;
  }

  /**
   * Get bank value in millions
   */
  get bankInMillions(): number {
    if (!this.team) return 0;
    return this.team.bank / 10;
  }

  /**
   * Get current gameweek (FPL API current_event is last completed, so add 1)
   */
  get currentGameweek(): number {
    if (!this.team) return 0;
    return this.team.current_event + 1;
  }

  /**
   * Get starting XI (positions 1-11)
   */
  get startingEleven(): TeamPick[] {
    if (!this.team?.picks) return [];
    return this.team.picks.filter(pick => pick.position <= 11);
  }

  /**
   * Get substitutes (positions 12-15)
   */
  get substitutes(): TeamPick[] {
    if (!this.team?.picks) return [];
    return this.team.picks.filter(pick => pick.position > 11);
  }

  /**
   * Get players by position type for formation display
   */
  get goalkeepers(): TeamPick[] {
    if (!this.team?.picks) return [];
    return this.startingEleven.filter(pick => pick.player_position === 1);
  }

  get defenders(): TeamPick[] {
    if (!this.team?.picks) return [];
    return this.startingEleven.filter(pick => pick.player_position === 2);
  }

  get midfielders(): TeamPick[] {
    if (!this.team?.picks) return [];
    return this.startingEleven.filter(pick => pick.player_position === 3);
  }

  get forwards(): TeamPick[] {
    if (!this.team?.picks) return [];
    return this.startingEleven.filter(pick => pick.player_position === 4);
  }

  /**
   * Get captain
   */
  get captain(): TeamPick | undefined {
    if (!this.team?.picks) return undefined;
    return this.team.picks.find(pick => pick.is_captain);
  }

  /**
   * Get vice captain
   */
  get viceCaptain(): TeamPick | undefined {
    if (!this.team?.picks) return undefined;
    return this.team.picks.find(pick => pick.is_vice_captain);
  }

  /**
   * Format number with commas
   */
  formatNumber(num: number): string {
    return num.toLocaleString('en-GB');
  }

  /**
   * Get multiplier text
   */
  getMultiplierText(pick: TeamPick): string {
    if (pick.is_captain) return '(C)';
    if (pick.is_vice_captain) return '(V)';
    return '';
  }

  /**
   * Get position label
   */
  getPositionLabel(position: number): string {
    if (position <= 11) return `Starting ${position}`;
    return `Sub ${position - 11}`;
  }

  /**
   * Get player display name
   */
  getPlayerDisplayName(pick: TeamPick): string {
    // Use player_name if available (e.g., "Salah")
    if (pick.player_name) {
      return pick.player_name;
    }

    // Fallback to full name if available
    if (pick.player_first_name && pick.player_second_name) {
      return `${pick.player_first_name} ${pick.player_second_name}`;
    }

    // Fallback to player ID
    return `Player #${pick.element}`;
  }

  /**
   * Get player selling price in millions (with FPL profit rules)
   */
  getPlayerCost(pick: TeamPick): string {
    if (!pick.player_cost) {
      return '';
    }

    // If we don't have purchase price, show current price
    if (!pick.purchase_price) {
      return `£${(pick.player_cost / 10).toFixed(1)}m`;
    }

    const currentPrice = pick.player_cost;
    const purchasePrice = pick.purchase_price;

    let sellingPrice: number;

    if (currentPrice >= purchasePrice) {
      // Price increased: gain half the profit (rounded down)
      const profit = currentPrice - purchasePrice;
      const profitGain = Math.floor(profit / 2);
      sellingPrice = purchasePrice + profitGain;
    } else {
      // Price decreased: take the full loss
      sellingPrice = currentPrice;
    }

    return `£${(sellingPrice / 10).toFixed(1)}m`;
  }

  /**
   * Get player display with cost
   */
  getPlayerDisplayWithCost(pick: TeamPick): string {
    const name = this.getPlayerDisplayName(pick);
    const cost = this.getPlayerCost(pick);
    return cost ? `${name} (${cost})` : name;
  }

  /**
   * Get team badge URL for a player
   */
  getTeamBadgeUrl(pick: TeamPick): string {
    if (pick.player_team_code) {
      // FPL uses team codes for badge images
      return `https://resources.premierleague.com/premierleague/badges/t${pick.player_team_code}.png`;
    }
    return '';
  }

  /**
   * Get team short name for display
   */
  getTeamShortName(pick: TeamPick): string {
    return pick.player_team_short_name || '';
  }

  /**
   * Get transfers made in last completed gameweek
   */
  get transfersMadeLastGameweek(): number {
    if (this.team?.transfers) {
      const transfers = this.team.transfers as any;
      return transfers.made ?? 0;
    }
    return 0;
  }

  /**
   * Get available free transfers for next gameweek
   */
  get freeTransfersAvailable(): number {
    if (this.team?.transfers) {
      const transfers = this.team.transfers as any;
      return transfers.free_transfers ?? 1;
    }
    return 1;
  }

  /**
   * Get bench number for substitute (0-indexed, excluding GK)
   */
  getBenchNumber(pick: TeamPick): number {
    return pick.position - 12;
  }

  /**
   * Check if substitute is a goalkeeper
   */
  isSubstituteGoalkeeper(pick: TeamPick): boolean {
    return pick.player_position === 1;
  }

  /**
   * Get expected points for a player
   * For now, returns random value between 0-6 if not available from API
   */
  getExpectedPoints(pick: TeamPick): number {
    if (pick.expected_points !== undefined && pick.expected_points !== null) {
      return pick.expected_points;
    }
    // Temporary: return random value between 0-6
    return Math.random() * 6;
  }

  /**
   * Format expected points for display
   */
  formatExpectedPoints(pick: TeamPick): string {
    const points = this.getExpectedPoints(pick);
    return points.toFixed(1);
  }

  /**
   * Get optimal starting XI based on expected points
   * Formation constraints: 1 GK, 3-5 DEF, 2-5 MID, 1-3 FWD
   */
  getOptimalStartingXI(): TeamPick[] {
    if (!this.team?.picks) return [];

    // Group players by position
    const gks = this.team.picks.filter(p => p.player_position === 1);
    const defs = this.team.picks.filter(p => p.player_position === 2);
    const mids = this.team.picks.filter(p => p.player_position === 3);
    const fwds = this.team.picks.filter(p => p.player_position === 4);

    // Sort each position by expected points (descending)
    const sortByPoints = (a: TeamPick, b: TeamPick) =>
      this.getExpectedPoints(b) - this.getExpectedPoints(a);

    gks.sort(sortByPoints);
    defs.sort(sortByPoints);
    mids.sort(sortByPoints);
    fwds.sort(sortByPoints);

    // Try all valid formations and find the one with max points
    let bestFormation: TeamPick[] = [];
    let maxPoints = -1;

    // Valid formations: [DEF, MID, FWD] (GK is always 1)
    // Each formation must have exactly 10 outfield players (3-5 DEF, 2-5 MID, 1-3 FWD)
    const validFormations = [
      [3, 4, 3], [3, 5, 2],
      [4, 3, 3], [4, 4, 2], [4, 5, 1],
      [5, 3, 2], [5, 4, 1]
    ];

    for (const [numDef, numMid, numFwd] of validFormations) {
      // Check if we have enough players
      if (defs.length < numDef || mids.length < numMid || fwds.length < numFwd || gks.length < 1) {
        continue;
      }

      // Build team
      const formation = [
        gks[0],
        ...defs.slice(0, numDef),
        ...mids.slice(0, numMid),
        ...fwds.slice(0, numFwd)
      ];

      // Calculate total expected points
      const totalPoints = formation.reduce((sum, pick) =>
        sum + this.getExpectedPoints(pick), 0);

      if (totalPoints > maxPoints) {
        maxPoints = totalPoints;
        bestFormation = formation;
      }
    }

    return bestFormation;
  }

  /**
   * Get total expected points for optimal XI
   */
  get optimalXITotalPoints(): number {
    const optimalXI = this.getOptimalStartingXI();
    return optimalXI.reduce((sum, pick) => sum + this.getExpectedPoints(pick), 0);
  }

  /**
   * Get formation string for optimal XI (e.g., "3-4-3")
   */
  get optimalFormation(): string {
    const optimalXI = this.getOptimalStartingXI();
    if (optimalXI.length === 0) return '';

    const defs = optimalXI.filter(p => p.player_position === 2).length;
    const mids = optimalXI.filter(p => p.player_position === 3).length;
    const fwds = optimalXI.filter(p => p.player_position === 4).length;

    return `${defs}-${mids}-${fwds}`;
  }

  /**
   * Check if a player is in the optimal starting XI
   */
  isInOptimalXI(pick: TeamPick): boolean {
    const optimalXI = this.getOptimalStartingXI();
    return optimalXI.some(p => p.element === pick.element);
  }

  /**
   * Apply optimal team selection - reorder picks to match optimal XI
   */
  applyOptimalTeam(): void {
    if (!this.team?.picks) return;

    const optimalXI = this.getOptimalStartingXI();
    if (optimalXI.length === 0) return;

    // Get all picks
    const allPicks = [...this.team.picks];

    // Create set of optimal player IDs for quick lookup
    const optimalIds = new Set(optimalXI.map(p => p.element));

    // Separate optimal and bench players
    const optimalPlayers = allPicks.filter(p => optimalIds.has(p.element));
    const benchPlayers = allPicks.filter(p => !optimalIds.has(p.element));

    // Sort optimal players by position type (GK, DEF, MID, FWD) to maintain formation order
    optimalPlayers.sort((a, b) => {
      if (a.player_position !== b.player_position) {
        return (a.player_position || 0) - (b.player_position || 0);
      }
      // Within same position, sort by expected points (descending)
      return this.getExpectedPoints(b) - this.getExpectedPoints(a);
    });

    // Sort bench players by expected points (descending) with GK first
    benchPlayers.sort((a, b) => {
      // Goalkeepers always go first on bench (position 12 = bench number 0)
      if (a.player_position === 1 && b.player_position !== 1) return -1;
      if (b.player_position === 1 && a.player_position !== 1) return 1;
      // Otherwise sort by expected points (descending)
      return this.getExpectedPoints(b) - this.getExpectedPoints(a);
    });

    // Create new picks array with updated positions
    const newPicks: TeamPick[] = [];

    // Find the top 2 players by expected points for captaincy
    const allPlayersSortedByPoints = [...optimalPlayers].sort((a, b) =>
      this.getExpectedPoints(b) - this.getExpectedPoints(a)
    );
    const captainId = allPlayersSortedByPoints[0]?.element;
    const viceCaptainId = allPlayersSortedByPoints[1]?.element;

    // Assign positions 1-11 to optimal XI with captaincy
    optimalPlayers.forEach((pick, index) => {
      newPicks.push({
        ...pick,
        position: index + 1,
        is_captain: pick.element === captainId,
        is_vice_captain: pick.element === viceCaptainId,
        multiplier: pick.element === captainId ? 2 : (pick.element === viceCaptainId ? 1 : 1)
      });
    });

    // Assign positions 12-15 to bench (no captaincy on bench)
    benchPlayers.forEach((pick, index) => {
      newPicks.push({
        ...pick,
        position: 12 + index,
        is_captain: false,
        is_vice_captain: false,
        multiplier: 0
      });
    });

    // Update team picks - avoid assigning to a readonly property by mutating the existing array reference when possible
    if (Array.isArray(this.team.picks) && typeof (this.team.picks as any).splice === 'function') {
      // Replace contents while keeping the same array reference (safe when picks is a normal array)
      this.team.picks.splice(0, this.team.picks.length, ...newPicks);
    } else {
      // Fallback: replace the whole team object (this assigns the team reference, not the readonly property directly)
      this.team = { ...this.team, picks: newPicks } as Team;
    }

    if (this.config.shouldLogToConsole) {
      console.log('✅ Applied optimal team selection');
      console.log(`Formation: ${this.optimalFormation}`);
      console.log(`Total xP: ${this.optimalXITotalPoints.toFixed(1)}`);
    }
  }

  /**
   * Track picks by position
   */
  trackByPosition(index: number, pick: TeamPick): number {
    return pick.position;
  }

  /**
   * Handle keyboard shortcuts
   */
  onKeyPress(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !this.isLoading) {
      this.loadTeam();
    }
  }

  /**
   * Get player shirt URL from FPL resources
   */
  getPlayerShirtUrl(pick: TeamPick): string {
    if (pick.player_team_code) {
      // FPL uses team codes for shirt images
      // Goalkeepers (position 1) use a different shirt type
      const shirtType = pick.player_position === 1 ? 'shirt_' : 'shirt_';
      const suffix = pick.player_position === 1 ? '-66' : '-110';

      // Format:
      // Outfield: https://fantasy.premierleague.com/dist/img/shirts/standard/shirt_{TEAM_CODE}-110.png
      // Goalkeeper: https://fantasy.premierleague.com/dist/img/shirts/standard/shirt_{TEAM_CODE}_1-66.png
      if (pick.player_position === 1) {
        return `https://fantasy.premierleague.com/dist/img/shirts/standard/shirt_${pick.player_team_code}_1${suffix}.png`;
      } else {
        return `https://fantasy.premierleague.com/dist/img/shirts/standard/shirt_${pick.player_team_code}${suffix}.png`;
      }
    }
    return '';
  }

  /**
   * Get player cost value (raw number)
   */
  getPlayerCostValue(pick: TeamPick): number {
    if (!pick.player_cost) {
      return 0;
    }

    // If we don't have purchase price, return current price
    if (!pick.purchase_price) {
      return pick.player_cost;
    }

    const currentPrice = pick.player_cost;
    const purchasePrice = pick.purchase_price;

    let sellingPrice: number;

    if (currentPrice >= purchasePrice) {
      // Price increased: gain half the profit (rounded down)
      const profit = currentPrice - purchasePrice;
      const profitGain = Math.floor(profit / 2);
      sellingPrice = purchasePrice + profitGain;
    } else {
      // Price decreased: take the full loss
      sellingPrice = currentPrice;
    }

    return sellingPrice;
  }

  /**
   * Get fixture display string (e.g., "WHU (H)" or "AVL (A)")
   */
  getFixtureDisplay(pick: TeamPick): string {
    // For now, return placeholder
    // TODO: Implement actual fixture lookup from API
    const homeAway = Math.random() > 0.5 ? 'H' : 'A';
    return homeAway;
  }

  /**
   * Get position abbreviation for a player
   */
  getPositionAbbreviation(pick: TeamPick): string {
    switch (pick.player_position) {
      case 1: return 'GKP';
      case 2: return 'DEF';
      case 3: return 'MID';
      case 4: return 'FWD';
      default: return '';
    }
  }
}
