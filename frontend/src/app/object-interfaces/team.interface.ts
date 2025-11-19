// Team interfaces matching backend API

export interface TeamPick {
  readonly element: number;  // Player ID
  readonly position: number; // Position in team (1-15)
  readonly multiplier: number; // Point multiplier (0=bench, 1=playing, 2=captain, 3=vice)
  readonly is_captain: boolean;
  readonly is_vice_captain: boolean;
  readonly player_name?: string;  // Player display name (e.g., 'Salah')
  readonly player_first_name?: string;
  readonly player_second_name?: string;
  readonly player_team?: number;  // Premier League team ID
  readonly player_team_name?: string;  // Team name (e.g., 'Liverpool')
  readonly player_team_short_name?: string;  // Team short name (e.g., 'LIV')
  readonly player_team_code?: number;  // Team code for badge URL
  readonly player_position?: number;  // Position type (1=GK, 2=DEF, 3=MID, 4=FWD)
  readonly player_cost?: number;  // Player current cost in £0.1m units
  readonly purchase_price?: number;  // Player purchase price in £0.1m units
  readonly expected_points?: number;  // Expected points for next gameweek
}

export interface Team {
  readonly id: number;
  readonly name: string;
  readonly player_first_name: string;
  readonly player_last_name: string;
  readonly started_event: number;
  readonly summary_overall_points: number;
  readonly summary_overall_rank: number;
  readonly summary_event_points: number;
  readonly summary_event_rank: number;
  readonly current_event: number;
  readonly total_transfers: number;
  readonly bank: number; // in £0.1m units
  readonly team_value: number; // in £0.1m units
  readonly transfers?: {
    limit: number | null;
    cost: number;
    status: string;
    made: number;
    bank: number;
    value: number;
  };
  readonly picks?: TeamPick[];
}

export interface TeamResponse {
  readonly success: boolean;
  readonly message: string;
  readonly data: Team;
}

export interface TeamSummary {
  readonly team_id: number;
  readonly team_name: string;
  readonly manager_name: string;
  readonly overall_points: number;
  readonly overall_rank: number;
  readonly gameweek_points: number;
  readonly gameweek_rank: number;
  readonly team_value: number; // in millions
  readonly bank: number; // in millions
  readonly total_transfers: number;
}

export interface TeamSummaryResponse {
  readonly success: boolean;
  readonly message: string;
  readonly data: TeamSummary;
}

export interface TransferRecommendation {
  readonly player_id: number;
  readonly player_name: string;
  readonly position?: string;
  readonly cost?: number;
}

export interface WeeklyTransferSolution {
  readonly gameweek: number;
  readonly transfers_in: TransferRecommendation[];
  readonly transfers_out: TransferRecommendation[];
  readonly expected_points: number;
  readonly transfer_cost: number;
  readonly free_transfers_used: number;
  readonly free_transfers_remaining: number;
}

export interface TransferPlanData {
  readonly current_gameweek: number;
  readonly weekly_solutions: WeeklyTransferSolution[];
  readonly total_expected_points: number;
  readonly total_transfer_cost: number;
  readonly current_expected_points: number;
  readonly improvement: number;
}

export interface TransferPlanResponse {
  readonly success: boolean;
  readonly message: string;
  readonly data: TransferPlanData | null;
}