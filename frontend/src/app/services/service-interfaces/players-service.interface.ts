import { Observable } from 'rxjs';
import { ApiResponse } from '../../object-interfaces/api-response.interface';
import { Player } from '../../object-interfaces/player.interface';
import { PlayerFilters, PlayersResponse } from '../../object-interfaces/players-response.interface';


export interface PlayersServiceInterface {
  // Essential player data methods
  getPlayers(filters?: PlayerFilters): Observable<PlayersResponse>;
  getPlayer(id: number): Observable<ApiResponse<Player>>;
}