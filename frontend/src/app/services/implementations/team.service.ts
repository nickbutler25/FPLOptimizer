// Team service implementation
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map, timeout } from 'rxjs/operators';

import { ConfigService } from '../../config/config.service';
import { TeamServiceInterface } from '../service-interfaces/team-service.interface';
import { Team, TeamResponse, TeamSummary, TeamSummaryResponse, TransferPlanResponse } from '../../object-interfaces/team.interface';

@Injectable({
  providedIn: 'root'
})
export class TeamService implements TeamServiceInterface {
  private readonly apiUrl: string;
  private readonly apiKey = 'dev-api-key-change-in-production'; // Should match backend .env

  constructor(
    private http: HttpClient,
    private config: ConfigService
  ) {
    this.apiUrl = `${this.config.apiBaseUrl}/teams`;
  }

  /**
   * Get HTTP headers with API key
   */
  private getHeaders(): HttpHeaders {
    return new HttpHeaders({
      'X-API-Key': this.apiKey,
      'Content-Type': 'application/json'
    });
  }

  /**
   * Get FPL team by ID
   */
  getTeamById(teamId: number, includePicks: boolean = true): Observable<TeamResponse> {
    let params = new HttpParams();
    params = params.set('include_picks', includePicks.toString());

    return this.http.get<TeamResponse>(`${this.apiUrl}/${teamId}`, {
      headers: this.getHeaders(),
      params
    }).pipe(
      timeout(this.config.apiTimeout),
      map(response => {
        if (this.config.shouldLogToConsole) {
          console.log('✅ Team data received:', response);
        }
        return response;
      }),
      catchError(error => {
        console.error('❌ Error fetching team:', error);
        return throwError(() => new Error(
          error.status === 404
            ? `Team with ID ${teamId} not found`
            : `Failed to fetch team data: ${error.message}`
        ));
      })
    );
  }

  /**
   * Get team summary with key statistics
   */
  getTeamSummary(teamId: number): Observable<TeamSummaryResponse> {
    return this.http.get<TeamSummaryResponse>(`${this.apiUrl}/${teamId}/summary`, {
      headers: this.getHeaders()
    }).pipe(
      timeout(this.config.apiTimeout),
      map(response => {
        if (this.config.shouldLogToConsole) {
          console.log('✅ Team summary received:', response);
        }
        return response;
      }),
      catchError(error => {
        console.error('❌ Error fetching team summary:', error);
        return throwError(() => new Error(
          error.status === 404
            ? `Team with ID ${teamId} not found`
            : `Failed to fetch team summary: ${error.message}`
        ));
      })
    );
  }

  /**
   * Generate transfer plan for N gameweeks
   */
  generateTransferPlan(
    teamId: number,
    numGameweeks: number = 5,
    freeTransfers: number = 3,
    discountFactor: number = 0.9
  ): Observable<TransferPlanResponse> {
    let params = new HttpParams();
    params = params.set('num_gameweeks', numGameweeks.toString());
    params = params.set('free_transfers', freeTransfers.toString());
    params = params.set('discount_factor', discountFactor.toString());

    return this.http.post<TransferPlanResponse>(
      `${this.apiUrl}/${teamId}/transfer-plan`,
      null,
      {
        headers: this.getHeaders(),
        params
      }
    ).pipe(
      timeout(60000), // 60 second timeout for solver
      map(response => {
        if (this.config.shouldLogToConsole) {
          console.log('✅ Transfer plan received:', response);
        }
        return response;
      }),
      catchError(error => {
        console.error('❌ Error generating transfer plan:', error);
        return throwError(() => new Error(
          error.status === 404
            ? `Team with ID ${teamId} not found`
            : error.status === 408 || error.name === 'TimeoutError'
            ? 'Transfer plan generation timed out. Please try again with fewer gameweeks.'
            : `Failed to generate transfer plan: ${error.message}`
        ));
      })
    );
  }
}