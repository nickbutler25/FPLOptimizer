"""Team endpoints."""

import logging
from fastapi import APIRouter, Query, Depends

from app.api.dependencies import TeamServiceDep, TransferSolverServiceDep
from app.schemas.responses import (
    TeamResponse,
    BaseResponse,
    TransferPlanResponse,
    TransferPlanData,
    WeeklyTransferSolution,
    TransferRecommendation,
)
from app.core.security import verify_api_key

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/teams/{team_id}",
    response_model=TeamResponse,
    response_model_by_alias=False,  # Use field names, not aliases
    summary="Get Team by ID",
    description="Retrieve FPL team data by team entry ID",
    dependencies=[Depends(verify_api_key)],
    tags=["Teams"],
)
async def get_team(
    team_id: int,
    team_service: TeamServiceDep,
    include_picks: bool = Query(
        True, description="Include current team picks (starting XI and bench)"
    ),
) -> TeamResponse:
    """Get FPL team by ID.

    Args:
        team_id: FPL team entry ID
        team_service: Injected team service
        include_picks: Whether to include current team picks

    Returns:
        Team data with optional picks
    """
    logger.info(f"GET /teams/{team_id}?include_picks={include_picks}")

    team = await team_service.get_team_by_id(team_id, include_picks=include_picks)

    return TeamResponse(
        success=True,
        message=f"Team {team_id} retrieved successfully",
        data=team,
    )


@router.get(
    "/teams/{team_id}/summary",
    response_model=BaseResponse[dict],
    response_model_by_alias=False,  # Use field names, not aliases
    summary="Get Team Summary",
    description="Get team summary with key statistics",
    dependencies=[Depends(verify_api_key)],
    tags=["Teams"],
)
async def get_team_summary(
    team_id: int,
    team_service: TeamServiceDep,
) -> BaseResponse[dict]:
    """Get team summary with key statistics.

    Args:
        team_id: FPL team entry ID
        team_service: Injected team service

    Returns:
        Team summary with key statistics
    """
    logger.info(f"GET /teams/{team_id}/summary")

    summary = await team_service.get_team_summary(team_id)

    return BaseResponse(
        success=True,
        message=f"Team {team_id} summary retrieved successfully",
        data=summary,
    )


@router.post(
    "/teams/{team_id}/transfer-plan",
    response_model=TransferPlanResponse,
    response_model_by_alias=False,
    summary="Generate Transfer Plan",
    description="Generate optimal transfer plan for N gameweeks using CVXPY",
    dependencies=[Depends(verify_api_key)],
    tags=["Teams", "Transfers"],
)
async def generate_transfer_plan(
    team_id: int,
    team_service: TeamServiceDep,
    transfer_solver_service: TransferSolverServiceDep,
    num_gameweeks: int = Query(5, ge=1, le=10, description="Number of gameweeks to optimize"),
    discount_factor: float = Query(0.9, ge=0.5, le=1.0, description="Discount factor for future gameweeks"),
) -> TransferPlanResponse:
    """Generate optimal transfer plan for N gameweeks.

    Args:
        team_id: FPL team entry ID
        team_service: Injected team service
        transfer_solver_service: Injected transfer solver service
        num_gameweeks: Number of gameweeks to optimize (1-10)
        discount_factor: Discount factor for future gameweeks (0.5-1.0)

    Returns:
        Complete transfer plan with weekly recommendations
    """
    # Get team with current squad
    team = await team_service.get_team_by_id(team_id, include_picks=True)

    if not team.picks or len(team.picks) == 0:
        return TransferPlanResponse(
            success=False,
            message="Team has no current picks to optimize",
            data=None,
        )

    # Get calculated free transfers from team data
    free_transfers = 1  # Default fallback
    if team.transfers and isinstance(team.transfers, dict):
        free_transfers = team.transfers.get("free_transfers", 1)

    logger.info(
        f"POST /teams/{team_id}/transfer-plan?num_gameweeks={num_gameweeks}&"
        f"free_transfers={free_transfers}&discount_factor={discount_factor}"
    )

    # Calculate budget (bank in millions)
    budget = team.bank / 10.0 if team.bank else 0.0

    # Solve transfer optimization
    transfer_plan = await transfer_solver_service.solve_transfers(
        current_squad=team.picks,
        num_gameweeks=num_gameweeks,
        free_transfers=free_transfers,
        budget=budget,
        discount_factor=discount_factor,
    )

    # Convert to response format
    weekly_solutions = [
        WeeklyTransferSolution(
            gameweek=sol.gameweek,
            transfers_in=[TransferRecommendation(**t) for t in sol.transfers_in],
            transfers_out=[TransferRecommendation(**t) for t in sol.transfers_out],
            expected_points=sol.expected_points,
            transfer_cost=sol.transfer_cost,
            free_transfers_used=sol.free_transfers_used,
            free_transfers_remaining=sol.free_transfers_remaining,
        )
        for sol in transfer_plan.weekly_solutions
    ]

    # FPL API current_event is the last completed gameweek, so add 1 for next gameweek
    next_gameweek = team.current_event + 1

    plan_data = TransferPlanData(
        current_gameweek=next_gameweek,
        weekly_solutions=weekly_solutions,
        total_expected_points=transfer_plan.total_expected_points,
        total_transfer_cost=transfer_plan.total_transfer_cost,
        current_expected_points=transfer_plan.current_expected_points,
        improvement=transfer_plan.improvement,
    )

    return TransferPlanResponse(
        success=True,
        message=f"Transfer plan generated for {num_gameweeks} gameweeks",
        data=plan_data,
    )
