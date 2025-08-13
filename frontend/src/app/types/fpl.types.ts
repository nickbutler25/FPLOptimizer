// ===== CORE FPL TYPES =====
export type Position = 'GKP' | 'DEF' | 'MID' | 'FWD';

export type PremierLeagueTeam = 
  | 'Arsenal'
  | 'Aston Villa'
  | 'Bournemouth'
  | 'Brentford'
  | 'Brighton'
  | 'Chelsea'
  | 'Crystal Palace'
  | 'Everton'
  | 'Fulham'
  | 'Ipswich'
  | 'Leicester'
  | 'Liverpool'
  | 'Man City'
  | 'Man Utd'
  | 'Newcastle'
  | 'Nottm Forest'
  | 'Southampton'
  | 'Tottenham'
  | 'West Ham'
  | 'Wolves';

export type Formation = '3-4-3' | '3-5-2' | '4-3-3' | '4-4-2' | '4-5-1' | '5-3-2' | '5-4-1';

// ===== STATUS TYPES =====
export type ApiStatus = 'success' | 'error' | 'loading' | 'idle';
export type HealthStatus = 'healthy' | 'unhealthy' | 'degraded';
export type InjuryStatus = 'available' | 'doubtful' | 'injured' | 'suspended' | 'unavailable';
export type CacheStatus = 'hit' | 'miss' | 'stale' | 'error';

// ===== RATING AND SCORE TYPES =====
export type FormRating = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;
export type PlayingChance = 0 | 25 | 50 | 75 | 100;
export type MaxPlayersPerTeam = 1 | 2 | 3;
export type GameweekNumber = 
  | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10
  | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20
  | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 | 30
  | 31 | 32 | 33 | 34 | 35 | 36 | 37 | 38;

// ===== BUSINESS LOGIC TYPES =====
export type RiskTolerance = 'conservative' | 'balanced' | 'aggressive';
export type OptimizationAlgorithm = 'linear_programming' | 'genetic_algorithm' | 'simulated_annealing' | 'greedy' | 'hybrid';
export type DataSource = 'fpl_api' | 'cache' | 'fallback' | 'mock';

export type OptimizationConstraintType = 
  | 'max_players_per_team' 
  | 'min_players_from_team' 
  | 'exclude_players' 
  | 'include_players' 
  | 'min_points' 
  | 'max_cost'
  | 'min_form'
  | 'injury_exclusion'
  | 'rotation_risk'
  | 'fixture_difficulty';

// ===== SORTING AND FILTERING TYPES =====
export type SortOrder = 'asc' | 'desc';

export type PlayerSortField = 
  | 'name' 
  | 'cost' 
  | 'points' 
  | 'points_per_cost' 
  | 'form' 
  | 'selected_by_percent'
  | 'minutes'
  | 'goals_scored'
  | 'assists'
  | 'clean_sheets'
  | 'bonus'
  | 'transfers_in'
  | 'transfers_out';

// ===== TECHNICAL TYPES =====
export type ValidationErrorCode = 
  | 'REQUIRED'
  | 'INVALID_VALUE'
  | 'OUT_OF_RANGE'
  | 'INVALID_RANGE'
  | 'INVALID_FORMAT'
  | 'CONSTRAINT_VIOLATION'
  | 'DUPLICATE_VALUE'
  | 'INSUFFICIENT_DATA'
  | 'BUSINESS_RULE_VIOLATION';

export type LogLevel = 'debug' | 'info' | 'warn' | 'error' | 'fatal';
export type RequestMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
export type ContentType = 'application/json' | 'application/xml' | 'text/plain' | 'text/html';
export type TimeUnit = 'seconds' | 'minutes' | 'hours' | 'days' | 'weeks';

// ===== UI AND UX TYPES =====
export type FormationTacticalStyle = 'attacking' | 'balanced' | 'defensive';
export type UserExperienceLevel = 'beginner' | 'intermediate' | 'advanced' | 'expert';
export type RecommendationType = 'beginners' | 'experienced' | 'aggressive' | 'conservative';
export type WarningType = 'injury_risk' | 'rotation_risk' | 'fixture_difficulty' | 'form_decline' | 'price_rise' | 'low_ownership';
export type WarningSeverity = 'low' | 'medium' | 'high';
export type FormTrend = 'improving' | 'declining' | 'stable';

// ===== CONSTANTS ARRAYS (readonly) =====
export const POSITIONS: readonly Position[] = ['GKP', 'DEF', 'MID', 'FWD'] as const;

export const PREMIER_LEAGUE_TEAMS: readonly PremierLeagueTeam[] = [
  'Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton', 'Chelsea',
  'Crystal Palace', 'Everton', 'Fulham', 'Ipswich', 'Leicester', 'Liverpool',
  'Man City', 'Man Utd', 'Newcastle', 'Nottm Forest', 'Southampton', 'Tottenham',
  'West Ham', 'Wolves'
] as const;

export const FORMATIONS: readonly Formation[] = [
  '3-4-3', '3-5-2', '4-3-3', '4-4-2', '4-5-1', '5-3-2', '5-4-1'
] as const;

export const INJURY_STATUSES: readonly InjuryStatus[] = [
  'available', 'doubtful', 'injured', 'suspended', 'unavailable'
] as const;

export const RISK_TOLERANCES: readonly RiskTolerance[] = [
  'conservative', 'balanced', 'aggressive'
] as const;

export const PLAYER_SORT_FIELDS: readonly PlayerSortField[] = [
  'name', 'cost', 'points', 'points_per_cost', 'form', 'selected_by_percent',
  'minutes', 'goals_scored', 'assists', 'clean_sheets', 'bonus', 'transfers_in', 'transfers_out'
] as const;

export const OPTIMIZATION_ALGORITHMS: readonly OptimizationAlgorithm[] = [
  'linear_programming', 'genetic_algorithm', 'simulated_annealing', 'greedy', 'hybrid'
] as const;

export const VALIDATION_ERROR_CODES: readonly ValidationErrorCode[] = [
  'REQUIRED', 'INVALID_VALUE', 'OUT_OF_RANGE', 'INVALID_RANGE', 'INVALID_FORMAT',
  'CONSTRAINT_VIOLATION', 'DUPLICATE_VALUE', 'INSUFFICIENT_DATA', 'BUSINESS_RULE_VIOLATION'
] as const;

// ===== CONFIGURATION CONSTANTS =====
export const POSITION_CONFIG = {
  GKP: { 
    name: 'Goalkeeper', 
    plural: 'Goalkeepers',
    min: 1, 
    max: 1, 
    color: '#f59e0b',
    icon: '🥅'
  },
  DEF: { 
    name: 'Defender', 
    plural: 'Defenders',
    min: 3, 
    max: 5, 
    color: '#10b981',
    icon: '🛡️'
  },
  MID: { 
    name: 'Midfielder', 
    plural: 'Midfielders',
    min: 2, 
    max: 5, 
    color: '#3b82f6',
    icon: '⚽'
  },
  FWD: { 
    name: 'Forward', 
    plural: 'Forwards',
    min: 1, 
    max: 3, 
    color: '#ef4444',
    icon: '🏃‍♂️'
  }
} as const;

export const FORMATION_CONFIG = {
  '3-4-3': {
    name: 'Three-Four-Three',
    tactical_style: 'attacking' as FormationTacticalStyle,
    attacking_rating: 9,
    defensive_rating: 6,
    balanced_rating: 7,
    popularity_rank: 2,
    description: 'High attacking potential with wing-backs providing width'
  },
  '3-5-2': {
    name: 'Three-Five-Two',
    tactical_style: 'balanced' as FormationTacticalStyle,
    attacking_rating: 7,
    defensive_rating: 7,
    balanced_rating: 8,
    popularity_rank: 1,
    description: 'Most balanced formation with midfield control'
  },
  '4-3-3': {
    name: 'Four-Three-Three',
    tactical_style: 'attacking' as FormationTacticalStyle,
    attacking_rating: 8,
    defensive_rating: 7,
    balanced_rating: 8,
    popularity_rank: 3,
    description: 'Classic attacking formation with wingers'
  },
  '4-4-2': {
    name: 'Four-Four-Two',
    tactical_style: 'balanced' as FormationTacticalStyle,
    attacking_rating: 7,
    defensive_rating: 8,
    balanced_rating: 9,
    popularity_rank: 4,
    description: 'Traditional balanced formation'
  },
  '4-5-1': {
    name: 'Four-Five-One',
    tactical_style: 'defensive' as FormationTacticalStyle,
    attacking_rating: 6,
    defensive_rating: 9,
    balanced_rating: 7,
    popularity_rank: 6,
    description: 'Defensive formation with midfield packed'
  },
  '5-3-2': {
    name: 'Five-Three-Two',
    tactical_style: 'defensive' as FormationTacticalStyle,
    attacking_rating: 6,
    defensive_rating: 9,
    balanced_rating: 6,
    popularity_rank: 7,
    description: 'Very defensive with five at the back'
  },
  '5-4-1': {
    name: 'Five-Four-One',
    tactical_style: 'defensive' as FormationTacticalStyle,
    attacking_rating: 5,
    defensive_rating: 10,
    balanced_rating: 5,
    popularity_rank: 5,
    description: 'Ultra-defensive formation'
  }
} as const;

// ===== CONSTRAINT CONSTANTS =====
export const BUDGET_CONSTRAINTS = {
  MIN: 50,
  MAX: 120,
  DEFAULT: 100,
  STEP: 0.1
} as const;

export const COST_CONSTRAINTS = {
  MIN: 3.9,
  MAX: 15.0
} as const;

export const GAMEWEEK_CONSTRAINTS = {
  MIN: 1,
  MAX: 38,
  CURRENT: 1 // This would be dynamically updated in a real app
} as const;

export const TEAM_CONSTRAINTS = {
  TOTAL_PLAYERS: 11,
  MAX_PLAYERS_PER_TEAM: 3,
  MIN_PLAYERS_PER_TEAM: 0
} as const;

export const POINTS_CONSTRAINTS = {
  MIN: 0,
  MAX: 500, // Realistic maximum for a season
  AVERAGE_GOOD_SEASON: 200
} as const;

export const FORM_CONSTRAINTS = {
  MIN: 0,
  MAX: 10,
  GOOD_FORM_THRESHOLD: 7
} as const;

export const SELECTION_CONSTRAINTS = {
  MIN_PERCENTAGE: 0,
  MAX_PERCENTAGE: 100,
  HIGH_OWNERSHIP_THRESHOLD: 20,
  DIFFERENTIAL_THRESHOLD: 5
} as const;

// ===== TYPE UTILITY FUNCTIONS =====
export type PositionCount = {
  readonly [K in Position]: number;
};

export type FormationPositions = PositionCount;

export type TeamStats = {
  readonly [K in PremierLeagueTeam]: {
    readonly player_count: number;
    readonly total_cost: number;
    readonly total_points: number;
  };
};

// ===== INTERFACE DEFINITIONS =====
export interface ValidationError {
  readonly field: string;
  readonly message: string;
  readonly code: ValidationErrorCode;
  readonly value?: unknown;
  readonly severity?: 'error' | 'warning' | 'info';
}

// ===== MAPPED TYPES FOR FLEXIBILITY =====
export type PlayerStatistics = {
  readonly [K in PlayerSortField]: number;
};

export type ConstraintValues = {
  readonly [K in OptimizationConstraintType]: unknown;
};

export type ValidationResults = {
  readonly [K in ValidationErrorCode]: ValidationError[];
};

// ===== EXPORT GROUPINGS FOR CONVENIENCE =====
export const CORE_TYPES = {
  POSITIONS,
  PREMIER_LEAGUE_TEAMS,
  FORMATIONS
} as const;

export const STATUS_TYPES = {
  INJURY_STATUSES,
  RISK_TOLERANCES
} as const;

export const CONSTRAINT_VALUES = {
  BUDGET_CONSTRAINTS,
  COST_CONSTRAINTS,
  GAMEWEEK_CONSTRAINTS,
  TEAM_CONSTRAINTS,
  POINTS_CONSTRAINTS,
  FORM_CONSTRAINTS,
  SELECTION_CONSTRAINTS
} as const;

