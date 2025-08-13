import { Player } from './player.interface';
import { 
  ApiStatus, 
  PlayerSortField, 
  SortOrder,
  Position,
  PremierLeagueTeam,
  InjuryStatus,
  FormRating
} from '../types/fpl.types';

export interface PlayersResponse {
  readonly status: ApiStatus;
  readonly players: readonly Player[];
  readonly total_count?: number;
  readonly page?: number;
  readonly page_size?: number;
  readonly total_pages?: number;
  readonly has_next_page?: boolean;
  readonly has_previous_page?: boolean;
  readonly filters_applied?: PlayerFilters;
  readonly sort?: PlayerSort;
}

export interface PlayerFilters {
  readonly positions?: readonly Position[];
  readonly teams?: readonly PremierLeagueTeam[];
  readonly min_cost?: number;
  readonly max_cost?: number;
  readonly min_points?: number;
  readonly max_points?: number;
  readonly min_form?: FormRating;
  readonly injury_status?: readonly InjuryStatus[];
  readonly available_only?: boolean;
  readonly min_minutes?: number;
  readonly search_term?: string;
}

export interface PlayerSort {
  readonly field: PlayerSortField;
  readonly order: SortOrder;
}