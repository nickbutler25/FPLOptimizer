"""Player domain model."""

from typing import Optional
from pydantic import BaseModel, Field


class Player(BaseModel):
    """FPL Player domain model."""

    id: int = Field(..., description="Unique player ID")
    web_name: str = Field(..., description="Player web name (short name)")
    first_name: str = Field(..., description="Player first name")
    second_name: str = Field(..., description="Player surname")
    team: int = Field(..., description="Team ID")
    team_name: Optional[str] = Field(None, description="Team name")
    element_type: int = Field(..., description="Player position (1=GK, 2=DEF, 3=MID, 4=FWD)")
    position: Optional[str] = Field(None, description="Position name")
    now_cost: int = Field(..., description="Current cost in £0.1m units")
    cost_change_start: int = Field(..., description="Cost change from start in £0.1m")
    total_points: int = Field(..., description="Total points scored this season")
    points_per_game: str = Field(..., description="Average points per game")
    form: str = Field(..., description="Recent form rating")
    selected_by_percent: str = Field(..., description="Percentage of teams selecting player")
    minutes: int = Field(..., description="Minutes played")
    goals_scored: int = Field(..., description="Goals scored")
    assists: int = Field(..., description="Assists")
    clean_sheets: int = Field(..., description="Clean sheets")
    goals_conceded: int = Field(..., description="Goals conceded")
    own_goals: int = Field(..., description="Own goals")
    penalties_saved: int = Field(..., description="Penalties saved")
    penalties_missed: int = Field(..., description="Penalties missed")
    yellow_cards: int = Field(..., description="Yellow cards")
    red_cards: int = Field(..., description="Red cards")
    saves: int = Field(..., description="Saves")
    bonus: int = Field(..., description="Bonus points")
    bps: int = Field(..., description="Bonus points system score")
    influence: str = Field(..., description="Influence rating")
    creativity: str = Field(..., description="Creativity rating")
    threat: str = Field(..., description="Threat rating")
    ict_index: str = Field(..., description="ICT index (combined influence/creativity/threat)")
    expected_goals: str = Field(..., description="Expected goals (xG)")
    expected_assists: str = Field(..., description="Expected assists (xA)")
    expected_goal_involvements: str = Field(..., description="Expected goal involvements (xGI)")
    expected_goals_conceded: str = Field(..., description="Expected goals conceded (xGC)")
    status: str = Field(..., description="Availability status (a=available, d=doubtful, i=injured, etc.)")
    news: str = Field(default="", description="Latest player news")
    chance_of_playing_next_round: Optional[int] = Field(None, description="Chance of playing percentage")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "web_name": "Salah",
                "first_name": "Mohamed",
                "second_name": "Salah",
                "team": 10,
                "team_name": "Liverpool",
                "element_type": 3,
                "position": "Midfielder",
                "now_cost": 130,
                "total_points": 245,
                "form": "7.5",
                "selected_by_percent": "45.2",
                "status": "a",
            }
        }
