"""Team service for business logic."""

import logging

from app.repositories.team_repository import TeamRepository
from app.models.team import Team

logger = logging.getLogger(__name__)


class TeamService:
    """Service for team-related business logic."""

    def __init__(self, team_repository: TeamRepository):
        """Initialize team service.

        Args:
            team_repository: Team repository instance
        """
        self.team_repository = team_repository

    async def get_team_by_id(self, team_id: int, include_picks: bool = True) -> Team:
        """Get team by ID with optional picks.

        Args:
            team_id: FPL team entry ID
            include_picks: Whether to include current team picks

        Returns:
            Team data with optional picks
        """
        logger.info(f"Getting team with ID: {team_id}, include_picks={include_picks}")
        team = await self.team_repository.get_team_by_id(team_id, include_picks)
        return team

    async def get_team_summary(self, team_id: int) -> dict:
        """Get team summary with key statistics.

        Args:
            team_id: FPL team entry ID

        Returns:
            Dictionary with team summary
        """
        logger.info(f"Getting team summary for ID: {team_id}")
        team = await self.team_repository.get_team_by_id(team_id, include_picks=True)

        # Get transfer information
        transfers_made = 0
        transfers_cost = 0
        free_transfers = 1  # Default
        if team.transfers and isinstance(team.transfers, dict):
            transfers_made = team.transfers.get("made", 0)
            transfers_cost = team.transfers.get("cost", 0)
            free_transfers = team.transfers.get("free_transfers", 1)

        summary = {
            "team_id": team.id,
            "team_name": team.name,
            "manager_name": f"{team.player_first_name} {team.player_last_name}",
            "overall_points": team.summary_overall_points,
            "overall_rank": team.summary_overall_rank,
            "gameweek_points": team.summary_event_points,
            "gameweek_rank": team.summary_event_rank,
            "team_value": team.team_value / 10,  # Convert to millions
            "bank": team.bank / 10,  # Convert to millions
            "total_transfers": team.total_transfers,
            "transfers_made_this_gw": transfers_made,  # Transfers made in last completed gameweek
            "transfers_cost_this_gw": transfers_cost,  # Points cost in last completed gameweek
            "free_transfers": free_transfers,  # Available free transfers for next gameweek
        }

        return summary
