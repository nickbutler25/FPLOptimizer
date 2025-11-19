import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { Subject, takeUntil, catchError, of, finalize, forkJoin } from 'rxjs';

import { PlayerWithFixtures } from '../object-interfaces/player-with-fixtures.interface';
import { Team, TeamResponse } from '../object-interfaces/team.interface';
import { ConfigService } from '../config/config.service';
import { HttpClient, HttpHeaders } from '@angular/common/http';

interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

@Component({
  selector: 'app-transfer-planner',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './transfer-planner.html',
  styleUrl: './transfer-planner.css'
})
export class TransferPlanner implements OnInit, OnDestroy {
  // Filter inputs
  selectedPosition: string = '';
  selectedTeam: number | null = null;
  minCost: number | null = null;
  maxCost: number | null = null;
  searchText: string = '';
  teamId: number = 1881344; // Default team ID - user can change this

  // Sorting
  sortColumn: string = 'expected_points_total';
  sortDirection: 'asc' | 'desc' = 'desc';

  // State
  isLoading = false;
  error: string | null = null;
  players: PlayerWithFixtures[] = [];
  filteredPlayers: PlayerWithFixtures[] = [];
  myTeam: Team | null = null;
  mySquadPlayerIds: Set<number> = new Set();

  // Cleanup
  private destroy$ = new Subject<void>();
  private apiKey = 'dev-api-key-change-in-production';

  // Position options
  positions = [
    { value: '', label: 'All Positions' },
    { value: 'Goalkeeper', label: 'Goalkeeper' },
    { value: 'Defender', label: 'Defender' },
    { value: 'Midfielder', label: 'Midfielder' },
    { value: 'Forward', label: 'Forward' }
  ];

  constructor(
    private http: HttpClient,
    public config: ConfigService
  ) {}

  ngOnInit(): void {
    // Load both team and players
    this.loadTeamAndPlayers();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Load team and players together
   */
  loadTeamAndPlayers(): void {
    this.isLoading = true;
    this.error = null;

    const headers = new HttpHeaders({
      'X-API-Key': this.apiKey
    });

    // Load user's team first to get squad player IDs
    const teamUrl = `${this.config.apiBaseUrl}/teams/${this.teamId}?include_picks=true`;

    this.http.get<ApiResponse<Team>>(teamUrl, { headers })
      .pipe(
        takeUntil(this.destroy$),
        catchError(error => {
          console.warn('Failed to load team data:', error);
          // Continue without team data - show all players
          return of(null);
        })
      )
      .subscribe({
        next: (teamResponse) => {
          if (teamResponse && teamResponse.success && teamResponse.data.picks) {
            this.myTeam = teamResponse.data;
            // Build set of player IDs in user's squad
            this.mySquadPlayerIds = new Set(
              teamResponse.data.picks.map(pick => pick.element)
            );
          }
          // Now load players
          this.loadPlayers();
        }
      });
  }

  /**
   * Load all players with fixture data
   */
  loadPlayers(): void {
    const headers = new HttpHeaders({
      'X-API-Key': this.apiKey
    });

    let url = `${this.config.apiBaseUrl}/players/fixtures/upcoming`;
    const params: string[] = [];

    if (this.selectedPosition) {
      params.push(`position=${encodeURIComponent(this.selectedPosition)}`);
    }
    if (this.selectedTeam) {
      params.push(`team_id=${this.selectedTeam}`);
    }
    if (this.minCost !== null && this.minCost > 0) {
      params.push(`min_cost=${this.minCost}`);
    }
    if (this.maxCost !== null && this.maxCost > 0) {
      params.push(`max_cost=${this.maxCost}`);
    }

    if (params.length > 0) {
      url += '?' + params.join('&');
    }

    this.http.get<ApiResponse<PlayerWithFixtures[]>>(url, { headers })
      .pipe(
        takeUntil(this.destroy$),
        finalize(() => {
          this.isLoading = false;
        }),
        catchError(error => {
          this.error = error.message || 'Failed to load players';
          console.error('Error loading players:', error);
          return of(null);
        })
      )
      .subscribe({
        next: (response) => {
          if (response && response.success) {
            // Show all players (including those in squad)
            this.players = response.data;
            this.applyFiltersAndSort();
          } else if (response) {
            this.error = response.message || 'Failed to load players';
          }
        }
      });
  }

  /**
   * Apply filters and sorting to players list
   */
  applyFiltersAndSort(): void {
    let filtered = [...this.players];

    // Apply search filter
    if (this.searchText) {
      const search = this.searchText.toLowerCase();
      filtered = filtered.filter(p =>
        p.web_name.toLowerCase().includes(search) ||
        p.first_name.toLowerCase().includes(search) ||
        p.second_name.toLowerCase().includes(search) ||
        (p.team_name && p.team_name.toLowerCase().includes(search))
      );
    }

    // Sort
    filtered.sort((a, b) => {
      let aVal: any;
      let bVal: any;

      switch (this.sortColumn) {
        case 'web_name':
          aVal = a.web_name;
          bVal = b.web_name;
          break;
        case 'position':
          aVal = a.element_type;
          bVal = b.element_type;
          break;
        case 'team_name':
          aVal = a.team_name || '';
          bVal = b.team_name || '';
          break;
        case 'now_cost':
          aVal = a.now_cost;
          bVal = b.now_cost;
          break;
        case 'form':
          aVal = parseFloat(a.form);
          bVal = parseFloat(b.form);
          break;
        case 'total_points':
          aVal = a.total_points;
          bVal = b.total_points;
          break;
        case 'expected_points_gw1':
          aVal = a.expected_points_gw1;
          bVal = b.expected_points_gw1;
          break;
        case 'expected_points_total':
          aVal = a.expected_points_total;
          bVal = b.expected_points_total;
          break;
        default:
          aVal = a.expected_points_total;
          bVal = b.expected_points_total;
      }

      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return this.sortDirection === 'asc'
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      } else {
        return this.sortDirection === 'asc'
          ? aVal - bVal
          : bVal - aVal;
      }
    });

    this.filteredPlayers = filtered;
  }

  /**
   * Sort by column
   */
  sortBy(column: string): void {
    if (this.sortColumn === column) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortColumn = column;
      this.sortDirection = 'desc';
    }
    this.applyFiltersAndSort();
  }

  /**
   * Get sort icon for column
   */
  getSortIcon(column: string): string {
    if (this.sortColumn !== column) return '';
    return this.sortDirection === 'asc' ? '↑' : '↓';
  }

  /**
   * Get player cost in millions
   */
  getPlayerCost(player: PlayerWithFixtures): string {
    return `£${(player.now_cost / 10).toFixed(1)}m`;
  }

  /**
   * Get position name
   */
  getPositionName(elementType: number): string {
    switch (elementType) {
      case 1: return 'GK';
      case 2: return 'DEF';
      case 3: return 'MID';
      case 4: return 'FWD';
      default: return '';
    }
  }

  /**
   * Get position badge class
   */
  getPositionClass(elementType: number): string {
    switch (elementType) {
      case 1: return 'position-gk';
      case 2: return 'position-def';
      case 3: return 'position-mid';
      case 4: return 'position-fwd';
      default: return '';
    }
  }

  /**
   * Handle search text change
   */
  onSearchChange(): void {
    this.applyFiltersAndSort();
  }

  /**
   * Clear all filters
   */
  clearFilters(): void {
    this.selectedPosition = '';
    this.selectedTeam = null;
    this.minCost = null;
    this.maxCost = null;
    this.searchText = '';
    this.loadTeamAndPlayers();
  }

  /**
   * Apply filters (reload data from API)
   */
  applyFilters(): void {
    this.loadTeamAndPlayers();
  }
}