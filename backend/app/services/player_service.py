"""Player service for business logic."""

import logging
from typing import List, Optional

from app.repositories.player_repository import PlayerRepository
from app.models.player import Player
from app.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class PlayerService:
    """Service for player-related business logic."""

    def __init__(self, player_repository: PlayerRepository):
        """Initialize player service.

        Args:
            player_repository: Player repository instance
        """
        self.player_repository = player_repository

    async def get_all_players(
        self,
        position: Optional[str] = None,
        team_id: Optional[int] = None,
        min_cost: Optional[float] = None,
        max_cost: Optional[float] = None,
    ) -> List[Player]:
        """Get all players with optional filters.

        Args:
            position: Filter by position name
            team_id: Filter by team ID
            min_cost: Minimum cost in millions
            max_cost: Maximum cost in millions

        Returns:
            List of players matching filters
        """
        logger.info(
            f"Getting all players with filters: position={position}, "
            f"team_id={team_id}, min_cost={min_cost}, max_cost={max_cost}"
        )

        # Get all players
        players = await self.player_repository.get_all_players()

        # Apply filters
        if position:
            players = [p for p in players if p.position == position]

        if team_id:
            players = [p for p in players if p.team == team_id]

        if min_cost is not None:
            min_cost_units = int(min_cost * 10)  # Convert to 0.1m units
            players = [p for p in players if p.now_cost >= min_cost_units]

        if max_cost is not None:
            max_cost_units = int(max_cost * 10)  # Convert to 0.1m units
            players = [p for p in players if p.now_cost <= max_cost_units]

        logger.info(f"Retrieved {len(players)} players after filtering")
        return players

    async def get_player_by_id(self, player_id: int) -> Player:
        """Get player by ID.

        Args:
            player_id: Player ID

        Returns:
            Player data

        Raises:
            NotFoundException: If player not found
        """
        logger.info(f"Getting player with ID: {player_id}")
        player = await self.player_repository.get_player_by_id(player_id)

        if not player:
            raise NotFoundException(f"Player with ID {player_id} not found")

        return player

    async def get_top_players_by_points(self, limit: int = 10) -> List[Player]:
        """Get top players by total points.

        Args:
            limit: Number of players to return

        Returns:
            List of top players
        """
        logger.info(f"Getting top {limit} players by points")
        players = await self.player_repository.get_all_players()

        # Sort by total points descending
        sorted_players = sorted(players, key=lambda p: p.total_points, reverse=True)

        return sorted_players[:limit]
