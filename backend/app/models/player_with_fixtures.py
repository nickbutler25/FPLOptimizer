"""Player with fixture difficulty model."""

from typing import List, Optional
from pydantic import BaseModel, Field


class PlayerWithFixtures(BaseModel):
    """Player with expected points for upcoming fixtures."""

    id: int = Field(..., description="Unique player ID")
    web_name: str = Field(..., description="Player web name (short name)")
    first_name: str = Field(..., description="Player first name")
    second_name: str = Field(..., description="Player surname")
    team: int = Field(..., description="Team ID")
    team_name: Optional[str] = Field(None, description="Team name")
    element_type: int = Field(..., description="Player position (1=GK, 2=DEF, 3=MID, 4=FWD)")
    position: Optional[str] = Field(None, description="Position name")
    now_cost: int = Field(..., description="Current cost in £0.1m units")
    total_points: int = Field(..., description="Total points scored this season")
    form: str = Field(..., description="Recent form rating")
    selected_by_percent: str = Field(..., description="Percentage of teams selecting player")
    minutes: int = Field(..., description="Minutes played")
    status: str = Field(..., description="Availability status (a=available, d=doubtful, i=injured, etc.)")
    news: str = Field(default="", description="Latest player news")
    chance_of_playing_next_round: Optional[int] = Field(None, description="Chance of playing percentage")

    # Expected points for next 5 gameweeks
    expected_points_gw1: float = Field(..., description="Expected points for GW+1")
    expected_points_gw2: float = Field(..., description="Expected points for GW+2")
    expected_points_gw3: float = Field(..., description="Expected points for GW+3")
    expected_points_gw4: float = Field(..., description="Expected points for GW+4")
    expected_points_gw5: float = Field(..., description="Expected points for GW+5")
    expected_points_total: float = Field(..., description="Total expected points over 5 GWs")

    class Config:
        """Pydantic config."""

        from_attributes = True