import { Formation, FormRating, Position } from '../types/fpl.types';

export interface FormationConfig {
  readonly formation: Formation;
  readonly positions: FormationPositions;
  readonly is_valid: boolean;
  readonly total_players: 11; // Always 11 for valid formations
  readonly attacking_rating: FormRating; // 0-10
  readonly defensive_rating: FormRating; // 0-10
  readonly balanced_rating: FormRating; // 0-10
}

export interface FormationPositions {
  readonly GKP: number;
  readonly DEF: number;
  readonly MID: number;
  readonly FWD: number;
}

export interface FormationMetadata {
  readonly name: string;
  readonly description: string;
  readonly tactical_style: 'attacking' | 'balanced' | 'defensive';
  readonly popularity_rank: number; // 1-7 (among available formations)
  readonly recommended_for: readonly ('beginners' | 'experienced' | 'aggressive' | 'conservative')[];
}