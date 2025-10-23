from typing import Optional, List, Dict
import logging
from datetime import datetime

from app.domain.entities.player import Player
from app.domain.enums.position import Position
from app.domain.enums.injury_status import InjuryStatus
from app.repositories.players.fpl_player_repository import FPLPlayerRepository
from app.services.players.players_data_mapping_service import PlayersDataMappingService
from app.services.players.players_filter_service import PlayerFilterService
from app.schemas.requests.players_request import GetPlayersRequestDTO
from app.schemas.internal.filters import PlayerFiltersDTO
from app.schemas.responses.players_response import PlayersResponseDTO, PlayerDTO


class PlayersBusinessService:
    """
    Business service that orchestrates data access and business logic
    """

    def __init__(self, repository):
        self.repository = repository  # Pure data access
        self.mapper = PlayersDataMappingService()  # Business mapping
        self.filter_service = PlayerFilterService()  # Business filtering
        self.logger = logging.getLogger(__name__)

    async def get_players(self, request: GetPlayersRequestDTO) -> PlayersResponseDTO:
        """
        Business method: Get players with business logic applied
        """
        self.logger.info("Business: Processing players request")

        try:
            # 1. Get raw data from repository (data access)
            bootstrap_data = await self.repository.get_bootstrap_data()

            # 2. Map to domain models (business logic)
            players = self.mapper.map_bootstrap_to_players(bootstrap_data)

            # 3. Convert request DTO to internal filter DTO
            filters = self._convert_request_to_filters(request)

            # 4. Apply business filters (business logic)
            if filters:
                players = self.filter_service.apply_filters(players, filters)

            # 5. Apply business validations (business logic)
            valid_players = [p for p in players if self._is_valid_player(p)]

            # 6. Convert to response DTOs
            player_dtos = [self._convert_player_to_dto(player) for player in valid_players]

            return PlayersResponseDTO(
                status="success",
                players=player_dtos,
                total_count=len(player_dtos),
                filters_applied=self._get_filters_summary(request),
                data_source="FPL_API"
            )

        except Exception as e:
            self.logger.error(f"Business: Error getting players: {e}")
            raise

    async def get_player(self, player_id: int):
        """Get single player with business logic"""
        self.logger.info(f"Business: Getting player {player_id}")

        # For now, use the same logic but filter by ID
        # You can optimize this later to fetch single player
        request = GetPlayersRequestDTO()
        response = await self.get_players(request)

        player = next((p for p in response.players if p.id == player_id), None)
        if not player:
            from app.core.exceptions import PlayerNotFoundException
            raise PlayerNotFoundException(f"Player {player_id} not found")

        return {
            "status": "success",
            "data": player,
            "metadata": {"data_source": "FPL_API"}
        }

    def _convert_request_to_filters(self, request: GetPlayersRequestDTO) -> PlayerFiltersDTO:
        """
        Convert API request DTO to internal filter DTO
        This handles the mapping and provides defaults
        """
        # Convert position strings to enums
        positions = None
        if request.positions:
            position_mapping = {
                "GKP": Position.GKP,
                "DEF": Position.DEF,
                "MID": Position.MID,
                "FWD": Position.FWD
            }
            positions = [position_mapping.get(pos, Position.MID) for pos in request.positions]

        # Handle available_only -> injury_status conversion
        injury_status = None
        if request.available_only:
            injury_status = [InjuryStatus.AVAILABLE]

        return PlayerFiltersDTO(
            positions=positions,
            teams=request.teams,
            min_cost=request.min_cost,
            max_cost=request.max_cost,
            min_points=request.min_points,
            max_points=request.max_points,
            min_form=request.min_form,
            injury_status=injury_status,  # This is the key fix!
            available_only=request.available_only,
            min_minutes=request.min_minutes,
            min_selected_percent=request.min_selected_percent,
            max_selected_percent=request.max_selected_percent,
            search_term=request.search_term
        )

    def _convert_player_to_dto(self, player: Player) -> PlayerDTO:
        """Convert domain Player to response DTO"""
        return PlayerDTO(
            id=player.id,
            name=player.name,
            web_name=player.web_name,
            position=player.position,
            team=player.team,
            cost=player.cost,
            points=player.points,
            points_per_cost=player.points_per_cost,
            form=player.form,
            minutes=player.minutes,
            goals_scored=player.goals_scored,
            assists=player.assists,
            clean_sheets=player.clean_sheets,
            bonus=player.bonus,
            selected_by_percent=player.selected_by_percent,
            transfers_in=player.transfers_in,
            transfers_out=player.transfers_out,
            injury_status=player.injury_status
        )

    def _get_filters_summary(self, request: GetPlayersRequestDTO) -> Dict:
        """Get summary of applied filters for response"""
        summary = {}
        if request.positions:
            summary["positions"] = request.positions
        if request.teams:
            summary["teams"] = request.teams
        if request.min_cost:
            summary["min_cost"] = request.min_cost
        if request.max_cost:
            summary["max_cost"] = request.max_cost
        if request.available_only:
            summary["available_only"] = request.available_only
        return summary

    def _is_valid_player(self, player: Player) -> bool:
        """Business rule: What constitutes a valid player"""
        return (
                player.id and player.id > 0 and
                player.name and len(player.name.strip()) > 0 and
                player.cost >= 3.0 and player.cost <= 15.0 and
                player.points >= 0
        )