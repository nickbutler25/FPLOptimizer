// src/app/services/statistics.service.ts (Real implementation - no mock needed)
import { Injectable } from '@angular/core';
import { Player, TeamStats } from '../../object-interfaces';
import { BUDGET_CONSTRAINTS, Formation } from '../../types/fpl.types';
import { StatisticsServiceInterface } from '../service-interfaces/statistics-service.interface';

@Injectable({
  providedIn: 'root'
})
export class StatisticsService implements StatisticsServiceInterface {

  calculateTeamStats(players: Player[], formation?: Formation, budget?: number): TeamStats {
    console.log('📊 Calculating team stats for', players.length, 'players');
    
    if (players.length === 0) {
      return this.getEmptyStats();
    }
    
    const totalCost = players.reduce((sum, p) => sum + p.cost, 0);
    const totalPoints = players.reduce((sum, p) => sum + p.points, 0);
    const usedBudget = budget || BUDGET_CONSTRAINTS.DEFAULT;
    
    // Count players by position
    const positionCount = {
      GKP: players.filter(p => p.position === 'GKP').length,
      DEF: players.filter(p => p.position === 'DEF').length,
      MID: players.filter(p => p.position === 'MID').length,
      FWD: players.filter(p => p.position === 'FWD').length
    };
    
    // Group players by team and calculate team stats
    const teamGroups = this.groupPlayersByTeam(players);
    const teamDistribution = Object.entries(teamGroups).map(([team, teamPlayers]) => ({
      team: team as any, // Cast to PremierLeagueTeam
      player_count: teamPlayers.length,
      total_cost: this.roundToDecimal(teamPlayers.reduce((sum, p) => sum + p.cost, 0)),
      total_points: teamPlayers.reduce((sum, p) => sum + p.points, 0),
      average_points_per_player: this.roundToDecimal(
        teamPlayers.reduce((sum, p) => sum + p.points, 0) / teamPlayers.length
      )
    })).filter(dist => dist.player_count > 0);
    
    // Calculate value metrics
    const valueMetrics = this.calculateValueMetrics(players, totalCost, totalPoints);
    
    return {
      total_cost: this.roundToDecimal(totalCost),
      total_points: totalPoints,
      remaining_budget: this.roundToDecimal(usedBudget - totalCost),
      average_points_per_player: this.roundToDecimal(totalPoints / players.length),
      formation: formation || '3-5-2',
      players_count: positionCount,
      team_distribution: teamDistribution,
      value_metrics: valueMetrics
    };
  }

  private groupPlayersByTeam(players: Player[]): Record<string, Player[]> {
    return players.reduce((acc, player) => {
      if (!acc[player.team]) {
        acc[player.team] = [];
      }
      acc[player.team].push(player);
      return acc;
    }, {} as Record<string, Player[]>);
  }

  private calculateValueMetrics(players: Player[], totalCost: number, totalPoints: number) {
    const sortedByCost = [...players].sort((a, b) => b.cost - a.cost);
    const sortedByValue = [...players].sort((a, b) => 
      (b.points_per_cost || b.points / b.cost) - (a.points_per_cost || a.points / a.cost)
    );
    const sortedByCheapest = [...players].sort((a, b) => a.cost - b.cost);
    
    // Calculate value efficiency score (0-10 scale)
    const pointsPerMillion = totalPoints / totalCost;
    const valueEfficiencyScore = Math.min(10, Math.max(0, 
      Math.round((pointsPerMillion - 15) / 5) // Rough scale: 15-20 pts/£m = 0-1, 20-25 = 1-2, etc.
    ));
    
    return {
      points_per_million: this.roundToDecimal(pointsPerMillion),
      best_value_player: sortedByValue[0]?.name || 'N/A',
      most_expensive_player: sortedByCost[0]?.name || 'N/A',
      cheapest_player: sortedByCheapest[0]?.name || 'N/A',
      value_efficiency_score: valueEfficiencyScore
    };
  }

  private getEmptyStats(): TeamStats {
    return {
      total_cost: 0,
      total_points: 0,
      remaining_budget: BUDGET_CONSTRAINTS.DEFAULT,
      average_points_per_player: 0,
      formation: '3-5-2',
      players_count: { GKP: 0, DEF: 0, MID: 0, FWD: 0 },
      team_distribution: [],
      value_metrics: {
        points_per_million: 0,
        best_value_player: 'N/A',
        most_expensive_player: 'N/A',
        cheapest_player: 'N/A',
        value_efficiency_score: 0
      }
    };
  }

  private roundToDecimal(value: number, decimals: number = 1): number {
    return Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals);
  }

  // Additional utility methods for advanced statistics
  calculatePositionAnalysis(players: Player[]) {
    const positions = ['GKP', 'DEF', 'MID', 'FWD'] as const;
    
    return positions.map(position => {
      const positionPlayers = players.filter(p => p.position === position);
      if (positionPlayers.length === 0) return null;
      
      const totalCost = positionPlayers.reduce((sum, p) => sum + p.cost, 0);
      const totalPoints = positionPlayers.reduce((sum, p) => sum + p.points, 0);
      
      return {
        position,
        player_count: positionPlayers.length,
        total_cost: this.roundToDecimal(totalCost),
        total_points: totalPoints,
        average_cost: this.roundToDecimal(totalCost / positionPlayers.length),
        average_points: this.roundToDecimal(totalPoints / positionPlayers.length),
        value_rating: this.roundToDecimal(totalPoints / totalCost)
      };
    }).filter(Boolean);
  }

  calculateRiskMetrics(players: Player[]) {
    const injuredCount = players.filter(p => 
      p.injury_status === 'injured' || p.injury_status === 'doubtful'
    ).length;
    
    const lowFormCount = players.filter(p => 
      (p.form || 0) < 5
    ).length;
    
    const highOwnershipCount = players.filter(p => 
      (p.selected_by_percent || 0) > 20
    ).length;
    
    return {
      injury_risk_score: Math.round((injuredCount / players.length) * 10) as any,
      form_risk_score: Math.round((lowFormCount / players.length) * 10) as any,
      ownership_risk_score: Math.round((highOwnershipCount / players.length) * 10) as any,
      overall_risk_score: Math.round(((injuredCount + lowFormCount) / (players.length * 2)) * 10) as any
    };
  }
}