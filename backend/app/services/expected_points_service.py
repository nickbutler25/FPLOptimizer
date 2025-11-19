"""Expected points calculation service for FPL players."""

import logging
from typing import Dict, List, Optional
from datetime import datetime

from app.infrastructure.http.fpl_client import FPLClient
from app.infrastructure.cache.redis_cache import RedisCache

logger = logging.getLogger(__name__)


class ExpectedPointsService:
    """Service for calculating custom expected points for FPL players."""

    CACHE_KEY_FIXTURES = "fpl:fixtures"
    CACHE_KEY_EXPECTED_POINTS = "fpl:expected_points:{element_id}"
    CACHE_KEY_ALL_EXPECTED_POINTS = "fpl:expected_points:all"

    # Weighting factors for expected points calculation
    WEIGHT_FORM = 0.25  # Recent form (last 3-5 gameweeks)
    WEIGHT_FIXTURE_DIFFICULTY = 0.20  # Opponent strength
    WEIGHT_HOME_AWAY = 0.10  # Home advantage
    WEIGHT_EXPECTED_MINUTES = 0.15  # Playing time likelihood
    WEIGHT_UNDERLYING_STATS = 0.20  # xG, xA, xGI, xGC
    WEIGHT_TEAM_FORM = 0.10  # Team performance

    def __init__(self, fpl_client: FPLClient, cache: RedisCache):
        """Initialize expected points service.

        Args:
            fpl_client: FPL API client
            cache: Redis cache instance
        """
        self.fpl_client = fpl_client
        self.cache = cache

    async def calculate_expected_points_for_all_players(self) -> Dict[int, float]:
        """Calculate expected points for all players.

        Returns:
            Dictionary mapping player element IDs to expected points
        """
        # Check cache first
        cached_data = await self.cache.get(self.CACHE_KEY_ALL_EXPECTED_POINTS)
        if cached_data:
            logger.info("Retrieved all expected points from cache")
            return cached_data

        logger.info("Calculating expected points for all players")

        # Get bootstrap data with all players
        bootstrap_data = await self.fpl_client.get_bootstrap_static()
        players_data = bootstrap_data.get("elements", [])
        teams_data = bootstrap_data.get("teams", [])
        events_data = bootstrap_data.get("events", [])

        # Get fixtures for difficulty ratings
        fixtures_data = await self._get_fixtures()

        # Find next gameweek
        next_event = self._get_next_event(events_data)
        if not next_event:
            logger.warning("No upcoming gameweek found")
            return {}

        # Create team lookup for team strength
        teams_lookup = {team["id"]: team for team in teams_data}

        # Calculate expected points for each player
        expected_points_map: Dict[int, float] = {}

        for player in players_data:
            element_id = player["id"]
            player_team_id = player.get("team")

            # Get player's next fixture
            next_fixture = self._get_next_fixture_for_team(
                fixtures_data, player_team_id, next_event["id"]
            )

            # Calculate expected points
            expected_points = await self._calculate_player_expected_points(
                player, next_fixture, teams_lookup
            )

            expected_points_map[element_id] = expected_points

        # Cache results for 10 minutes
        await self.cache.set(
            self.CACHE_KEY_ALL_EXPECTED_POINTS, expected_points_map, ttl=600
        )

        logger.info(f"Calculated expected points for {len(expected_points_map)} players")
        return expected_points_map

    async def calculate_expected_points(self, element_id: int) -> Optional[float]:
        """Calculate expected points for a single player.

        Args:
            element_id: Player element ID

        Returns:
            Expected points or None if calculation fails
        """
        cache_key = self.CACHE_KEY_EXPECTED_POINTS.format(element_id=element_id)

        # Check cache first
        cached_data = await self.cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"Retrieved expected points for player {element_id} from cache")
            return cached_data

        logger.info(f"Calculating expected points for player {element_id}")

        try:
            # Get all expected points (this will be cached)
            all_expected_points = await self.calculate_expected_points_for_all_players()

            expected_points = all_expected_points.get(element_id)

            if expected_points is not None:
                # Cache individual result
                await self.cache.set(cache_key, expected_points, ttl=600)

            return expected_points

        except Exception as e:
            logger.error(f"Failed to calculate expected points for player {element_id}: {e}")
            return None

    async def _calculate_player_expected_points(
        self,
        player: Dict,
        next_fixture: Optional[Dict],
        teams_lookup: Dict[int, Dict],
    ) -> float:
        """Calculate expected points for a player.

        Args:
            player: Player data from bootstrap-static
            next_fixture: Next fixture data (None if no upcoming fixture)
            teams_lookup: Dictionary of team data

        Returns:
            Calculated expected points
        """
        # Extract player stats
        form = float(player.get("form", 0) or 0)
        minutes = int(player.get("minutes", 0))
        # FPL API uses "starts" not "games_played"
        games_played = player.get("starts", 0)
        element_type = int(player.get("element_type", 0))  # 1=GK, 2=DEF, 3=MID, 4=FWD

        # If player hasn't played at all, return low expected points
        if games_played == 0 or minutes == 0:
            return 1.0

        # Ensure games_played is at least 1 for division
        games_played = max(games_played, 1)

        # Underlying stats (cumulative season totals)
        xg = float(player.get("expected_goals", 0) or 0)
        xa = float(player.get("expected_assists", 0) or 0)
        xgi = float(player.get("expected_goal_involvements", 0) or 0)
        xgc = float(player.get("expected_goals_conceded", 0) or 0)

        # Calculate average minutes per game early for use in baseline calculation
        avg_minutes_per_game = minutes / games_played

        # --- Start with form as baseline (average points per game) ---
        base_score = form

        # If form is 0 but player is a regular starter, use underlying stats as baseline
        if form == 0 and avg_minutes_per_game > 60:
            # Use xGI for attackers, or a small baseline for defenders/GKs
            if element_type in [3, 4]:  # MID, FWD
                xgi_per_game = xgi / games_played if xgi > 0 else 0
                base_score = max(1.5, min(xgi_per_game * 5, 3.0))  # Cap at 3.0
            else:
                base_score = 2.0  # Defenders and GKs with no form get 2.0

        # --- Fixture Difficulty Multiplier (0.7 to 1.3) ---
        fixture_multiplier = 1.0
        home_multiplier = 1.0

        if next_fixture:
            player_team_id = player.get("team")
            is_home = next_fixture.get("team_h") == player_team_id

            # Get difficulty rating (1-5, where 1 is easiest)
            difficulty = (
                next_fixture.get("team_h_difficulty", 3)
                if is_home
                else next_fixture.get("team_a_difficulty", 3)
            )

            # Convert difficulty to multiplier
            # Difficulty 1 (easiest): 1.3x
            # Difficulty 2: 1.15x
            # Difficulty 3 (average): 1.0x
            # Difficulty 4: 0.85x
            # Difficulty 5 (hardest): 0.7x
            fixture_multiplier = 1.0 + (3 - difficulty) * 0.15

            # Home/away multiplier
            # Home: 1.1x (10% boost)
            # Away: 0.95x (5% penalty)
            home_multiplier = 1.1 if is_home else 0.95

        # --- Minutes likelihood multiplier (0.3 to 1.0) ---
        # Players who don't play full games get penalized
        minutes_multiplier = 0.3 + (min(avg_minutes_per_game / 90, 1.0) * 0.7)

        # --- Underlying stats adjustment (position-specific) ---
        underlying_adjustment = 0.0

        if element_type in [3, 4]:  # MID, FWD
            # Compare xGI per game to form
            # Good attackers should have xGI close to or above their form
            xgi_per_game = xgi / games_played
            # If xGI is higher than form, add up to +1 point
            # If xGI is lower than form, subtract up to -0.5 points
            xgi_diff = xgi_per_game - (form * 0.5)
            underlying_adjustment = max(-0.5, min(1.0, xgi_diff))

        elif element_type == 2:  # DEF
            # Defenders: lower xGC is better (clean sheet potential)
            xgc_per_game = xgc / games_played
            # Average xGC is around 1.0-1.2 per game
            # Below 1.0 is good, add bonus
            # Above 1.2 is bad, subtract
            if xgc_per_game < 1.0:
                underlying_adjustment = (1.0 - xgc_per_game) * 0.5
            elif xgc_per_game > 1.2:
                underlying_adjustment = (1.2 - xgc_per_game) * 0.3

            # Also consider attacking threat for defenders
            xgi_per_game = xgi / games_played
            if xgi_per_game > 0.1:  # Decent attacking threat
                underlying_adjustment += xgi_per_game * 0.5

        elif element_type == 1:  # GK
            # Goalkeepers: focus on clean sheet potential
            xgc_per_game = xgc / games_played
            # Lower xGC means better chance of clean sheet
            if xgc_per_game < 1.0:
                underlying_adjustment = (1.0 - xgc_per_game) * 0.8
            elif xgc_per_game > 1.5:
                underlying_adjustment = (1.5 - xgc_per_game) * 0.4

        # --- Calculate final expected points ---
        # Apply multipliers to base form score
        expected_points = base_score * fixture_multiplier * home_multiplier * minutes_multiplier

        # Cap after multipliers to prevent explosion
        expected_points = min(expected_points, 8.0)

        # Add underlying stats adjustment (capped contribution)
        expected_points += max(-1.0, min(underlying_adjustment, 1.5))

        # Ensure reasonable range (0.5 to 8)
        # Top players in best fixtures might hit 7-8
        # Average players in average fixtures should be 3-5
        # Bench fodder or bad fixtures should be 1-3
        expected_points = max(0.5, min(expected_points, 8.0))

        final_value = round(expected_points, 1)

        # Debug logging for high values
        if final_value > 8.0:
            logger.warning(
                f"Player {player.get('web_name', player.get('id'))} has xP > 8.0: {final_value} "
                f"(form={form}, base={base_score}, fixture_mult={fixture_multiplier}, "
                f"home_mult={home_multiplier}, mins_mult={minutes_multiplier})"
            )

        # Specific logging for Mateta (ID 283)
        if player.get('id') == 283:
            logger.warning(
                f"MATETA (283) - xP: {final_value} | form: {form}, base: {base_score:.2f}, "
                f"fixture_mult: {fixture_multiplier:.2f}, home_mult: {home_multiplier:.2f}, "
                f"mins_mult: {minutes_multiplier:.2f}, underlying_adj: {underlying_adjustment:.2f}"
            )

        return final_value

    async def _get_fixtures(self) -> List[Dict]:
        """Get all fixtures with caching.

        Returns:
            List of fixture data
        """
        # Check cache first
        cached_data = await self.cache.get(self.CACHE_KEY_FIXTURES)
        if cached_data:
            logger.info("Retrieved fixtures from cache")
            return cached_data

        # Fetch from API
        logger.info("Fetching fixtures from FPL API")
        fixtures_data = await self.fpl_client.get_fixtures()

        # Cache for 30 minutes
        await self.cache.set(self.CACHE_KEY_FIXTURES, fixtures_data, ttl=1800)

        logger.info(f"Retrieved {len(fixtures_data)} fixtures")
        return fixtures_data

    def _get_next_event(self, events_data: List[Dict]) -> Optional[Dict]:
        """Get the next upcoming gameweek.

        Args:
            events_data: List of gameweek events

        Returns:
            Next event data or None
        """
        for event in events_data:
            if event.get("is_next"):
                return event

        # Fallback: find first event that hasn't finished
        for event in events_data:
            if not event.get("finished"):
                return event

        return None

    def _get_next_fixture_for_team(
        self, fixtures_data: List[Dict], team_id: int, event_id: int
    ) -> Optional[Dict]:
        """Get next fixture for a team in a specific gameweek.

        Args:
            fixtures_data: List of all fixtures
            team_id: Team ID
            event_id: Gameweek/event ID

        Returns:
            Fixture data or None
        """
        for fixture in fixtures_data:
            if fixture.get("event") == event_id:
                if fixture.get("team_h") == team_id or fixture.get("team_a") == team_id:
                    return fixture

        return None

    async def calculate_expected_points_next_n_gameweeks(
        self, num_gameweeks: int = 5
    ) -> Dict[int, List[float]]:
        """Calculate expected points for all players for the next N gameweeks.

        Args:
            num_gameweeks: Number of upcoming gameweeks to calculate (default 5)

        Returns:
            Dictionary mapping player element IDs to list of expected points per gameweek
        """
        logger.info(f"Calculating expected points for next {num_gameweeks} gameweeks")

        # Get bootstrap data
        bootstrap_data = await self.fpl_client.get_bootstrap_static()
        players_data = bootstrap_data.get("elements", [])
        teams_data = bootstrap_data.get("teams", [])
        events_data = bootstrap_data.get("events", [])

        # Get all fixtures
        fixtures_data = await self._get_fixtures()

        # Find next gameweek
        next_event = self._get_next_event(events_data)
        if not next_event:
            logger.warning("No upcoming gameweek found")
            return {}

        next_event_id = next_event["id"]
        teams_lookup = {team["id"]: team for team in teams_data}

        # Calculate expected points for each player for next N gameweeks
        expected_points_map: Dict[int, List[float]] = {}

        for player in players_data:
            element_id = player["id"]
            player_team_id = player.get("team")
            gameweek_points = []

            # Calculate for each of the next N gameweeks
            for i in range(num_gameweeks):
                event_id = next_event_id + i

                # Get fixture for this gameweek
                fixture = self._get_next_fixture_for_team(
                    fixtures_data, player_team_id, event_id
                )

                # Calculate expected points for this gameweek
                expected_points = await self._calculate_player_expected_points(
                    player, fixture, teams_lookup
                )

                gameweek_points.append(expected_points)

            expected_points_map[element_id] = gameweek_points

        logger.info(
            f"Calculated expected points for {len(expected_points_map)} players "
            f"across {num_gameweeks} gameweeks"
        )
        return expected_points_map
