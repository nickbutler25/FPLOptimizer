from typing import Optional, List, Dict
import logging
from datetime import datetime

from app.domain.entities.player import Player
from app.repositories.players.fpl_player_repository import FPLPlayerRepository
from app.services.players.players_data_mapping_service import PlayersDataMappingService
from app.services.players.players_filter_service import PlayerFilterService


class PlayersBusinessService:
    """
    Business service that orchestrates data access and business logic
    """

    def __init__(self, repository: FPLPlayerRepository):
        self.repository = repository  # Pure data access
        self.mapper = PlayersDataMappingService()  # Business mapping
        self.filter_service = PlayerFilterService()  # Business filtering
        self.logger = logging.getLogger(__name__)

    async def get_players(self, filters: Optional[Dict] = None) -> List[Player]:
        """
        Business method: Get players with business logic applied
        """
        # 1. Get raw data from repository (data access)
        bootstrap_data = await self.repository.get_bootstrap_data()

        # 2. Map to domain models (business logic)
        players = self.mapper.map_bootstrap_to_players(bootstrap_data)

        # 3. Apply business filters (business logic)
        if filters:
            players = self.filter_service.apply_filters(players, filters)

        # 4. Apply business validations (business logic)
        valid_players = [p for p in players if self._is_valid_player(p)]

        return valid_players

    async def get_player(self, player_id: int) -> Optional[Player]:
        """Get single player with business logic"""
        players = await self.get_players()
        return next((p for p in players if p.id == player_id), None)

    def _is_valid_player(self, player: Player) -> bool:
        """Business rule: What constitutes a valid player"""
        return (
                player.id and player.id > 0 and
                player.name and len(player.name.strip()) > 0 and
                player.cost >= 3.0 and player.cost <= 15.0 and
                player.points >= 0
        )