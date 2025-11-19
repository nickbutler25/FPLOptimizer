"""FastAPI dependencies for dependency injection."""

from typing import Annotated
from fastapi import Depends

from app.core.container import container
from app.services.player_service import PlayerService
from app.services.team_service import TeamService
from app.services.transfer_solver_service import TransferSolverService


async def get_player_service() -> PlayerService:
    """Get player service instance."""
    return container.player_service()


async def get_team_service() -> TeamService:
    """Get team service instance."""
    return container.team_service()


async def get_transfer_solver_service() -> TransferSolverService:
    """Get transfer solver service instance."""
    return container.transfer_solver_service()


# Type aliases for dependency injection
PlayerServiceDep = Annotated[PlayerService, Depends(get_player_service)]
TeamServiceDep = Annotated[TeamService, Depends(get_team_service)]
TransferSolverServiceDep = Annotated[TransferSolverService, Depends(get_transfer_solver_service)]
