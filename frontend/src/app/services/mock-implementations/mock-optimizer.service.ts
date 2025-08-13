import { Injectable } from '@angular/core';
import { delay, Observable, of } from 'rxjs';
import { OptimizationRequest, OptimizationResult } from '../../object-interfaces';
import { Formation } from '../../types/fpl.types';
import { OptimizerServiceInterface } from '../service-interfaces/optimizer-service.interface';

@Injectable({
  providedIn: 'root'
})
export class MockOptimizerService implements OptimizerServiceInterface {

  optimize(budget: number, formation: Formation): Observable<OptimizationResult> {
    console.log(`Mock API call: POST /api/optimize`);
    console.log(`Request body:`, { budget, formation });
    
    // Simulate what your Python backend would return
    const mockResponse: OptimizationResult = {
      status: 'success',
      players: [
        { id: 1, name: 'Alisson', position: 'GKP', team: 'Liverpool', cost: 5.5, points: 185, injury_status: 'available' },
        { id: 2, name: 'Alexander-Arnold', position: 'DEF', team: 'Liverpool', cost: 7.5, points: 210, injury_status: 'available' },
        { id: 3, name: 'van Dijk', position: 'DEF', team: 'Liverpool', cost: 6.5, points: 180, injury_status: 'available' },
        { id: 4, name: 'White', position: 'DEF', team: 'Arsenal', cost: 4.5, points: 145, injury_status: 'available' },
        { id: 5, name: 'Salah', position: 'MID', team: 'Liverpool', cost: 13.0, points: 280, injury_status: 'available' },
        { id: 6, name: 'De Bruyne', position: 'MID', team: 'Man City', cost: 11.5, points: 245, injury_status: 'available' },
        { id: 7, name: 'Saka', position: 'MID', team: 'Arsenal', cost: 8.5, points: 195, injury_status: 'available' },
        { id: 8, name: 'Bowen', position: 'MID', team: 'West Ham', cost: 6.5, points: 155, injury_status: 'available' },
        { id: 9, name: 'Odegaard', position: 'MID', team: 'Arsenal', cost: 8.0, points: 180, injury_status: 'available' },
        { id: 10, name: 'Haaland', position: 'FWD', team: 'Man City', cost: 14.0, points: 320, injury_status: 'available' },
        { id: 11, name: 'Jesus', position: 'FWD', team: 'Arsenal', cost: 8.0, points: 185, injury_status: 'available' }
      ],
      total_cost: 98.5,
      total_points: 2280,
      remaining_budget: budget - 98.5,
      formation: formation,
      optimization_time: 2100,
      algorithm_used: 'linear_programming',
      confidence_score: 0.89,
      data_source: 'fpl_api'
    };
    
    // Simulate network delay (what a real API call would take)
    return of(mockResponse).pipe(delay(2200));
  }

  optimizeAdvanced(request: OptimizationRequest): Observable<OptimizationResult> {
    console.log(`Mock API call: POST /api/optimize-advanced`);
    console.log(`Request body:`, request);
    
    // Simulate what your Python backend would return for advanced optimization
    const mockResponse: OptimizationResult = {
      status: 'success',
      players: [
        { id: 1, name: 'Alisson', position: 'GKP', team: 'Liverpool', cost: 5.5, points: 185, injury_status: 'available' },
        { id: 2, name: 'Alexander-Arnold', position: 'DEF', team: 'Liverpool', cost: 7.5, points: 210, injury_status: 'available' },
        { id: 3, name: 'Gabriel', position: 'DEF', team: 'Arsenal', cost: 5.0, points: 155, injury_status: 'available' },
        { id: 4, name: 'White', position: 'DEF', team: 'Arsenal', cost: 4.5, points: 145, injury_status: 'available' },
        { id: 5, name: 'Salah', position: 'MID', team: 'Liverpool', cost: 13.0, points: 280, injury_status: 'available' },
        { id: 6, name: 'De Bruyne', position: 'MID', team: 'Man City', cost: 11.5, points: 245, injury_status: 'available' },
        { id: 7, name: 'Saka', position: 'MID', team: 'Arsenal', cost: 8.5, points: 195, injury_status: 'available' },
        { id: 8, name: 'Maddison', position: 'MID', team: 'Tottenham', cost: 7.0, points: 170, injury_status: 'available' },
        { id: 9, name: 'Martinelli', position: 'MID', team: 'Arsenal', cost: 7.0, points: 165, injury_status: 'available' },
        { id: 10, name: 'Haaland', position: 'FWD', team: 'Man City', cost: 14.0, points: 320, injury_status: 'available' },
        { id: 11, name: 'Watkins', position: 'FWD', team: 'Aston Villa', cost: 7.0, points: 165, injury_status: 'available' }
      ],
      total_cost: 97.0,
      total_points: 2235,
      remaining_budget: request.budget - 97.0,
      formation: request.formation,
      optimization_time: 3400,
      algorithm_used: request.algorithm || 'linear_programming',
      confidence_score: 0.93,
      data_source: 'fpl_api',
      constraints_applied: [
        {
          type: 'max_players_per_team',
          description: 'Maximum 3 players per team constraint applied',
          value: 3,
          applied: true,
          impact_score: 0.12
        },
        {
          type: 'exclude_players',
          description: 'Excluded injured/doubtful players',
          value: request.constraints?.exclude_injured || false,
          applied: request.constraints?.exclude_injured || false,
          impact_score: 0.05
        }
      ],
      warnings: request.constraints?.exclude_injured ? [
        {
          type: 'injury_risk',
          message: 'Excluded 3 players due to injury concerns',
          severity: 'low'
        }
      ] : []
    };
    
    // Simulate longer processing time for advanced optimization
    return of(mockResponse).pipe(delay(3500));
  }
}