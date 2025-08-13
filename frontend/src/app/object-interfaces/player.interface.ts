import { 
  Position, 
  PremierLeagueTeam, 
  InjuryStatus, 
  FormRating, 
  PlayingChance,
  GameweekNumber
} from '../types/fpl.types';

export interface Player {
  readonly id: number;
  readonly name: string;
  readonly position: Position;
  readonly team: PremierLeagueTeam;
  readonly cost: number; // in millions (e.g., 13.0 = £13.0m)
  readonly points: number;
  readonly points_per_cost?: number;
  // Additional FPL data with union types
  readonly form?: FormRating; // 0-10 scale
  readonly selected_by_percent?: number; // 0-100
  readonly minutes?: number;
  readonly goals_scored?: number;
  readonly assists?: number;
  readonly clean_sheets?: number;
  readonly bonus?: number;
  readonly transfers_in?: number;
  readonly transfers_out?: number;
  readonly news?: string;
  readonly chance_of_playing_this_round?: PlayingChance | null;
  readonly chance_of_playing_next_round?: PlayingChance | null;
  readonly injury_status?: InjuryStatus;
  readonly photo_url?: string;
  readonly gameweek?: GameweekNumber;
  readonly fixture_difficulty?: FormRating; // 1-5 scale typically, using 0-10 for consistency
}