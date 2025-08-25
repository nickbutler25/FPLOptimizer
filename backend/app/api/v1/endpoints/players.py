"""
Players API Endpoints - MINIMAL validation, focus on HTTP concerns
"""

from typing import Optional
from fastapi import APIRouter, Query, Path, HTTPException, status
import logging

from app.api.dependencies import PlayersServiceDep

from app.core.exceptions import ValidationError, PlayerNotFoundException, FPLAPIException

# Create router
router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/",
    response_model=PlayersResponseDTO,
    summary="Get filtered players",
    description="Get a filtered list of players from the official FPL API."
)
async def get_players(
        # MINIMAL validation here - just HTTP parameter parsing
        positions: Optional[str] = Query(None, description="Comma-separated positions (GKP,DEF,MID,FWD)"),
        teams: Optional[str] = Query(None, description="Comma-separated team names"),
        min_cost: Optional[float] = Query(None, description="Minimum player cost"),
        max_cost: Optional[float] = Query(None, description="Maximum player cost"),
        min_points: Optional[int] = Query(None, description="Minimum total points"),
        max_points: Optional[int] = Query(None, description="Maximum total points"),
        min_form: Optional[float] = Query(None, description="Minimum form rating"),
        available_only: Optional[bool] = Query(False, description="Only available players"),
        min_minutes: Optional[int] = Query(None, description="Minimum minutes played"),
        min_selected_percent: Optional[float] = Query(None, description="Minimum ownership %"),
        max_selected_percent: Optional[float] = Query(None, description="Maximum ownership %"),
        search_term: Optional[str] = Query(None, description="Search term"),

        # Dependency injection
        service: PlayersServiceDep
):
    """
    API Layer: Minimal validation, just HTTP parameter parsing and delegation to business layer
    """
    try:
        # Create request DTO with raw parameters
        # NO business validation here - just pass the parameters
        request_dto = GetPlayersRequestDTO(
            positions=positions.split(',') if positions else None,
            teams=teams.split(',') if teams else None,
            min_cost=min_cost,
            max_cost=max_cost,
            min_points=min_points,
            max_points=max_points,
            min_form=min_form,
            available_only=available_only,
            min_minutes=min_minutes,
            min_selected_percent=min_selected_percent,
            max_selected_percent=max_selected_percent,
            search_term=search_term
        )

        logger.info(f"API: Received request for players with filters")

        # Delegate to business service - ALL validation happens there
        result = await service.get_players(request_dto)

        return result

    except ValidationError as e:
        # Business layer validation errors
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.to_dict()
        )

    except FPLAPIException as e:
        logger.error(f"FPL API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"message": "FPL API unavailable", "details": str(e)}
        )

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"}
        )


@router.get("/{player_id}", response_model=PlayerDetailResponseDTO)
async def get_player(
        player_id: int = Path(..., ge=1, description="Player ID"),
        service: PlayersServiceDep
):
    """
    API Layer: Minimal validation, delegate to business layer
    """
    try:
        logger.info(f"API: Received request for player {player_id}")

        # Delegate to business service
        result = await service.get_player(player_id)

        return result

    except PlayerNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"Player with ID {player_id} not found"}
        )

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"}
        )