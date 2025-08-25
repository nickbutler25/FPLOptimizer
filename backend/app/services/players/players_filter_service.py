"""
Player Filter Service - Business Layer Filtering Logic
Centralized filtering logic with business rules and performance optimization
"""

import logging
from typing import List, Optional, Callable, Any, Dict
from functools import reduce

from app.domain.entities.player import Player
from app.domain.enums.position import Position
from app.domain.enums.injury_status import InjuryStatus
from app.schemas.internal.filters import PlayerFiltersDTO


class PlayerFilterService:
    """
    Business service responsible for applying filters to player data.

    This is a BUSINESS concern because:
    - Contains business rules about what constitutes valid filters
    - Implements business logic for complex filter combinations
    - Handles business-specific search functionality
    - Optimizes filter performance based on business priorities
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def apply_filters(self, players: List[Player], filters: PlayerFiltersDTO) -> List[Player]:
        """
        Apply business filters to player list with performance optimization.

        Business Logic:
        - Applies filters in order of selectivity (most restrictive first)
        - Implements business rules for filter combinations
        - Handles edge cases and null values according to business requirements
        """
        if not filters:
            return players

        if not players:
            return []

        self.logger.debug(f"Applying filters to {len(players)} players")

        # Apply filters in order of selectivity (most restrictive first for performance)
        filtered_players = players

        # 1. Position filter (usually most selective)
        if filters.positions:
            filtered_players = self._filter_by_positions(filtered_players, filters.positions)
            self.logger.debug(f"After position filter: {len(filtered_players)} players")

        # 2. Availability filter (highly selective)
        if filters.available_only:
            filtered_players = self._filter_by_availability(filtered_players)
            self.logger.debug(f"After availability filter: {len(filtered_players)} players")

        # 3. Injury status filter
        if filters.injury_status:
            filtered_players = self._filter_by_injury_status(filtered_players, filters.injury_status)
            self.logger.debug(f"After injury status filter: {len(filtered_players)} players")

        # 4. Team filters
        if filters.teams:
            filtered_players = self._filter_by_teams(filtered_players, filters.teams)
            self.logger.debug(f"After team filter: {len(filtered_players)} players")

        # 5. Cost range filters
        if filters.min_cost is not None or filters.max_cost is not None:
            filtered_players = self._filter_by_cost_range(
                filtered_players, filters.min_cost, filters.max_cost
            )
            self.logger.debug(f"After cost filter: {len(filtered_players)} players")

        # 6. Points range filters
        if filters.min_points is not None or filters.max_points is not None:
            filtered_players = self._filter_by_points_range(
                filtered_players, filters.min_points, filters.max_points
            )
            self.logger.debug(f"After points filter: {len(filtered_players)} players")

        # 7. Form filter
        if filters.min_form is not None:
            filtered_players = self._filter_by_form(filtered_players, filters.min_form)
            self.logger.debug(f"After form filter: {len(filtered_players)} players")

        # 8. Minutes filter
        if filters.min_minutes is not None:
            filtered_players = self._filter_by_minutes(filtered_players, filters.min_minutes)
            self.logger.debug(f"After minutes filter: {len(filtered_players)} players")

        # 9. Ownership percentage filters
        if filters.min_selected_percent is not None or filters.max_selected_percent is not None:
            filtered_players = self._filter_by_ownership_range(
                filtered_players, filters.min_selected_percent, filters.max_selected_percent
            )
            self.logger.debug(f"After ownership filter: {len(filtered_players)} players")

        # 10. Search term filter (least selective, applied last)
        if filters.search_term:
            filtered_players = self._filter_by_search_term(filtered_players, filters.search_term)
            self.logger.debug(f"After search filter: {len(filtered_players)} players")

        self.logger.info(f"Filtering complete: {len(players)} → {len(filtered_players)} players")
        return filtered_players

    # ===== INDIVIDUAL FILTER METHODS =====

    def _filter_by_positions(self, players: List[Player], positions: List[Position]) -> List[Player]:
        """
        Business Logic: Filter players by position.
        Only includes players whose position is in the allowed list.
        """
        return [player for player in players if player.position in positions]

    def _filter_by_teams(self, players: List[Player], teams: List[str]) -> List[Player]:
        """
        Business Logic: Filter players by team names.
        Case-insensitive matching for better user experience.
        """
        # Convert to lowercase for case-insensitive matching (business decision)
        team_names_lower = [team.lower() for team in teams]

        return [
            player for player in players
            if player.team.lower() in team_names_lower
        ]

    def _filter_by_availability(self, players: List[Player]) -> List[Player]:
        """
        Business Logic: Filter to only available players.
        Business rule: "Available" means injury_status == AVAILABLE.
        """
        return [
            player for player in players
            if player.injury_status == InjuryStatus.AVAILABLE
        ]

    def _filter_by_injury_status(self, players: List[Player], allowed_statuses: List[InjuryStatus]) -> List[Player]:
        """
        Business Logic: Filter by specific injury statuses.
        Allows more granular control than just "available_only".
        """
        return [
            player for player in players
            if player.injury_status in allowed_statuses
        ]

    def _filter_by_cost_range(
            self,
            players: List[Player],
            min_cost: Optional[float],
            max_cost: Optional[float]
    ) -> List[Player]:
        """
        Business Logic: Filter players by cost range.
        Handles edge cases where min/max might be None.
        """
        filtered = players

        if min_cost is not None:
            filtered = [player for player in filtered if player.cost >= min_cost]

        if max_cost is not None:
            filtered = [player for player in filtered if player.cost <= max_cost]

        return filtered

    def _filter_by_points_range(
            self,
            players: List[Player],
            min_points: Optional[int],
            max_points: Optional[int]
    ) -> List[Player]:
        """
        Business Logic: Filter players by points range.
        """
        filtered = players

        if min_points is not None:
            filtered = [player for player in filtered if player.points >= min_points]

        if max_points is not None:
            filtered = [player for player in filtered if player.points <= max_points]

        return filtered

    def _filter_by_form(self, players: List[Player], min_form: float) -> List[Player]:
        """
        Business Logic: Filter players by minimum form rating.
        Business rule: Players with no form data (None) are excluded.
        """
        return [
            player for player in players
            if player.form is not None and player.form >= min_form
        ]

    def _filter_by_minutes(self, players: List[Player], min_minutes: int) -> List[Player]:
        """
        Business Logic: Filter players by minimum minutes played.
        Business rule: Players with no minutes data (None) are excluded.
        """
        return [
            player for player in players
            if player.minutes is not None and player.minutes >= min_minutes
        ]

    def _filter_by_ownership_range(
            self,
            players: List[Player],
            min_percent: Optional[float],
            max_percent: Optional[float]
    ) -> List[Player]:
        """
        Business Logic: Filter players by ownership percentage range.
        Useful for finding differentials (low ownership) or popular picks (high ownership).
        """
        filtered = players

        if min_percent is not None:
            filtered = [
                player for player in filtered
                if player.selected_by_percent is not None and player.selected_by_percent >= min_percent
            ]

        if max_percent is not None:
            filtered = [
                player for player in filtered
                if player.selected_by_percent is not None and player.selected_by_percent <= max_percent
            ]

        return filtered

    def _filter_by_search_term(self, players: List[Player], search_term: str) -> List[Player]:
        """
        Business Logic: Filter players by search term.

        Business rules:
        - Case-insensitive search
        - Searches in: player name, web name, team name
        - Partial matches allowed
        - Minimum 2 characters for performance
        """
        if not search_term or len(search_term.strip()) < 2:
            return players

        term = search_term.strip().lower()

        def matches_search(player: Player) -> bool:
            """Check if player matches search term"""
            # Search in player name
            if term in player.name.lower():
                return True

            # Search in web name (short name)
            if player.web_name and term in player.web_name.lower():
                return True

            # Search in team name
            if term in player.team.lower():
                return True

            return False

        return [player for player in players if matches_search(player)]

    # ===== ADVANCED FILTERING METHODS =====

    def apply_custom_filter(
            self,
            players: List[Player],
            filter_func: Callable[[Player], bool]
    ) -> List[Player]:
        """
        Apply a custom filter function to players.
        Useful for complex business rules that don't fit standard filters.
        """
        try:
            return [player for player in players if filter_func(player)]
        except Exception as e:
            self.logger.error(f"Custom filter failed: {str(e)}")
            return players  # Return unfiltered on error

    def get_value_players(
            self,
            players: List[Player],
            min_points_per_cost: float = 15.0
    ) -> List[Player]:
        """
        Business Logic: Get "value" players based on points per cost ratio.

        Business rule: Value players have high points-per-cost ratio.
        Default threshold: 15 points per million.
        """
        return [
            player for player in players
            if (player.points_per_cost is not None and
                player.points_per_cost >= min_points_per_cost)
        ]

    def get_differential_players(
            self,
            players: List[Player],
            max_ownership: float = 5.0
    ) -> List[Player]:
        """
        Business Logic: Get "differential" players (low ownership).

        Business rule: Differentials have low selection percentage.
        Default threshold: Less than 5% ownership.
        """
        return [
            player for player in players
            if (player.selected_by_percent is not None and
                player.selected_by_percent <= max_ownership)
        ]

    def get_premium_players(
            self,
            players: List[Player],
            min_cost: float = 10.0
    ) -> List[Player]:
        """
        Business Logic: Get "premium" players (expensive players).

        Business rule: Premium players cost 10.0m or more.
        """
        return [
            player for player in players
            if player.cost >= min_cost
        ]

    def get_budget_players(
            self,
            players: List[Player],
            max_cost: float = 5.0
    ) -> List[Player]:
        """
        Business Logic: Get "budget" players (cheap enablers).

        Business rule: Budget players cost 5.0m or less.
        """
        return [
            player for player in players
            if player.cost <= max_cost
        ]

    def get_in_form_players(
            self,
            players: List[Player],
            min_form: float = 7.0
    ) -> List[Player]:
        """
        Business Logic: Get players in good form.

        Business rule: Good form is 7.0+ on FPL's form rating.
        """
        return [
            player for player in players
            if player.form is not None and player.form >= min_form
        ]

    # ===== FILTER COMBINATION METHODS =====

    def get_rotation_proof_players(self, players: List[Player]) -> List[Player]:
        """
        Business Logic: Get players likely to play consistently.

        Business rules:
        - High minutes played (indicates regular starter)
        - Available (not injured/suspended)
        - Good recent form
        """
        return [
            player for player in players
            if (player.minutes is not None and player.minutes >= 1000 and  # Regular starter
                player.injury_status == InjuryStatus.AVAILABLE and  # Available
                player.form is not None and player.form >= 5.0)  # Decent form
        ]

    def get_captain_candidates(self, players: List[Player]) -> List[Player]:
        """
        Business Logic: Get players suitable for captaincy.

        Business rules:
        - High points total (proven performers)
        - Available to play
        - Not budget players (premiums more likely to score big)
        """
        return [
            player for player in players
            if (player.points >= 100 and  # High points
                player.injury_status == InjuryStatus.AVAILABLE and  # Available
                player.cost >= 8.0)  # Not budget players
        ]

    # ===== PERFORMANCE OPTIMIZATION METHODS =====

    def apply_filters_optimized(
            self,
            players: List[Player],
            filters: PlayerFiltersDTO
    ) -> List[Player]:
        """
        Performance-optimized filtering using generator expressions.
        For large datasets, this can be more memory efficient.
        """
        if not filters:
            return players

        # Chain filters as generator expressions for memory efficiency
        result = iter(players)

        if filters.positions:
            result = (p for p in result if p.position in filters.positions)

        if filters.available_only:
            result = (p for p in result if p.injury_status == InjuryStatus.AVAILABLE)

        if filters.teams:
            team_names_lower = [team.lower() for team in filters.teams]
            result = (p for p in result if p.team.lower() in team_names_lower)

        if filters.min_cost is not None:
            result = (p for p in result if p.cost >= filters.min_cost)

        if filters.max_cost is not None:
            result = (p for p in result if p.cost <= filters.max_cost)

        # Convert back to list at the end
        return list(result)

    # ===== UTILITY METHODS =====

    def get_filter_summary(self, filters: PlayerFiltersDTO) -> Dict[str, Any]:
        """
        Get a summary of applied filters for logging/debugging.
        """
        summary = {}

        if filters.positions:
            summary["positions"] = [pos.value for pos in filters.positions]

        if filters.teams:
            summary["teams"] = filters.teams

        if filters.min_cost is not None or filters.max_cost is not None:
            summary["cost_range"] = {
                "min": filters.min_cost,
                "max": filters.max_cost
            }

        if filters.available_only:
            summary["available_only"] = True

        if filters.search_term:
            summary["search_term"] = filters.search_term

        return summary

    def estimate_filter_selectivity(self, players: List[Player], filters: PlayerFiltersDTO) -> float:
        """
        Estimate how selective the filters will be (what % of players will remain).
        Useful for query planning and performance optimization.
        """
        if not filters or not players:
            return 1.0

        # Simple heuristic based on filter types
        selectivity = 1.0

        if filters.positions:
            # Positions are usually quite selective
            selectivity *= len(filters.positions) / 4  # 4 total positions

        if filters.available_only:
            # Availability filter is moderately selective
            selectivity *= 0.85  # Assume ~85% of players are available

        if filters.min_cost is not None and filters.max_cost is not None:
            # Cost range can be very selective
            range_size = filters.max_cost - filters.min_cost
            total_range = 12.0  # Rough estimate of FPL cost range
            selectivity *= min(1.0, range_size / total_range)

        return max(0.01, selectivity)  # Minimum 1% selectivity

