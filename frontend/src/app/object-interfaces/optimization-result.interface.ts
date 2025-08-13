import { ApiStatus, DataSource, Formation, OptimizationAlgorithm, OptimizationConstraintType } from "../types/fpl.types";
import { Player } from "./player.interface";

export interface OptimizationResult {
  readonly status: ApiStatus;
  readonly players?: readonly Player[];
  readonly total_cost?: number;
  readonly total_points?: number;
  readonly remaining_budget?: number;
  readonly formation?: Formation;
  readonly message?: string;
  readonly optimization_time?: number; // in milliseconds
  readonly constraints_applied?: readonly OptimizationConstraint[];
  readonly alternatives_count?: number;
  readonly confidence_score?: number; // 0-1
  readonly algorithm_used?: OptimizationAlgorithm;
  readonly data_source?: DataSource;
  readonly warnings?: readonly OptimizationWarning[];
}

export interface OptimizationConstraint {
  readonly type: OptimizationConstraintType;
  readonly description: string;
  readonly value: unknown;
  readonly applied: boolean;
  readonly impact_score?: number; // 0-1, how much this constraint affected the result
}

export interface OptimizationWarning {
  readonly type: 'injury_risk' | 'rotation_risk' | 'fixture_difficulty' | 'form_decline' | 'price_rise' | 'low_ownership';
  readonly message: string;
  readonly player_ids?: readonly number[];
  readonly severity: 'low' | 'medium' | 'high';
}