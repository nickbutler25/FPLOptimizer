from backend.app.domain.interfaces.player_repository_interface import PlayerRepositoryInterface


class PlayersBusinessService:
    """
    Business service that works with any repository implementation.
    Doesn't need to know if data comes from FPL API, database, or mock.
    """

    def __init__(self, repository: PlayerRepositoryInterface):
        self.repository = repository
        self.logger = logging.getLogger(__name__)

    async def get_players(self, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Get filtered list of players"""
        try:
            players = await self.repository.find_all(filters)

            # Apply any business-level filtering here
            # (repository handles data source, service handles business logic)

            return {
                "status": "success",
                "players": [asdict(player) for player in players],
                "total_count": len(players),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error in get_players: {str(e)}")
            raise

    async def get_player(self, player_id: int) -> Dict[str, Any]:
        """Get single player by ID"""
        try:
            player = await self.repository.find_by_id(player_id)

            if not player:
                return {
                    "status": "error",
                    "message": f"Player with ID {player_id} not found"
                }

            return {
                "status": "success",
                "data": asdict(player),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error in get_player: {str(e)}")
            raise

    async def refresh_data(self) -> Dict[str, Any]:
        """Force refresh of data source"""
        try:
            success = await self.repository.refresh_data()
            return {
                "status": "success" if success else "error",
                "message": "Data refreshed" if success else "Refresh failed",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error refreshing data: {str(e)}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """Check health of underlying data source"""
        try:
            health_data = await self.repository.health_check()
            health_data["timestamp"] = datetime.utcnow().isoformat()
            return health_data
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }