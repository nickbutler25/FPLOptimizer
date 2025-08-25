"""
Player Validation Service - Centralized business validation logic
"""

from typing import List, Optional
from app.schemas.requests.players import GetPlayersRequestDTO
from app.core.exceptions import ValidationError


class PlayerValidationService:
    """
    Centralized validation service for all player-related business rules
    """

    async def validate_get_players_request(self, request: GetPlayersRequestDTO) -> None:
        """
        Validate get players request according to business rules
        """
        errors = []

        # Business Rule: Cost range validation
        if (request.min_cost is not None and request.max_cost is not None and
                request.min_cost > request.max_cost):
            errors.append({
                "field": "cost_range",
                "message": "min_cost cannot be greater than max_cost",
                "min_cost": request.min_cost,
                "max_cost": request.max_cost
            })

        # Business Rule: Points range validation
        if (request.min_points is not None and request.max_points is not None and
                request.min_points > request.max_points):
            errors.append({
                "field": "points_range",
                "message": "min_points cannot be greater than max_points"
            })

        # Business Rule: Ownership range validation
        if (request.min_selected_percent is not None and request.max_selected_percent is not None and
                request.min_selected_percent > request.max_selected_percent):
            errors.append({
                "field": "ownership_range",
                "message": "min_selected_percent cannot be greater than max_selected_percent"
            })

        # Business Rule: Cost limits
        if request.min_cost is not None and (request.min_cost < 3.0 or request.min_cost > 15.0):
            errors.append({
                "field": "min_cost",
                "message": "min_cost must be between 3.0 and 15.0"
            })

        if request.max_cost is not None and (request.max_cost < 3.0 or request.max_cost > 15.0):
            errors.append({
                "field": "max_cost",
                "message": "max_cost must be between 3.0 and 15.0"
            })

        # Business Rule: Form rating limits
        if request.min_form is not None and (request.min_form < 0 or request.min_form > 10):
            errors.append({
                "field": "min_form",
                "message": "min_form must be between 0 and 10"
            })

        # Business Rule: Team names validation
        if request.teams:
            for team in request.teams:
                if not team.strip():
                    errors.append({
                        "field": "teams",
                        "message": "Team names cannot be empty"
                    })
                    break

        # Business Rule: Search term length
        if request.search_term and len(request.search_term.strip()) < 2:
            errors.append({
                "field": "search_term",
                "message": "Search term must be at least 2 characters"
            })

        # If we have validation errors, raise them
        if errors:
            raise ValidationError(
                message="Request validation failed",
                field_errors=errors
            )

    async def validate_player_id(self, player_id: int) -> None:
        """
        Validate player ID according to business rules
        """
        # Business Rule: Player ID must be positive
        if player_id <= 0:
            raise ValidationError(
                message="Invalid player ID",
                field="player_id",
                details="Player ID must be a positive integer"
            )

        # Business Rule: Player ID reasonable range (FPL has ~600 players)
        if player_id > 1000:
            raise ValidationError(
                message="Invalid player ID",
                field="player_id",
                details="Player ID is outside expected range"
            )