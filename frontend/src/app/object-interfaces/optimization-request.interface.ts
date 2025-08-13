import { 
  Formation, 
  PremierLeagueTeam, 
  MaxPlayersPerTeam,
  RiskTolerance,
  OptimizationAlgorithm,
  GameweekNumber,
  FormRating
} from '../types/fpl.types';

export interface OptimizationRequest {
  readonly budget: number; // 50-120
  readonly formation: Formation;
  readonly gameweek?: GameweekNumber;
  readonly constraints?: OptimizationConstraints;
  readonly preferences?: OptimizationPreferences;
  readonly algorithm?: OptimizationAlgorithm;
}

export interface OptimizationConstraints {
  readonly max_players_per_team?: MaxPlayersPerTeam; // 1-3, default 3
  readonly min_players_from_teams?: readonly PremierLeagueTeam[];
  readonly exclude_player_ids?: readonly number[];
  readonly include_player_ids?: readonly number[];
  readonly min_total_points?: number;
  readonly max_player_cost?: number;
  readonly min_player_cost?: number;
  readonly exclude_injured?: boolean;
  readonly exclude_doubtful?: boolean;
  readonly min_minutes_played?: number;
  readonly min_form_rating?: FormRating;
  readonly max_fixture_difficulty?: FormRating;
}

export interface OptimizationPreferences {
  readonly prefer_form?: boolean; // Weight recent form higher
  readonly prefer_popular?: boolean; // Weight selection % higher  
  readonly risk_tolerance?: RiskTolerance;
  readonly prioritize_captaincy?: boolean; // Ensure good captain options
  readonly prefer_differentials?: boolean; // Prefer low-owned players
  readonly consider_fixtures?: boolean; // Factor in upcoming fixtures
  readonly weight_bonus_points?: number; // 0-1 multiplier for bonus points
  readonly weight_clean_sheets?: number; // 0-1 multiplier for clean sheets (DEF/GKP)
}