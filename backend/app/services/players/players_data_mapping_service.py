from typing import List, Dict, Any, Optional

from app.core import logging
from app.domain.entities.player import Player
from app.domain.enums.position import Position
from app.domain.enums.injury_status import InjuryStatus


class PlayersDataMappingService:
    """
    Business service responsible for mapping raw FPL API data to domain models.

    This is a BUSINESS concern because:
    - It involves understanding business rules
    - It makes decisions about data interpretation
    - It applies business logic for derived fields
    - It handles data validation and defaults
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def map_bootstrap_to_players(self, bootstrap_data: Dict[str, Any]) -> List[Player]:
        """
        Map raw FPL bootstrap data to Player domain models.
        Business logic: how to interpret FPL data in our domain.
        """
        elements = bootstrap_data.get("elements", [])
        teams = bootstrap_data.get("teams", [])

        if not elements:
            raise ValueError("No player elements in bootstrap data")

        # Create team lookup for business logic
        team_lookup = {team["id"]: team["name"] for team in teams}

        players = []
        for element in elements:
            try:
                player = self._map_element_to_player(element, team_lookup)
                players.append(player)
            except Exception as e:
                self.logger.warning(f"Failed to map player {element.get('id')}: {e}")
                continue

        self.logger.info(f"Mapped {len(players)} players from FPL data")
        return players

    def _map_element_to_player(self, element: Dict[str, Any], team_lookup: Dict[int, str]) -> Player:
        """
        Map single FPL element to Player domain model.
        Contains business logic for interpretation and calculation.
        """
        # Business rule: How to construct player name
        first_name = element.get("first_name", "").strip()
        second_name = element.get("second_name", "").strip()
        name = f"{first_name} {second_name}".strip() or "Unknown Player"

        # Business rule: Position mapping
        position = self._map_position(element.get("element_type"))

        # Business rule: Team name resolution
        team_id = element.get("team")
        team_name = team_lookup.get(team_id, "Unknown Team")

        # Business rule: Cost conversion (FPL uses 0.1m units)
        raw_cost = element.get("now_cost", 0)
        cost = raw_cost / 10.0

        # Business rule: Points per cost calculation
        points = element.get("total_points", 0)
        points_per_cost = round(points / cost, 2) if cost > 0 else 0.0

        # Business rule: Injury status interpretation
        injury_status = self._determine_injury_status(element)

        # Business rule: Safe number conversion
        form = self._safe_float(element.get("form"))
        selected_percent = self._safe_float(element.get("selected_by_percent"))

        return Player(
            id=element.get("id"),
            name=name,
            position=position,
            team=team_name,
            cost=cost,
            points=points,
            points_per_cost=points_per_cost,
            form=form,
            selected_by_percent=selected_percent,
            minutes=element.get("minutes"),
            goals_scored=element.get("goals_scored"),
            assists=element.get("assists"),
            clean_sheets=element.get("clean_sheets"),
            bonus=element.get("bonus"),
            transfers_in=element.get("transfers_in_event"),
            transfers_out=element.get("transfers_out_event"),
            news=element.get("news") or None,
            chance_of_playing_this_round=element.get("chance_of_playing_this_round"),
            chance_of_playing_next_round=element.get("chance_of_playing_next_round"),
            injury_status=injury_status,
            web_name=element.get("web_name"),
            fpl_id=element.get("id")
        )

    def _map_position(self, element_type: int) -> Position:
        """Business rule: Map FPL element_type to Position enum"""
        mapping = {
            1: Position.GKP,
            2: Position.DEF,
            3: Position.MID,
            4: Position.FWD
        }
        return mapping.get(element_type, Position.MID)  # Default to MID

    def _determine_injury_status(self, element: Dict[str, Any]) -> InjuryStatus:
        """
        Business rule: Determine injury status from multiple FPL fields.
        This involves business logic about what constitutes "injured" vs "doubtful".
        """
        status = element.get("status", "a")
        news = element.get("news", "").lower()
        chance_playing = element.get("chance_of_playing_this_round")

        # Business rules for injury classification
        if status == "i" or "injured" in news or "injury" in news:
            return InjuryStatus.INJURED
        elif status == "s" or "suspended" in news or "suspension" in news:
            return InjuryStatus.SUSPENDED
        elif status == "d" or (chance_playing is not None and chance_playing < 75):
            return InjuryStatus.DOUBTFUL
        else:
            return InjuryStatus.AVAILABLE

    def _safe_float(self, value) -> Optional[float]:
        """Business rule: How to handle invalid numeric data"""
        try:
            return float(value) if value is not None else None
        except (ValueError, TypeError):
            return None

