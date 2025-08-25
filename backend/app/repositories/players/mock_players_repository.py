from typing import Optional

from backend.app.domain.entities.player import Player
from backend.app.domain.enums.position import Position
from backend.app.domain.interfaces.player_repository_interface import PlayerRepositoryInterface


class MockPlayerRepository(PlayerRepositoryInterface):
    """Mock repository for testing - doesn't make real API calls"""

    def __init__(self):
        self.mock_players = [
            Player(1, "Mo Salah", Position.MID, "Liverpool", 13.0, 280, 21.5),
            Player(2, "Erling Haaland", Position.FWD, "Man City", 14.0, 320, 22.9),
            Player(3, "Kevin De Bruyne", Position.MID, "Man City", 11.5, 245, 21.3),
            # ... more mock players
        ]

    async def find_all(self, filters: Optional[Dict] = None) -> List[Player]:
        return self.mock_players.copy()

    async def find_by_id(self, player_id: int) -> Optional[Player]:
        return next((p for p in self.mock_players if p.id == player_id), None)

    async def count(self, filters: Optional[Dict] = None) -> int:
        return len(self.mock_players)

    async def refresh_data(self) -> bool:
        return True  # Mock always succeeds

    async def health_check(self) -> Dict[str, Any]:
        return {"status": "healthy", "data_source": "mock"}