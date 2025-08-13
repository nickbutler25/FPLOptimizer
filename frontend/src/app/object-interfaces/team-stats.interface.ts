import { 
  Formation,
  PremierLeagueTeam,
  RiskTolerance,
  FormRating
} from '../types/fpl.types';

export interface TeamStats {
  readonly total_cost: number;
  readonly total_points: number;
  readonly remaining_budget: number;
  readonly average_points_per_player: number;
  readonly formation: Formation;
  readonly players_count: PositionCount;
  readonly team_distribution: readonly TeamDistribution[];
  readonly value_metrics: ValueMetrics;
  readonly risk_metrics?: RiskMetrics;
  readonly performance_metrics?: PerformanceMetrics;
}

export interface PositionCount {
  readonly GKP: number;
  readonly DEF: number;
  readonly MID: number;
  readonly FWD: number;
}

export interface TeamDistribution {
  readonly team: PremierLeagueTeam;
  readonly player_count: number;
  readonly total_cost: number;
  readonly total_points: number;
  readonly average_points_per_player: number;
}

export interface ValueMetrics {
  readonly points_per_million: number;
  readonly best_value_player: string;
  readonly most_expensive_player: string;
  readonly cheapest_player: string;
  readonly value_efficiency_score: number; // 0-10
}

export interface RiskMetrics {
  readonly injury_risk_score: FormRating; // 0-10
  readonly rotation_risk_score: FormRating; // 0-10
  readonly fixture_difficulty: FormRating; // 0-10
  readonly overall_risk_score: FormRating; // 0-10
  readonly risk_tolerance: RiskTolerance;
  readonly high_risk_players: readonly number[]; // player IDs
}

export interface PerformanceMetrics {
  readonly projected_points: number;
  readonly consistency_score: FormRating; // 0-10
  readonly captaincy_options: readonly number[]; // player IDs
  readonly differential_score: FormRating; // 0-10 (based on low ownership)
  readonly form_trend: 'improving' | 'declining' | 'stable';
}