"""
Dependency Injection Setup
Centralizes dependency creation and injection for FastAPI endpoints
"""

from typing import Annotated
from fastapi import Depends
import logging

from app.core.config import get_settings
from app.domain.interfaces.player_repository_interface import PlayerRepositoryInterface
from app.repositories.repository_factory import RepositoryFactory
from app.services.players.players_business_service import PlayersBusinessService
from app.services.common.health_service import HealthService

# ===== REPOSITORY DEPENDENCIES =====

def get_player_repository() -> PlayerRepositoryInterface:
    """
    Create and return the appropriate player repository based on configuration.
    This is where we decide which repository implementation to use.
    """
    settings = get_settings()
    repository_type = getattr(settings, 'PLAYER_REPOSITORY_TYPE', 'fpl')

    logger = logging.getLogger(__name__)
    logger.info(f"Creating player repository of type: {repository_type}")

    return RepositoryFactory.create_player_repository(repository_type)


# ===== SERVICE DEPENDENCIES =====

def get_players_service(
        repository: Annotated[PlayerRepositoryInterface, Depends(get_player_repository)]
) -> PlayersBusinessService:
    """
    Create and return the players business service with injected repository.
    The service doesn't know which repository implementation it's using.
    """
    return PlayersBusinessService(repository)


def get_health_service(
        repository: Annotated[PlayerRepositoryInterface, Depends(get_player_repository)]
) -> HealthService:
    """
    Create and return the health service with injected repository.
    """
    return HealthService(repository)


# ===== TYPED DEPENDENCIES FOR ENDPOINTS =====

# Type aliases for cleaner endpoint signatures
PlayersServiceDep = Annotated[PlayersBusinessService, Depends(get_players_service)]
HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]
