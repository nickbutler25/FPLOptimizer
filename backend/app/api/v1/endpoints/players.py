"""Player endpoints."""

import logging
from typing import Optional, List
from fastapi import APIRouter, Query, Depends

from app.api.dependencies import PlayerServiceDep
from app.schemas.responses import PlayersResponse, BaseResponse
from app.models.player import Player
from app.models.player_with_fixtures import PlayerWithFixtures
from app.core.security import verify_api_key
from app.core.container import container

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/players",
    response_model=PlayersResponse,
    summary="Get All Players",
    description="Retrieve all available FPL players with optional filters",
    dependencies=[Depends(verify_api_key)],
    tags=["Players"],
)
async def get_all_players(
    player_service: PlayerServiceDep,
    position: Optional[str] = Query(
        None,
        description="Filter by position (Goalkeeper, Defender, Midfielder, Forward)",
    ),
    team_id: Optional[int] = Query(None, description="Filter by team ID", ge=1, le=20),
    min_cost: Optional[float] = Query(
        None, description="Minimum cost in millions (e.g., 5.0)", ge=0
    ),
    max_cost: Optional[float] = Query(
        None, description="Maximum cost in millions (e.g., 13.0)", ge=0
    ),
) -> PlayersResponse:
    """Get all FPL players with optional filters.

    Args:
        player_service: Injected player service
        position: Filter by position name
        team_id: Filter by team ID
        min_cost: Minimum cost filter
        max_cost: Maximum cost filter

    Returns:
        List of players matching the filters
    """
    logger.info(
        f"GET /players - position={position}, team_id={team_id}, "
        f"min_cost={min_cost}, max_cost={max_cost}"
    )

    players = await player_service.get_all_players(
        position=position,
        team_id=team_id,
        min_cost=min_cost,
        max_cost=max_cost,
    )

    return PlayersResponse(
        success=True,
        message=f"Retrieved {len(players)} players successfully",
        data=players,
    )


@router.get(
    "/players/{player_id}",
    response_model=BaseResponse[Player],
    summary="Get Player by ID",
    description="Retrieve a specific player by their ID",
    dependencies=[Depends(verify_api_key)],
    tags=["Players"],
)
async def get_player_by_id(
    player_id: int,
    player_service: PlayerServiceDep,
) -> BaseResponse[Player]:
    """Get a specific player by ID.

    Args:
        player_id: Player ID
        player_service: Injected player service

    Returns:
        Player data
    """
    logger.info(f"GET /players/{player_id}")

    player = await player_service.get_player_by_id(player_id)

    return BaseResponse(
        success=True,
        message=f"Player {player_id} retrieved successfully",
        data=player,
    )


@router.get(
    "/players/top/points",
    response_model=PlayersResponse,
    summary="Get Top Players by Points",
    description="Get the top performing players by total points",
    dependencies=[Depends(verify_api_key)],
    tags=["Players"],
)
async def get_top_players(
    player_service: PlayerServiceDep,
    limit: int = Query(10, description="Number of players to return", ge=1, le=100),
) -> PlayersResponse:
    """Get top players by total points.

    Args:
        player_service: Injected player service
        limit: Number of top players to return

    Returns:
        List of top players
    """
    logger.info(f"GET /players/top/points?limit={limit}")

    players = await player_service.get_top_players_by_points(limit)

    return PlayersResponse(
        success=True,
        message=f"Retrieved top {len(players)} players successfully",
        data=players,
    )


@router.get(
    "/players/fixtures/upcoming",
    response_model=BaseResponse[List[PlayerWithFixtures]],
    summary="Get All Players with Upcoming Fixture Difficulty",
    description="Retrieve all players with expected points for the next 5 gameweeks",
    dependencies=[Depends(verify_api_key)],
    tags=["Players"],
)
async def get_players_with_upcoming_fixtures(
    player_service: PlayerServiceDep,
    position: Optional[str] = Query(
        None,
        description="Filter by position (Goalkeeper, Defender, Midfielder, Forward)",
    ),
    team_id: Optional[int] = Query(None, description="Filter by team ID", ge=1, le=20),
    min_cost: Optional[float] = Query(
        None, description="Minimum cost in millions (e.g., 5.0)", ge=0
    ),
    max_cost: Optional[float] = Query(
        None, description="Maximum cost in millions (e.g., 13.0)", ge=0
    ),
) -> BaseResponse[List[PlayerWithFixtures]]:
    """Get all players with expected points for next 5 gameweeks.

    Args:
        player_service: Injected player service
        position: Filter by position name
        team_id: Filter by team ID
        min_cost: Minimum cost filter
        max_cost: Maximum cost filter

    Returns:
        List of players with expected points for upcoming fixtures
    """
    logger.info(
        f"GET /players/fixtures/upcoming - position={position}, team_id={team_id}, "
        f"min_cost={min_cost}, max_cost={max_cost}"
    )

    # Get all players
    all_players = await player_service.get_all_players(
        position=position,
        team_id=team_id,
        min_cost=min_cost,
        max_cost=max_cost,
    )

    # Get expected points service from container
    expected_points_service = container.expected_points_service()

    # Calculate expected points for next 5 gameweeks
    expected_points_map = await expected_points_service.calculate_expected_points_next_n_gameweeks(5)

    # Build response with expected points
    players_with_fixtures = []

    for player in all_players:
        player_id = player.id
        expected_points = expected_points_map.get(player_id, [1.0, 1.0, 1.0, 1.0, 1.0])

        # Ensure we have exactly 5 values
        while len(expected_points) < 5:
            expected_points.append(1.0)

        player_with_fixtures = PlayerWithFixtures(
            id=player.id,
            web_name=player.web_name,
            first_name=player.first_name,
            second_name=player.second_name,
            team=player.team,
            team_name=player.team_name,
            element_type=player.element_type,
            position=player.position,
            now_cost=player.now_cost,
            total_points=player.total_points,
            form=player.form,
            selected_by_percent=player.selected_by_percent,
            minutes=player.minutes,
            status=player.status,
            news=player.news,
            chance_of_playing_next_round=player.chance_of_playing_next_round,
            expected_points_gw1=expected_points[0],
            expected_points_gw2=expected_points[1],
            expected_points_gw3=expected_points[2],
            expected_points_gw4=expected_points[3],
            expected_points_gw5=expected_points[4],
            expected_points_total=sum(expected_points[:5]),
        )

        players_with_fixtures.append(player_with_fixtures)

    logger.info(f"Retrieved {len(players_with_fixtures)} players with fixture data")

    return BaseResponse(
        success=True,
        message=f"Retrieved {len(players_with_fixtures)} players with upcoming fixtures successfully",
        data=players_with_fixtures,
    )
