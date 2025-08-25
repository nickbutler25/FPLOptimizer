"""
Dependency Injection Container
Centralized dependency management and configuration
"""

from typing import Dict, Any, Type, TypeVar, Optional
from functools import lru_cache
import logging

from app.core.config import get_settings, Settings
from app.domain.interfaces.player_repository_interface import PlayerRepositoryInterface
from app.repositories.repository_factory import RepositoryFactory
from app.services.players.players_business_service import PlayersBusinessService
from app.services.common.health_service import HealthService

T = TypeVar('T')


class DependencyContainer:
    """
    Dependency injection container for managing application dependencies

    Implements:
    - Singleton pattern for shared dependencies
    - Lazy initialization
    - Environment-based configuration
    - Type safety
    """

    def __init__(self, settings: Settings = None):
        self._settings = settings or get_settings()
        self._instances: Dict[Type, Any] = {}
        self._logger = logging.getLogger(__name__)

    @property
    def settings(self) -> Settings:
        """Get application settings"""
        return self._settings

    def get_player_repository(self) -> PlayerRepositoryInterface:
        """
        Get player repository instance (singleton)
        Repository type determined by configuration
        """
        if PlayerRepositoryInterface not in self._instances:
            self._logger.info(f"Creating player repository: {self._settings.PLAYER_REPOSITORY_TYPE}")

            repository = RepositoryFactory.create_player_repository(
                self._settings.PLAYER_REPOSITORY_TYPE
            )

            self._instances[PlayerRepositoryInterface] = repository

        return self._instances[PlayerRepositoryInterface]

    def get_players_business_service(self) -> PlayersBusinessService:
        """
        Get players business service instance (singleton)
        Automatically injects repository dependency
        """
        if PlayersBusinessService not in self._instances:
            self._logger.info("Creating players business service")

            repository = self.get_player_repository()
            service = PlayersBusinessService(repository)

            self._instances[PlayersBusinessService] = service

        return self._instances[PlayersBusinessService]

    def get_health_service(self) -> HealthService:
        """
        Get health service instance (singleton)
        Automatically injects repository dependency
        """
        if HealthService not in self._instances:
            self._logger.info("Creating health service")

            repository = self.get_player_repository()
            service = HealthService(repository)

            self._instances[HealthService] = service

        return self._instances[HealthService]

    def register_instance(self, interface: Type[T], instance: T) -> None:
        """
        Register a specific instance for an interface
        Useful for testing with mocks
        """
        self._logger.debug(f"Registering instance for {interface.__name__}")
        self._instances[interface] = instance

    def clear_cache(self) -> None:
        """
        Clear all cached instances
        Useful for testing or configuration changes
        """
        self._logger.info("Clearing dependency container cache")
        self._instances.clear()

    def get_dependency_info(self) -> Dict[str, Any]:
        """
        Get information about registered dependencies
        Useful for debugging and monitoring
        """
        return {
            "settings": {
                "environment": self._settings.ENVIRONMENT,
                "repository_type": self._settings.PLAYER_REPOSITORY_TYPE,
                "cache_enabled": self._settings.CACHE_ENABLED,
                "debug": self._settings.DEBUG
            },
            "registered_instances": {
                cls.__name__: type(instance).__name__
                for cls, instance in self._instances.items()
            },
            "instance_count": len(self._instances)
        }


# Global container instance
_container: Optional[DependencyContainer] = None


def get_container() -> DependencyContainer:
    """
    Get global dependency container instance
    Implements singleton pattern
    """
    global _container
    if _container is None:
        _container = DependencyContainer()
    return _container


def reset_container() -> None:
    """
    Reset global container instance
    Useful for testing
    """
    global _container
    _container = None