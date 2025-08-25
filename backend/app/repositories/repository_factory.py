# ===== DEPENDENCY INJECTION =====
from app.domain.interfaces.player_repository_interface import PlayerRepositoryInterface
from app.repositories.players.fpl_player_repository import FPLPlayerRepository
from app.repositories.players.mock_players_repository import MockPlayerRepository


class RepositoryFactory:
    """Factory for creating repository instances"""

    @staticmethod
    def create_player_repository(repository_type: str = "fpl") -> PlayerRepositoryInterface:
        """Create appropriate repository based on configuration"""
        if repository_type == "mock":
            return MockPlayerRepository()
        elif repository_type == "fpl":
            return FPLPlayerRepository()
        else:
            raise ValueError(f"Unknown repository type: {repository_type}")