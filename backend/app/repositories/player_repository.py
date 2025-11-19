"""Player repository for accessing FPL player data."""

import logging
from typing import List, Optional

from app.infrastructure.http.fpl_client import FPLClient
from app.infrastructure.cache.redis_cache import RedisCache
from app.models.player import Player
from app.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class PlayerRepository:
    """Repository for FPL player data."""

    CACHE_KEY_ALL_PLAYERS = "fpl:players:all"
    CACHE_KEY_PLAYER = "fpl:player:{player_id}"

    def __init__(self, fpl_client: FPLClient, cache: RedisCache):
        """Initialize player repository.

        Args:
            fpl_client: FPL API client
            cache: Redis cache instance
        """
        self.fpl_client = fpl_client
        self.cache = cache

    async def get_all_players(self) -> List[Player]:
        """Get all available FPL players.

        Returns:
            List of all players

        Raises:
            ExternalAPIException: If FPL API request fails
        """
        # Try cache first
        cached_data = await self.cache.get(self.CACHE_KEY_ALL_PLAYERS)
        if cached_data:
            logger.info("Retrieved all players from cache")
            return [Player(**player) for player in cached_data]

        # Fetch from API
        logger.info("Fetching all players from FPL API")
        bootstrap_data = await self.fpl_client.get_bootstrap_static()

        # Extract players and teams for name mapping
        players_data = bootstrap_data.get("elements", [])
        teams_data = bootstrap_data.get("teams", [])
        element_types = bootstrap_data.get("element_types", [])

        # Create lookup dictionaries
        teams_lookup = {team["id"]: team["name"] for team in teams_data}
        position_lookup = {pos["id"]: pos["singular_name"] for pos in element_types}

        # Enrich player data with team and position names
        enriched_players = []
        for player_data in players_data:
            player_data["team_name"] = teams_lookup.get(player_data["team"])
            player_data["position"] = position_lookup.get(player_data["element_type"])
            enriched_players.append(player_data)

        # Convert to Player models
        players = [Player(**player) for player in enriched_players]

        # Cache the results
        await self.cache.set(
            self.CACHE_KEY_ALL_PLAYERS,
            [player.model_dump() for player in players],
            ttl=300,  # Cache for 5 minutes
        )

        logger.info(f"Retrieved {len(players)} players from FPL API")
        return players

    async def get_player_by_id(self, player_id: int) -> Optional[Player]:
        """Get a specific player by ID.

        Args:
            player_id: Player ID

        Returns:
            Player if found, None otherwise
        """
        cache_key = self.CACHE_KEY_PLAYER.format(player_id=player_id)

        # Try cache first
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            logger.info(f"Retrieved player {player_id} from cache")
            return Player(**cached_data)

        # Get all players and filter
        all_players = await self.get_all_players()
        player = next((p for p in all_players if p.id == player_id), None)

        if player:
            # Cache individual player
            await self.cache.set(cache_key, player.model_dump(), ttl=300)
            logger.info(f"Retrieved player {player_id} from API")

        return player
