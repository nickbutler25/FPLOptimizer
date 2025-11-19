"""Team pick domain model."""

from typing import Optional
from pydantic import BaseModel, Field


class TeamPick(BaseModel):
    """Team player pick."""

    element: int = Field(..., description="Player ID")
    position: int = Field(..., description="Position in team (1-15)")
    multiplier: int = Field(..., description="Point multiplier (0=bench, 1=playing, 2=captain, 3=vice)")
    is_captain: bool = Field(..., description="Is team captain")
    is_vice_captain: bool = Field(..., description="Is vice captain")

    # Enriched player data (populated from bootstrap-static)
    player_name: Optional[str] = Field(None, description="Player display name")
    player_first_name: Optional[str] = Field(None, description="Player first name")
    player_second_name: Optional[str] = Field(None, description="Player last name")
    player_team: Optional[int] = Field(None, description="Player's Premier League team ID")
    player_team_name: Optional[str] = Field(None, description="Player's team name")
    player_team_short_name: Optional[str] = Field(None, description="Player's team short name")
    player_team_code: Optional[int] = Field(None, description="Player's team code for badge URL")
    player_position: Optional[int] = Field(None, description="Player position type")
    player_cost: Optional[int] = Field(None, description="Player current cost in £0.1m units")
    purchase_price: Optional[int] = Field(None, description="Player purchase price in £0.1m units")
    expected_points: Optional[float] = Field(None, description="Expected points for next gameweek")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "element": 1,
                "position": 1,
                "multiplier": 2,
                "is_captain": True,
                "is_vice_captain": False,
                "player_name": "Salah",
                "player_first_name": "Mohamed",
                "player_second_name": "Salah",
                "player_team": 10,
                "player_position": 3,
                "player_cost": 130,
            }
        }
