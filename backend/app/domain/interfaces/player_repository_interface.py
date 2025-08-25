from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Any

from app.domain.entities.player import Player


class PlayerRepositoryInterface(ABC):
    """Abstract repository interface for player data access"""

    @abstractmethod
    async def find_all(self, filters: Optional[Dict] = None) -> List[Player]:
        """Get all players with optional filtering"""
        pass

    @abstractmethod
    async def find_by_id(self, player_id: int) -> Optional[Player]:
        """Get a specific player by ID"""
        pass

    @abstractmethod
    async def count(self, filters: Optional[Dict] = None) -> int:
        """Count players matching filters"""
        pass

    @abstractmethod
    async def refresh_data(self) -> bool:
        """Refresh underlying data source"""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check health of data source"""
        pass