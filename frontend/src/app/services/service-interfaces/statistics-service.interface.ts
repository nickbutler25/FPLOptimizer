import { Player, TeamStats } from "../../object-interfaces/";

export interface StatisticsServiceInterface {
  calculateTeamStats(players: Player[]): TeamStats;
}