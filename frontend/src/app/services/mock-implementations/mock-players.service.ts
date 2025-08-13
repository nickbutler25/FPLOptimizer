import { Injectable } from '@angular/core';
import { delay, Observable, of } from 'rxjs';
import { PlayersServiceInterface } from '..';
import { ApiResponse, Player, PlayerFilters, PlayersResponse } from '../../object-interfaces';
import { ApiStatus } from '../../types/fpl.types';


@Injectable({
  providedIn: 'root'
})
export class MockPlayersService implements PlayersServiceInterface {

  private readonly mockPlayers: readonly Player[] = [
    // Goalkeepers
    {
      id: 1, name: 'Alisson', position: 'GKP', team: 'Liverpool',
      cost: 5.5, points: 185, points_per_cost: 33.6, injury_status: 'available'
    },
    {
      id: 2, name: 'Ederson', position: 'GKP', team: 'Man City', 
      cost: 5.0, points: 170, points_per_cost: 34.0, injury_status: 'available'
    },
    
    // Defenders
    {
      id: 3, name: 'Alexander-Arnold', position: 'DEF', team: 'Liverpool',
      cost: 7.5, points: 210, points_per_cost: 28.0, injury_status: 'available'
    },
    {
      id: 4, name: 'Cancelo', position: 'DEF', team: 'Man City',
      cost: 7.0, points: 195, points_per_cost: 27.9, injury_status: 'available'
    },
    {
      id: 5, name: 'James', position: 'DEF', team: 'Chelsea',
      cost: 6.0, points: 165, points_per_cost: 27.5, injury_status: 'doubtful'
    },
    
    // Midfielders
    {
      id: 6, name: 'Salah', position: 'MID', team: 'Liverpool',
      cost: 13.0, points: 280, points_per_cost: 21.5, injury_status: 'available'
    },
    {
      id: 7, name: 'De Bruyne', position: 'MID', team: 'Man City',
      cost: 11.5, points: 245, points_per_cost: 21.3, injury_status: 'available'
    },
    {
      id: 8, name: 'Saka', position: 'MID', team: 'Arsenal',
      cost: 8.5, points: 195, points_per_cost: 22.9, injury_status: 'available'
    },
    
    // Forwards
    {
      id: 9, name: 'Haaland', position: 'FWD', team: 'Man City',
      cost: 14.0, points: 320, points_per_cost: 22.9, injury_status: 'available'
    },
    {
      id: 10, name: 'Kane', position: 'FWD', team: 'Tottenham',
      cost: 12.5, points: 270, points_per_cost: 21.6, injury_status: 'available'
    },
    {
      id: 11, name: 'Jesus', position: 'FWD', team: 'Arsenal',
      cost: 8.0, points: 185, points_per_cost: 23.1, injury_status: 'available'
    }
  ];

  getPlayers(filters?: PlayerFilters): Observable<PlayersResponse> {
    console.log(`Mock API call: GET /players`, filters);
    
    let filteredPlayers = [...this.mockPlayers];
    
    // Apply filters if provided
    if (filters) {
      if (filters.positions?.length) {
        filteredPlayers = filteredPlayers.filter(p => filters.positions!.includes(p.position));
      }
      
      if (filters.teams?.length) {
        filteredPlayers = filteredPlayers.filter(p => filters.teams!.includes(p.team));
      }
      
      if (filters.min_cost !== undefined) {
        filteredPlayers = filteredPlayers.filter(p => p.cost >= filters.min_cost!);
      }
      
      if (filters.max_cost !== undefined) {
        filteredPlayers = filteredPlayers.filter(p => p.cost <= filters.max_cost!);
      }
      
      if (filters.available_only) {
        filteredPlayers = filteredPlayers.filter(p => p.injury_status === 'available');
      }
      
      if (filters.search_term) {
        const term = filters.search_term.toLowerCase();
        filteredPlayers = filteredPlayers.filter(p => 
          p.name.toLowerCase().includes(term) ||
          p.team.toLowerCase().includes(term)
        );
      }
    }
    
    const response: PlayersResponse = {
      status: 'success',
      players: filteredPlayers,
      total_count: filteredPlayers.length,
      filters_applied: filters
    };
    
    return of(response).pipe(delay(600));
  }

  getPlayer(id: number): Observable<ApiResponse<Player>> {
    console.log(`Mock API call: GET /players/${id}`);
    
    const player = this.mockPlayers.find(p => p.id === id);
    
    if (!player) {
      return of({
        status: 'error' as ApiStatus,
        message: `Player with ID ${id} not found`,
        errors: [{
          field: 'id',
          message: 'Player not found',
          code: 'INVALID_VALUE',
          value: id
        }] as const
      }).pipe(delay(400));
    }
    
    return of({
      status: 'success' as ApiStatus,
      data: player,
      timestamp: new Date().toISOString()
    }).pipe(delay(400));
  }
}