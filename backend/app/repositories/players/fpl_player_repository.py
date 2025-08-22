class FPLPlayerRepository(PlayerRepositoryInterface):
    """
    Repository implementation that handles FPL API integration internally.
    This encapsulates all FPL-specific logic within the repository layer.
    """

    def __init__(self):
        self.fpl_base_url = "https://fantasy.premierleague.com/api"
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.logger = logging.getLogger(__name__)

        # Internal caching
        self._players_cache: Optional[List[Player]] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(hours=1)

        # FPL API session management
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session for FPL API calls"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    async def _close_session(self):
        """Close HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _fetch_fpl_data(self, endpoint: str) -> Dict[str, Any]:
        """
        Internal method to fetch data from FPL API.
        This is private to the repository - external code doesn't need to know about FPL API.
        """
        url = f"{self.fpl_base_url}/{endpoint.lstrip('/')}"
        session = await self._get_session()

        try:
            self.logger.info(f"Fetching FPL data from: {endpoint}")
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                self.logger.info(f"Successfully fetched FPL data from {endpoint}")
                return data

        except aiohttp.ClientError as e:
            self.logger.error(f"FPL API error for {endpoint}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"FPL API unavailable: {str(e)}"
            )
        except Exception as e:
            self.logger.error(f"Unexpected error fetching FPL data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing FPL data: {str(e)}"
            )

    def _map_fpl_player_to_domain(self, element_data: Dict, teams_data: List[Dict]) -> Player:
        """
        Internal method to map FPL API data to our domain model.
        This encapsulates FPL-specific data transformation within the repository.
        """
        # Get team name
        team_id = element_data.get("team")
        team_name = "Unknown"
        for team in teams_data:
            if team.get("id") == team_id:
                team_name = team.get("name", "Unknown")
                break

        # Map position
        position_mapping = {1: Position.GKP, 2: Position.DEF, 3: Position.MID, 4: Position.FWD}
        position = position_mapping.get(element_data.get("element_type"), Position.MID)

        # Calculate derived fields
        cost = element_data.get("now_cost", 0) / 10.0  # FPL stores in 0.1m units
        total_points = element_data.get("total_points", 0)
        points_per_cost = round(total_points / cost, 2) if cost > 0 else 0

        # Determine injury status
        injury_status = self._determine_injury_status(element_data)

        return Player(
            id=element_data.get("id"),
            name=f"{element_data.get('first_name', '')} {element_data.get('second_name', '')}".strip(),
            position=position,
            team=team_name,
            cost=cost,
            points=total_points,
            points_per_cost=points_per_cost,
            form=float(element_data.get("form", 0)) if element_data.get("form") else None,
            selected_by_percent=float(element_data.get("selected_by_percent", 0)),
            minutes=element_data.get("minutes"),
            goals_scored=element_data.get("goals_scored"),
            assists=element_data.get("assists"),
            clean_sheets=element_data.get("clean_sheets"),
            bonus=element_data.get("bonus"),
            transfers_in=element_data.get("transfers_in_event"),
            transfers_out=element_data.get("transfers_out_event"),
            news=element_data.get("news") if element_data.get("news") else None,
            chance_of_playing_this_round=element_data.get("chance_of_playing_this_round"),
            chance_of_playing_next_round=element_data.get("chance_of_playing_next_round"),
            injury_status=injury_status,
            web_name=element_data.get("web_name"),
            fpl_id=element_data.get("id")
        )

    def _determine_injury_status(self, player_data: Dict) -> InjuryStatus:
        """Internal method to determine injury status from FPL data"""
        news = player_data.get("news", "").lower()
        status = player_data.get("status", "a")
        chance_playing = player_data.get("chance_of_playing_this_round")

        if status == "i" or "injured" in news or "injury" in news:
            return InjuryStatus.INJURED
        elif status == "s" or "suspended" in news or "suspension" in news:
            return InjuryStatus.SUSPENDED
        elif status == "d" or (chance_playing is not None and chance_playing < 75):
            return InjuryStatus.DOUBTFUL
        else:
            return InjuryStatus.AVAILABLE

    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if self._players_cache is None or self._cache_timestamp is None:
            return False
        return datetime.now() - self._cache_timestamp < self._cache_ttl

    async def _load_players_from_fpl(self) -> List[Player]:
        """
        Internal method to load all players from FPL API.
        This is where the actual FPL API integration happens.
        """
        try:
            # Fetch bootstrap data from FPL API
            bootstrap_data = await self._fetch_fpl_data("bootstrap-static/")

            elements = bootstrap_data.get("elements", [])
            teams = bootstrap_data.get("teams", [])

            players = []
            for element in elements:
                try:
                    player = self._map_fpl_player_to_domain(element, teams)
                    players.append(player)
                except Exception as e:
                    self.logger.warning(f"Failed to map player {element.get('id')}: {str(e)}")
                    continue

            self.logger.info(f"Successfully loaded {len(players)} players from FPL API")
            return players

        except HTTPException:
            # Re-raise HTTP exceptions (already handled)
            raise
        except Exception as e:
            self.logger.error(f"Error loading players from FPL API: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load player data from FPL API"
            )

    # ===== PUBLIC REPOSITORY INTERFACE IMPLEMENTATION =====

    async def find_all(self, filters: Optional[Dict] = None) -> List[Player]:
        """
        Get all players. This is the main entry point - callers don't need to know about FPL API.
        The repository handles caching and FPL API calls internally.
        """
        try:
            # Use cache if valid
            if self._is_cache_valid():
                self.logger.info("Returning cached player data")
                return self._players_cache.copy()

            # Load fresh data from FPL API
            self.logger.info("Cache expired, loading fresh data from FPL API")
            players = await self._load_players_from_fpl()

            # Update cache
            self._players_cache = players
            self._cache_timestamp = datetime.now()

            return players.copy()

        except HTTPException:
            # If we have cached data and FPL API fails, return cache as fallback
            if self._players_cache:
                self.logger.warning("FPL API failed, returning stale cached data")
                return self._players_cache.copy()
            raise
        except Exception as e:
            self.logger.error(f"Error in find_all: {str(e)}")
            # Return cached data if available, otherwise re-raise
            if self._players_cache:
                return self._players_cache.copy()
            raise

    async def find_by_id(self, player_id: int) -> Optional[Player]:
        """Get a specific player by ID"""
        players = await self.find_all()
        return next((p for p in players if p.id == player_id), None)

    async def count(self, filters: Optional[Dict] = None) -> int:
        """Count players matching filters"""
        players = await self.find_all(filters)
        return len(players)

    async def refresh_data(self) -> bool:
        """Force refresh of FPL data"""
        try:
            self.logger.info("Force refreshing FPL data")
            players = await self._load_players_from_fpl()

            # Update cache
            self._players_cache = players
            self._cache_timestamp = datetime.now()

            self.logger.info("FPL data refresh successful")
            return True

        except Exception as e:
            self.logger.error(f"Failed to refresh FPL data: {str(e)}")
            return False

    async def health_check(self) -> Dict[str, Any]:
        """Check health of FPL API connection"""
        try:
            # Test FPL API connectivity
            await self._fetch_fpl_data("bootstrap-static/")

            return {
                "status": "healthy",
                "fpl_api": "connected",
                "cache_status": "valid" if self._is_cache_valid() else "expired",
                "cached_players": len(self._players_cache) if self._players_cache else 0,
                "last_refresh": self._cache_timestamp.isoformat() if self._cache_timestamp else None
            }

        except Exception as e:
            return {
                "status": "degraded",
                "fpl_api": "disconnected",
                "error": str(e),
                "cache_status": "valid" if self._is_cache_valid() else "expired",
                "cached_players": len(self._players_cache) if self._players_cache else 0
            }

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup resources"""
        await self._close_session()