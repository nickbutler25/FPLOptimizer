
import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { retry, timeout } from 'rxjs/operators';
import { ConfigService } from '../../config/config.service';
import { ApiResponse } from '../../object-interfaces/api-response.interface';
import { Player } from '../../object-interfaces/player.interface';
import { PlayerFilters, PlayersResponse } from '../../object-interfaces/players-response.interface';
import { PlayersServiceInterface } from '../service-interfaces/players-service.interface';

@Injectable({
  providedIn: 'root'
})
export class PlayersService implements PlayersServiceInterface {

  constructor(
    private http: HttpClient,
    private config: ConfigService
  ) {}

  getPlayers(filters?: PlayerFilters): Observable<PlayersResponse> {
    let params = new HttpParams();
    
    if (filters) {
      if (filters.positions?.length) {
        params = params.set('positions', filters.positions.join(','));
      }
      if (filters.teams?.length) {
        params = params.set('teams', filters.teams.join(','));
      }
      if (filters.min_cost !== undefined) {
        params = params.set('min_cost', filters.min_cost.toString());
      }
      if (filters.max_cost !== undefined) {
        params = params.set('max_cost', filters.max_cost.toString());
      }
      if (filters.available_only) {
        params = params.set('available_only', 'true');
      }
    }
    
    return this.http.get<PlayersResponse>(
      this.config.getApiUrl('players'),
      { params }
    ).pipe(
      timeout(this.config.apiTimeout),
      retry(this.config.apiRetryAttempts)
    );
  }

  getPlayer(id: number): Observable<ApiResponse<Player>> {
    return this.http.get<ApiResponse<Player>>(
      this.config.getApiUrl(`players/${id}`)
    ).pipe(
      timeout(this.config.apiTimeout),
      retry(this.config.apiRetryAttempts)
    );
  }
}