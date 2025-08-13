import { FormationConfig } from '../object-interfaces/formation.interface';
import { OptimizationConstraints, OptimizationRequest } from '../object-interfaces/optimization-request.interface';
import { Player } from '../object-interfaces/player.interface';
import { PlayerFilters } from '../object-interfaces/players-response.interface';
import {
    BUDGET_CONSTRAINTS, COST_CONSTRAINTS,
    Formation,
    FormationPositions,
    FORMATIONS,
    FormRating,
    GAMEWEEK_CONSTRAINTS,
    GameweekNumber,
    INJURY_STATUSES,
    InjuryStatus,
    MaxPlayersPerTeam,
    PLAYER_SORT_FIELDS,
    PlayerSortField,
    PlayingChance,
    Position,
    POSITIONS, PREMIER_LEAGUE_TEAMS,
    PremierLeagueTeam,
    RISK_TOLERANCES,
    RiskTolerance,
    ValidationError,
    ValidationErrorCode
} from '../types/fpl.types';

// Type guards with union type support
export function isValidPosition(value: unknown): value is Position {
  return typeof value === 'string' && POSITIONS.includes(value as Position);
}

export function isValidTeam(value: unknown): value is PremierLeagueTeam {
  return typeof value === 'string' && PREMIER_LEAGUE_TEAMS.includes(value as PremierLeagueTeam);
}

export function isValidFormation(value: unknown): value is Formation {
  return typeof value === 'string' && FORMATIONS.includes(value as Formation);
}

export function isValidInjuryStatus(value: unknown): value is InjuryStatus {
  return typeof value === 'string' && INJURY_STATUSES.includes(value as InjuryStatus);
}

export function isValidRiskTolerance(value: unknown): value is RiskTolerance {
  return typeof value === 'string' && RISK_TOLERANCES.includes(value as RiskTolerance);
}

export function isValidPlayerSortField(value: unknown): value is PlayerSortField {
  return typeof value === 'string' && PLAYER_SORT_FIELDS.includes(value as PlayerSortField);
}

export function isValidFormRating(value: unknown): value is FormRating {
  return typeof value === 'number' && Number.isInteger(value) && value >= 0 && value <= 10;
}

export function isValidPlayingChance(value: unknown): value is PlayingChance {
  return typeof value === 'number' && [0, 25, 50, 75, 100].includes(value);
}

export function isValidMaxPlayersPerTeam(value: unknown): value is MaxPlayersPerTeam {
  return typeof value === 'number' && [1, 2, 3].includes(value);
}

export function isValidGameweek(value: unknown): value is GameweekNumber {
  return typeof value === 'number' && 
         Number.isInteger(value) && 
         value >= GAMEWEEK_CONSTRAINTS.MIN && 
         value <= GAMEWEEK_CONSTRAINTS.MAX;
}

export function isValidBudget(value: unknown): value is number {
  return typeof value === 'number' && 
         value >= BUDGET_CONSTRAINTS.MIN && 
         value <= BUDGET_CONSTRAINTS.MAX;
}

export function isValidCost(value: unknown): value is number {
  return typeof value === 'number' && 
         value >= COST_CONSTRAINTS.MIN && 
         value <= COST_CONSTRAINTS.MAX;
}

export function isValidPercentage(value: unknown): value is number {
  return typeof value === 'number' && value >= 0 && value <= 100;
}

export function isValidScore(value: unknown, min: number = 0, max: number = 1): value is number {
  return typeof value === 'number' && value >= min && value <= max;
}

// Validation functions with comprehensive union type checking
export function validatePlayer(player: Partial<Player>): ValidationError[] {
  const errors: ValidationError[] = [];
  
  // Required fields
  if (!player.name?.trim()) {
    errors.push(createValidationError(
      'name', 
      'Player name is required and cannot be empty', 
      'REQUIRED'
    ));
  }
  
  if (!isValidPosition(player.position)) {
    errors.push(createValidationError(
      'position',
      `Position must be one of: ${POSITIONS.join(', ')}`,
      'INVALID_VALUE',
      player.position
    ));
  }
  
  if (!isValidTeam(player.team)) {
    errors.push(createValidationError(
      'team',
      'Must be a valid Premier League team',
      'INVALID_VALUE',
      player.team
    ));
  }
  
  if (!isValidCost(player.cost)) {
    errors.push(createValidationError(
      'cost',
      `Cost must be between £${COST_CONSTRAINTS.MIN}m and £${COST_CONSTRAINTS.MAX}m`,
      'OUT_OF_RANGE',
      player.cost
    ));
  }
  
  if (typeof player.points !== 'number' || player.points < 0) {
    errors.push(createValidationError(
      'points',
      'Points must be a non-negative number',
      'INVALID_VALUE',
      player.points
    ));
  }
  
  // Optional fields with union type validation
  if (player.form !== undefined && !isValidFormRating(player.form)) {
    errors.push(createValidationError(
      'form',
      'Form rating must be an integer between 0 and 10',
      'OUT_OF_RANGE',
      player.form
    ));
  }
  
  if (player.selected_by_percent !== undefined && !isValidPercentage(player.selected_by_percent)) {
    errors.push(createValidationError(
      'selected_by_percent',
      'Selected by percentage must be between 0 and 100',
      'OUT_OF_RANGE',
      player.selected_by_percent
    ));
  }
  
  if (player.chance_of_playing_this_round !== undefined && 
      player.chance_of_playing_this_round !== null && 
      !isValidPlayingChance(player.chance_of_playing_this_round)) {
    errors.push(createValidationError(
      'chance_of_playing_this_round',
      'Playing chance must be one of: 0, 25, 50, 75, 100',
      'INVALID_VALUE',
      player.chance_of_playing_this_round
    ));
  }
  
  if (player.chance_of_playing_next_round !== undefined && 
      player.chance_of_playing_next_round !== null && 
      !isValidPlayingChance(player.chance_of_playing_next_round)) {
    errors.push(createValidationError(
      'chance_of_playing_next_round',
      'Playing chance must be one of: 0, 25, 50, 75, 100',
      'INVALID_VALUE',
      player.chance_of_playing_next_round
    ));
  }
  
  if (player.injury_status !== undefined && !isValidInjuryStatus(player.injury_status)) {
    errors.push(createValidationError(
      'injury_status',
      `Injury status must be one of: ${INJURY_STATUSES.join(', ')}`,
      'INVALID_VALUE',
      player.injury_status
    ));
  }
  
  if (player.fixture_difficulty !== undefined && !isValidFormRating(player.fixture_difficulty)) {
    errors.push(createValidationError(
      'fixture_difficulty',
      'Fixture difficulty must be an integer between 0 and 10',
      'OUT_OF_RANGE',
      player.fixture_difficulty
    ));
  }
  
  if (player.gameweek !== undefined && !isValidGameweek(player.gameweek)) {
    errors.push(createValidationError(
      'gameweek',
      `Gameweek must be between ${GAMEWEEK_CONSTRAINTS.MIN} and ${GAMEWEEK_CONSTRAINTS.MAX}`,
      'OUT_OF_RANGE',
      player.gameweek
    ));
  }
  
  // Non-negative number validations
  const nonNegativeFields: (keyof Player)[] = [
    'minutes', 'goals_scored', 'assists', 'clean_sheets', 'bonus',
    'transfers_in', 'transfers_out'
  ];
  
  nonNegativeFields.forEach(field => {
    const value = player[field];
    if (value !== undefined && (typeof value !== 'number' || value < 0)) {
      errors.push(createValidationError(
        field as string,
        `${field} must be a non-negative number`,
        'OUT_OF_RANGE',
        value
      ));
    }
  });
  
  return errors;
}

export function validateOptimizationRequest(request: Partial<OptimizationRequest>): ValidationError[] {
  const errors: ValidationError[] = [];
  
  if (!isValidBudget(request.budget)) {
    errors.push(createValidationError(
      'budget',
      `Budget must be between £${BUDGET_CONSTRAINTS.MIN}m and £${BUDGET_CONSTRAINTS.MAX}m`,
      'OUT_OF_RANGE',
      request.budget
    ));
  }
  
  if (!isValidFormation(request.formation)) {
    errors.push(createValidationError(
      'formation',
      `Formation must be one of: ${FORMATIONS.join(', ')}`,
      'INVALID_VALUE',
      request.formation
    ));
  }
  
  if (request.gameweek !== undefined && !isValidGameweek(request.gameweek)) {
    errors.push(createValidationError(
      'gameweek',
      `Gameweek must be between ${GAMEWEEK_CONSTRAINTS.MIN} and ${GAMEWEEK_CONSTRAINTS.MAX}`,
      'OUT_OF_RANGE',
      request.gameweek
    ));
  }
  
  if (request.constraints) {
    errors.push(...validateOptimizationConstraints(request.constraints));
  }
  
  if (request.preferences?.risk_tolerance && 
      !isValidRiskTolerance(request.preferences.risk_tolerance)) {
    errors.push(createValidationError(
      'preferences.risk_tolerance',
      `Risk tolerance must be one of: ${RISK_TOLERANCES.join(', ')}`,
      'INVALID_VALUE',
      request.preferences.risk_tolerance
    ));
  }
  
  return errors;
}

export function validateOptimizationConstraints(constraints: OptimizationConstraints): ValidationError[] {
  const errors: ValidationError[] = [];
  
  if (constraints.max_players_per_team !== undefined && 
      !isValidMaxPlayersPerTeam(constraints.max_players_per_team)) {
    errors.push(createValidationError(
      'constraints.max_players_per_team',
      'Maximum players per team must be 1, 2, or 3',
      'INVALID_VALUE',
      constraints.max_players_per_team
    ));
  }
  
  if (constraints.min_players_from_teams) {
    const invalidTeams = constraints.min_players_from_teams.filter(team => !isValidTeam(team));
    if (invalidTeams.length > 0) {
      errors.push(createValidationError(
        'constraints.min_players_from_teams',
        'All teams must be valid Premier League teams',
        'INVALID_VALUE',
        invalidTeams
      ));
    }
  }
  
  if (constraints.min_form_rating !== undefined && 
      !isValidFormRating(constraints.min_form_rating)) {
    errors.push(createValidationError(
      'constraints.min_form_rating',
      'Minimum form rating must be an integer between 0 and 10',
      'OUT_OF_RANGE',
      constraints.min_form_rating
    ));
  }
  
  if (constraints.max_fixture_difficulty !== undefined && 
      !isValidFormRating(constraints.max_fixture_difficulty)) {
    errors.push(createValidationError(
      'constraints.max_fixture_difficulty',
      'Maximum fixture difficulty must be an integer between 0 and 10',
      'OUT_OF_RANGE',
      constraints.max_fixture_difficulty
    ));
  }
  
  // Validate cost constraints
  if (constraints.min_player_cost !== undefined && !isValidCost(constraints.min_player_cost)) {
    errors.push(createValidationError(
      'constraints.min_player_cost',
      `Minimum player cost must be between £${COST_CONSTRAINTS.MIN}m and £${COST_CONSTRAINTS.MAX}m`,
      'OUT_OF_RANGE',
      constraints.min_player_cost
    ));
  }
  
  if (constraints.max_player_cost !== undefined && !isValidCost(constraints.max_player_cost)) {
    errors.push(createValidationError(
      'constraints.max_player_cost',
      `Maximum player cost must be between £${COST_CONSTRAINTS.MIN}m and £${COST_CONSTRAINTS.MAX}m`,
      'OUT_OF_RANGE',
      constraints.max_player_cost
    ));
  }
  
  if (constraints.min_player_cost && 
      constraints.max_player_cost && 
      constraints.min_player_cost > constraints.max_player_cost) {
    errors.push(createValidationError(
      'constraints.player_cost_range',
      'Minimum player cost cannot be greater than maximum player cost',
      'INVALID_RANGE'
    ));
  }
  
  return errors;
}

export function validatePlayerFilters(filters: PlayerFilters): ValidationError[] {
  const errors: ValidationError[] = [];
  
  if (filters.positions) {
    const invalidPositions = filters.positions.filter(pos => !isValidPosition(pos));
    if (invalidPositions.length > 0) {
      errors.push(createValidationError(
        'filters.positions',
        `Invalid positions: ${invalidPositions.join(', ')}. Valid positions: ${POSITIONS.join(', ')}`,
        'INVALID_VALUE',
        invalidPositions
      ));
    }
  }
  
  if (filters.teams) {
    const invalidTeams = filters.teams.filter(team => !isValidTeam(team));
    if (invalidTeams.length > 0) {
      errors.push(createValidationError(
        'filters.teams',
        `Invalid teams: ${invalidTeams.join(', ')}`,
        'INVALID_VALUE',
        invalidTeams
      ));
    }
  }
  
  if (filters.injury_status) {
    const invalidStatuses = filters.injury_status.filter(status => !isValidInjuryStatus(status));
    if (invalidStatuses.length > 0) {
      errors.push(createValidationError(
        'filters.injury_status',
        `Invalid injury statuses: ${invalidStatuses.join(', ')}. Valid statuses: ${INJURY_STATUSES.join(', ')}`,
        'INVALID_VALUE',
        invalidStatuses
      ));
    }
  }
  
  if (filters.min_form !== undefined && !isValidFormRating(filters.min_form)) {
    errors.push(createValidationError(
      'filters.min_form',
      'Minimum form must be an integer between 0 and 10',
      'OUT_OF_RANGE',
      filters.min_form
    ));
  }
  
  // Cost range validations
  if (filters.min_cost !== undefined && !isValidCost(filters.min_cost)) {
    errors.push(createValidationError(
      'filters.min_cost',
      `Minimum cost must be between £${COST_CONSTRAINTS.MIN}m and £${COST_CONSTRAINTS.MAX}m`,
      'OUT_OF_RANGE',
      filters.min_cost
    ));
  }
  
  if (filters.max_cost !== undefined && !isValidCost(filters.max_cost)) {
    errors.push(createValidationError(
      'filters.max_cost',
      `Maximum cost must be between £${COST_CONSTRAINTS.MIN}m and £${COST_CONSTRAINTS.MAX}m`,
      'OUT_OF_RANGE',
      filters.max_cost
    ));
  }
  
  if (filters.min_cost && filters.max_cost && filters.min_cost > filters.max_cost) {
    errors.push(createValidationError(
      'filters.cost_range',
      'Minimum cost cannot be greater than maximum cost',
      'INVALID_RANGE'
    ));
  }
  
  // Points range validations
  if (filters.min_points !== undefined && (typeof filters.min_points !== 'number' || filters.min_points < 0)) {
    errors.push(createValidationError(
      'filters.min_points',
      'Minimum points must be a non-negative number',
      'OUT_OF_RANGE',
      filters.min_points
    ));
  }
  
  if (filters.max_points !== undefined && (typeof filters.max_points !== 'number' || filters.max_points < 0)) {
    errors.push(createValidationError(
      'filters.max_points',
      'Maximum points must be a non-negative number',
      'OUT_OF_RANGE',
      filters.max_points
    ));
  }
  
  if (filters.min_points && filters.max_points && filters.min_points > filters.max_points) {
    errors.push(createValidationError(
      'filters.points_range',
      'Minimum points cannot be greater than maximum points',
      'INVALID_RANGE'
    ));
  }
  
  if (filters.min_minutes !== undefined && (typeof filters.min_minutes !== 'number' || filters.min_minutes < 0)) {
    errors.push(createValidationError(
      'filters.min_minutes',
      'Minimum minutes must be a non-negative number',
      'OUT_OF_RANGE',
      filters.min_minutes
    ));
  }
  
  return errors;
}

// Helper function to create consistent validation errors
function createValidationError(
  field: string,
  message: string,
  code: ValidationErrorCode,
  value?: unknown
): ValidationError {
  return {
    field,
    message,
    code,
    value,
    severity: code === 'REQUIRED' || code === 'CONSTRAINT_VIOLATION' ? 'error' : 'warning'
  };
}

// Utility functions with union type support
export function parseFormation(formation: Formation): FormationPositions {
  const [def, mid, fwd] = formation.split('-').map(Number) as [number, number, number];
  return {
    GKP: 1,
    DEF: def,
    MID: mid,
    FWD: fwd
  };
}

export function isValidFormationPlayers(positions: FormationPositions): boolean {
  const total = Object.values(positions).reduce((sum, count) => sum + count, 0);
  return total === 11;
}

export function validateFormationConfig(config: Partial<FormationConfig>): ValidationError[] {
  const errors: ValidationError[] = [];
  
  if (!config.formation || !isValidFormation(config.formation)) {
    errors.push(createValidationError(
      'formation',
      `Formation must be one of: ${FORMATIONS.join(', ')}`,
      'INVALID_VALUE',
      config.formation
    ));
  }
  
  if (config.positions && !isValidFormationPlayers(config.positions)) {
    errors.push(createValidationError(
      'positions',
      'Formation must have exactly 11 players total',
      'CONSTRAINT_VIOLATION',
      config.positions
    ));
  }
  
  if (config.attacking_rating !== undefined && !isValidFormRating(config.attacking_rating)) {
    errors.push(createValidationError(
      'attacking_rating',
      'Attacking rating must be an integer between 0 and 10',
      'OUT_OF_RANGE',
      config.attacking_rating
    ));
  }
  
  if (config.defensive_rating !== undefined && !isValidFormRating(config.defensive_rating)) {
    errors.push(createValidationError(
      'defensive_rating',
      'Defensive rating must be an integer between 0 and 10',
      'OUT_OF_RANGE',
      config.defensive_rating
    ));
  }
  
  if (config.balanced_rating !== undefined && !isValidFormRating(config.balanced_rating)) {
    errors.push(createValidationError(
      'balanced_rating',
      'Balanced rating must be an integer between 0 and 10',
      'OUT_OF_RANGE',
      config.balanced_rating
    ));
  }
  
  return errors;
}

// Type assertion functions for runtime type checking
export function assertPlayer(obj: unknown): Player {
  if (!obj || typeof obj !== 'object') {
    throw new Error('Invalid player object');
  }
  
  const errors = validatePlayer(obj as Partial<Player>);
  if (errors.length > 0) {
    throw new Error(`Player validation failed: ${errors.map(e => e.message).join(', ')}`);
  }
  
  return obj as Player;
}

export function assertOptimizationRequest(obj: unknown): OptimizationRequest {
  if (!obj || typeof obj !== 'object') {
    throw new Error('Invalid optimization request object');
  }
  
  const errors = validateOptimizationRequest(obj as Partial<OptimizationRequest>);
  if (errors.length > 0) {
    throw new Error(`Optimization request validation failed: ${errors.map(e => e.message).join(', ')}`);
  }
  
  return obj as OptimizationRequest;
}