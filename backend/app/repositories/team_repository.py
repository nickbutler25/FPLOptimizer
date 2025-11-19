"""Team repository for accessing FPL team data."""

import logging
from typing import Optional, Dict, TYPE_CHECKING

from app.infrastructure.http.fpl_client import FPLClient
from app.infrastructure.cache.redis_cache import RedisCache
from app.models.team import Team
from app.models.team_pick import TeamPick
from app.core.exceptions import NotFoundException

if TYPE_CHECKING:
    from app.services.expected_points_service import ExpectedPointsService

logger = logging.getLogger(__name__)


class TeamRepository:
    """Repository for FPL team data."""

    CACHE_KEY_TEAM = "fpl:team:{team_id}"
    CACHE_KEY_TEAM_PICKS = "fpl:team:{team_id}:event:{event}"
    CACHE_KEY_PLAYERS_LOOKUP = "fpl:players:lookup"

    def __init__(
        self,
        fpl_client: FPLClient,
        cache: RedisCache,
        expected_points_service: "ExpectedPointsService",
    ):
        """Initialize team repository.

        Args:
            fpl_client: FPL API client
            cache: Redis cache instance
            expected_points_service: Expected points calculation service
        """
        self.fpl_client = fpl_client
        self.cache = cache
        self.expected_points_service = expected_points_service

    async def get_team_by_id(self, team_id: int, include_picks: bool = True) -> Team:
        """Get FPL team by ID.

        Args:
            team_id: FPL team entry ID
            include_picks: Whether to include current team picks

        Returns:
            Team data

        Raises:
            NotFoundException: If team not found
            ExternalAPIException: If FPL API request fails
        """
        cache_key = self.CACHE_KEY_TEAM.format(team_id=team_id)

        # Try cache first (without picks for now)
        cached_data = await self.cache.get(cache_key)
        if cached_data and not include_picks:
            logger.info(f"Retrieved team {team_id} from cache")
            return Team(**cached_data)

        # Fetch from API
        logger.info(f"Fetching team {team_id} from FPL API")
        try:
            team_data = await self.fpl_client.get_entry(team_id)
        except Exception as e:
            logger.error(f"Failed to fetch team {team_id}: {e}")
            raise NotFoundException(f"Team with ID {team_id} not found") from e

        # Get current event for picks
        current_event = team_data.get("current_event")

        # Create team model (without picks initially)
        team = Team(**team_data)

        # Cache team data
        await self.cache.set(cache_key, team.model_dump(exclude={"picks"}), ttl=300)

        # Get picks if requested and current event exists
        if include_picks and current_event:
            picks, picks_metadata = await self._get_team_picks(team_id, current_event)
            # Get purchase prices from transfer history
            purchase_prices = await self._get_purchase_prices(team_id)
            # Enrich picks with player data and purchase prices
            picks = await self._enrich_picks_with_player_data(picks, purchase_prices)
            team.picks = picks

            # Extract transfer information from picks metadata
            entry_history = picks_metadata.get("entry_history", {})
            if entry_history:
                # Calculate free transfers available
                free_transfers = await self._calculate_free_transfers(team_id, current_event)

                # Update the transfers dict with transfer stats
                team.transfers = {
                    "made": entry_history.get("event_transfers", 0),  # Transfers made this gameweek
                    "cost": entry_history.get("event_transfers_cost", 0),  # Points cost for transfers this gameweek
                    "bank": entry_history.get("bank", 0) / 10.0,  # Money in bank (in millions)
                    "value": entry_history.get("value", 0) / 10.0,  # Squad value (in millions)
                    "free_transfers": free_transfers,  # Available free transfers for next gameweek
                }

        logger.info(f"Retrieved team {team_id} from FPL API")
        return team

    async def _get_team_picks(self, team_id: int, event: int) -> tuple[list[TeamPick], dict]:
        """Get team picks for a specific gameweek.

        Args:
            team_id: FPL team entry ID
            event: Gameweek number

        Returns:
            Tuple of (list of team picks, full picks metadata dict)
        """
        cache_key = self.CACHE_KEY_TEAM_PICKS.format(team_id=team_id, event=event)

        # Try cache first
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            logger.info(f"Retrieved team {team_id} picks for event {event} from cache")
            # When returning from cache, we only have picks, not full metadata
            return [TeamPick(**pick) for pick in cached_data], {}

        # Fetch from API
        logger.info(f"Fetching team {team_id} picks for event {event} from FPL API")
        picks_data = await self.fpl_client.get_entry_picks(team_id, event)

        picks_list = picks_data.get("picks", [])

        # Convert to TeamPick models
        picks = [TeamPick(**pick) for pick in picks_list]

        # Cache picks
        await self.cache.set(
            cache_key,
            [pick.model_dump() for pick in picks],
            ttl=600,  # Cache for 10 minutes
        )

        logger.info(f"Retrieved {len(picks)} picks for team {team_id} event {event}")
        return picks, picks_data

    async def _get_players_lookup(self) -> Dict[int, dict]:
        """Get player lookup dictionary from bootstrap-static.

        Returns:
            Dictionary mapping player IDs to player data
        """
        # Try cache first
        cached_data = await self.cache.get(self.CACHE_KEY_PLAYERS_LOOKUP)
        if cached_data:
            logger.info("Retrieved players lookup from cache")
            return cached_data

        # Fetch from API
        logger.info("Fetching players lookup from FPL API")
        bootstrap_data = await self.fpl_client.get_bootstrap_static()

        # Extract players and teams
        players_data = bootstrap_data.get("elements", [])
        teams_data = bootstrap_data.get("teams", [])

        # Create team lookup for team names and shirt codes
        teams_lookup = {
            team["id"]: {
                "name": team.get("name", ""),
                "short_name": team.get("short_name", ""),
                "code": team.get("code", 0),
            }
            for team in teams_data
        }

        # Create lookup dictionary with team info
        players_lookup = {
            player["id"]: {
                "web_name": player.get("web_name", ""),
                "first_name": player.get("first_name", ""),
                "second_name": player.get("second_name", ""),
                "team": player.get("team", 0),
                "team_name": teams_lookup.get(player.get("team", 0), {}).get("name", ""),
                "team_short_name": teams_lookup.get(player.get("team", 0), {}).get("short_name", ""),
                "team_code": teams_lookup.get(player.get("team", 0), {}).get("code", 0),
                "element_type": player.get("element_type", 0),
                "now_cost": player.get("now_cost", 0),
                "ep_next": player.get("ep_next"),  # Expected points next gameweek
            }
            for player in players_data
        }

        # Cache the lookup
        await self.cache.set(
            self.CACHE_KEY_PLAYERS_LOOKUP,
            players_lookup,
            ttl=600,  # Cache for 10 minutes
        )

        logger.info(f"Created lookup for {len(players_lookup)} players")
        return players_lookup

    async def _get_purchase_prices(self, team_id: int) -> Dict[int, int]:
        """Get purchase prices for current squad from transfer history.

        Args:
            team_id: FPL team entry ID

        Returns:
            Dictionary mapping player IDs to purchase prices
        """
        try:
            transfers_data = await self.fpl_client.get_entry_transfers(team_id)

            # Build a dictionary of current purchase prices
            # Start with empty dict, track latest transfer for each player
            purchase_prices: Dict[int, int] = {}

            # Process transfers chronologically (oldest first)
            # Transfers are returned newest first, so reverse them
            for transfer in reversed(transfers_data):
                player_in = transfer.get("element_in")
                purchase_price = transfer.get("element_in_cost")

                if player_in and purchase_price:
                    # Update purchase price (will be overwritten if player was transferred out and back in)
                    purchase_prices[player_in] = purchase_price

                # Remove player that was transferred out
                player_out = transfer.get("element_out")
                if player_out and player_out in purchase_prices:
                    del purchase_prices[player_out]

            logger.info(f"Calculated purchase prices for {len(purchase_prices)} players")
            return purchase_prices

        except Exception as e:
            logger.error(f"Failed to fetch transfers for team {team_id}: {e}")
            return {}

    async def _enrich_picks_with_player_data(
        self, picks: list[TeamPick], purchase_prices: Dict[int, int] = None
    ) -> list[TeamPick]:
        """Enrich team picks with player data and purchase prices.

        Args:
            picks: List of team picks
            purchase_prices: Dictionary mapping player IDs to purchase prices

        Returns:
            List of enriched team picks
        """
        if not picks:
            return picks

        if purchase_prices is None:
            purchase_prices = {}

        # Get player lookup
        players_lookup = await self._get_players_lookup()

        # Get calculated expected points for all players
        expected_points_map = await self.expected_points_service.calculate_expected_points_for_all_players()

        # Enrich each pick
        enriched_picks = []
        for pick in picks:
            player_data = players_lookup.get(pick.element, {})

            # Get calculated expected points (fallback to None if not available)
            expected_points = expected_points_map.get(pick.element)

            enriched_pick = TeamPick(
                element=pick.element,
                position=pick.position,
                multiplier=pick.multiplier,
                is_captain=pick.is_captain,
                is_vice_captain=pick.is_vice_captain,
                player_name=player_data.get("web_name"),
                player_first_name=player_data.get("first_name"),
                player_second_name=player_data.get("second_name"),
                player_team=player_data.get("team"),
                player_team_name=player_data.get("team_name"),
                player_team_short_name=player_data.get("team_short_name"),
                player_team_code=player_data.get("team_code"),
                player_position=player_data.get("element_type"),
                player_cost=player_data.get("now_cost"),
                purchase_price=purchase_prices.get(pick.element),
                expected_points=expected_points,
            )
            enriched_picks.append(enriched_pick)

        return enriched_picks

    async def _calculate_free_transfers(self, team_id: int, current_event: int) -> int:
        """Calculate available free transfers for next gameweek.

        Args:
            team_id: FPL team entry ID
            current_event: Current (last completed) gameweek number

        Returns:
            Number of free transfers available for the next gameweek (1-5)
        """
        try:
            # Fetch gameweek-by-gameweek history
            logger.info(f"=== FREE TRANSFER CALCULATION FOR TEAM {team_id} ===")
            logger.info(f"Current (last completed) gameweek: {current_event}")

            history_data = await self.fpl_client.get_entry_history(team_id)
            current_history = history_data.get("current", [])

            if not current_history or current_event < 1:
                logger.info("No history data available - defaulting to 1 FT")
                return 1  # Default to 1 FT

            logger.info(f"Total gameweeks in history: {len(current_history)}")
            logger.info(f"Raw history data sample (first GW): {current_history[0] if current_history else 'None'}")

            # Print all gameweek data for debugging
            for gw_data in current_history:
                event = gw_data.get("event")
                active_chip = gw_data.get("active_chip")
                event_transfers = gw_data.get("event_transfers", 0)
                event_transfers_cost = gw_data.get("event_transfers_cost", 0)
                logger.info(
                    f"GW{event}: transfers={event_transfers}, cost={event_transfers_cost}, "
                    f"chip={active_chip if active_chip else 'None'}"
                )

            logger.info(f"\n--- Analyzing transfers to calculate FT for GW{current_event + 1} ---")

            # Track FT week by week going FORWARD from GW1
            # You get 1 FT for GW2 (after GW1 completes)
            # Then you can bank up to 5 FT total
            available_ft = 0  # Start with 0 (for calculating what happens after each GW)
            last_wildcard_gw = 0

            for gw_data in current_history:
                event = gw_data.get("event")

                # Only process gameweeks up to current_event
                if event > current_event:
                    break

                active_chip = gw_data.get("active_chip")
                event_transfers = gw_data.get("event_transfers", 0)
                event_transfers_cost = gw_data.get("event_transfers_cost", 0)

                logger.info(f"GW{event}: Started with {available_ft} FT")

                # Check for wildcards and free hits (they reset free transfers)
                if active_chip in ["wildcard", "freehit"]:
                    logger.info(f"  ➜ {active_chip.upper()} used - unlimited transfers")
                    # After wildcard/freehit, you get 1 FT for next GW
                    available_ft = 1
                    logger.info(f"  ➜ Next GW will have {available_ft} FT")
                    last_wildcard_gw = event
                    continue

                # Check if they took a hit
                if event_transfers_cost > 0:
                    # Calculate how many paid transfers (4 points per transfer)
                    paid_transfers = event_transfers_cost // 4
                    free_used = event_transfers - paid_transfers
                    logger.info(f"  ➜ Made {event_transfers} transfers ({free_used} free, {paid_transfers} paid, cost={event_transfers_cost})")
                    # Subtract free transfers used, then add 1 for next week
                    available_ft = max(0, available_ft - free_used) + 1
                    logger.info(f"  ➜ Next GW will have {available_ft} FT")
                elif event_transfers > 0:
                    # Used free transfers without taking a hit
                    logger.info(f"  ➜ Made {event_transfers} free transfers")
                    # Subtract transfers used, then add 1 for next week (min 1)
                    available_ft = max(1, available_ft - event_transfers + 1)
                    logger.info(f"  ➜ Next GW will have {available_ft} FT")
                else:
                    # No transfers made - add 1 FT for next week (max 5)
                    available_ft = min(available_ft + 1, 5)
                    logger.info(f"  ➜ No transfers - banking FT")
                    logger.info(f"  ➜ Next GW will have {available_ft} FT")

            logger.info(f"\n=== FINAL CALCULATION ===")
            logger.info(f"After GW{current_event}: {available_ft} FT available for GW{current_event + 1}")
            logger.info(f"=====================================\n")
            return available_ft

        except Exception as e:
            logger.error(f"Failed to calculate free transfers for team {team_id}: {e}")
            return 1  # Default to 1 FT on error
