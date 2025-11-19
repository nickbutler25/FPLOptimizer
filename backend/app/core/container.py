"""Dependency injection container using dependency-injector."""

from dependency_injector import containers, providers
import httpx

from app.core.config import settings
from app.infrastructure.http.fpl_client import FPLClient
from app.infrastructure.cache.redis_cache import RedisCache
from app.repositories.player_repository import PlayerRepository
from app.repositories.team_repository import TeamRepository
from app.services.player_service import PlayerService
from app.services.team_service import TeamService
from app.services.expected_points_service import ExpectedPointsService
from app.services.transfer_solver_service import TransferSolverService


class Container(containers.DeclarativeContainer):
    """Dependency injection container for the application."""

    # Configuration
    config = providers.Singleton(lambda: settings)

    # HTTP Client
    http_client = providers.Singleton(
        httpx.AsyncClient,
        timeout=settings.fpl_api_timeout,
        follow_redirects=True,
    )

    # Infrastructure
    fpl_client = providers.Singleton(
        FPLClient,
        client=http_client,
        base_url=settings.fpl_api_base_url,
        max_retries=settings.fpl_api_max_retries,
    )

    redis_cache = providers.Singleton(
        RedisCache,
        redis_url=settings.redis_url,
        ttl=settings.redis_cache_ttl,
    )

    # Services (defined before repositories that depend on them)
    expected_points_service = providers.Singleton(
        ExpectedPointsService,
        fpl_client=fpl_client,
        cache=redis_cache,
    )

    # Repositories
    player_repository = providers.Singleton(
        PlayerRepository,
        fpl_client=fpl_client,
        cache=redis_cache,
    )

    team_repository = providers.Singleton(
        TeamRepository,
        fpl_client=fpl_client,
        cache=redis_cache,
        expected_points_service=expected_points_service,
    )

    # Domain Services
    player_service = providers.Singleton(
        PlayerService,
        player_repository=player_repository,
    )

    team_service = providers.Singleton(
        TeamService,
        team_repository=team_repository,
    )

    transfer_solver_service = providers.Singleton(
        TransferSolverService,
        expected_points_service=expected_points_service,
        player_service=player_service,
    )


# Global container instance
container = Container()
