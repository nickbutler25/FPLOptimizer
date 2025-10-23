from dataclasses import dataclass
from typing import List, Optional, Dict

from app.domain.enums.injury_status import InjuryStatus
from app.domain.enums.position import Position


@dataclass
class Player:
    """Core Player domain model with FPL API mapping"""
    id: int
    name: str
    position: Position
    team: str  # Team name from FPL API
    cost: float  # Will be converted from FPL's "now_cost" (in 0.1m units)
    points: int  # "total_points" from FPL API
    points_per_cost: Optional[float] = None

    # FPL specific fields
    form: Optional[float] = None  # "form" from FPL API
    selected_by_percent: Optional[float] = None  # "selected_by_percent"
    minutes: Optional[int] = None  # "minutes"
    goals_scored: Optional[int] = None  # "goals_scored"
    assists: Optional[int] = None  # "assists"
    clean_sheets: Optional[int] = None  # "clean_sheets"
    bonus: Optional[int] = None  # "bonus"
    transfers_in: Optional[int] = None  # "transfers_in_event"
    transfers_out: Optional[int] = None  # "transfers_out_event"
    news: Optional[str] = None  # "news"
    chance_of_playing_this_round: Optional[int] = None  # "chance_of_playing_this_round"
    chance_of_playing_next_round: Optional[int] = None  # "chance_of_playing_next_round"
    injury_status: InjuryStatus = InjuryStatus.AVAILABLE

    # Additional FPL fields
    web_name: Optional[str] = None  # "web_name" - commonly used short name
    fpl_id: Optional[int] = None  # Original FPL element ID
    team_code: Optional[int] = None  # FPL team code
    event_points: Optional[int] = None  # Points in current gameweek
    value_form: Optional[float] = None  # FPL's value form metric
    value_season: Optional[float] = None  # FPL's value season metric
    fixtures: Optional[List[Dict]] = None  # Upcoming fixtures