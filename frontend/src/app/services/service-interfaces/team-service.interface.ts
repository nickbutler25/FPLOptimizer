// Team service interface
import { Observable } from 'rxjs';
import { Team, TeamResponse, TeamSummary, TeamSummaryResponse } from '../../object-interfaces/team.interface';

export interface TeamServiceInterface {
  /**
   * Get FPL team by ID
   * @param teamId - FPL team entry ID
   * @param includePicks - Whether to include current team picks
   */
  getTeamById(teamId: number, includePicks?: boolean): Observable<TeamResponse>;

  /**
   * Get team summary with key statistics
   * @param teamId - FPL team entry ID
   */
  getTeamSummary(teamId: number): Observable<TeamSummaryResponse>;
}