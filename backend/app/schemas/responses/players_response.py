"""
Player-specific response DTOs
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.schemas.base import BaseResponseDTO, ResponseMetadataDTO, PaginationDTO
from app.domain.enums.position import Position
from app.domain.enums.injury_status import InjuryStatus


class PlayerDTO(BaseModel):
    """
    Player data transfer object with comprehensive FPL data
    """
    # Core player information
    id: int = Field(description="Unique player identifier")
    name: str = Field(description="Player full name")
    web_name: Optional[str] = Field(None, description="Player web/short name")
    position: Position = Field(description="Player position")
    team: str = Field(description="Player team name")

    # Financial information
    cost: float = Field(ge=3.0, le=15.0, description="Player cost in millions")

    # Performance metrics
    points: int = Field(ge=0, description="Total points this season")
    points_per_cost: Optional[float] = Field(None, ge=0, description="Points per million cost")
    form: Optional[float] = Field(None, ge=0, le=10, description="Recent form rating")

    # Playing time and statistics
    minutes: Optional[int] = Field(None, ge=0, description="Minutes played this season")
    goals_scored: Optional[int] = Field(None, ge=0, description="Goals scored")
    assists: Optional[int] = Field(None, ge=0, description="Assists provided")
    clean_sheets: Optional[int] = Field(None, ge=0, description="Clean sheets (GK/DEF)")
    bonus: Optional[int] = Field(None, ge=0, description="Bonus points earned")

    # Ownership and transfers
    selected_by_percent: Optional[float] = Field(None, ge=0, le=100, description="Ownership percentage")
    transfers_in: Optional[int] = Field(None, ge=0, description="Transfers in this gameweek")
    transfers_out: Optional[int] = Field(None, ge=0, description="Transfers out this gameweek")

    # Availability and fitness
    injury_status: InjuryStatus = Field(default=InjuryStatus.AVAILABLE, description="Current injury status")
    news: Optional[str] = Field(None, description="Latest news about the player")
    chance_of_playing_this_round: Optional[int] = Field(
        None, ge=0, le=100, description="Chance of playing this gameweek (%)"
    )
    chance_of_playing_next_round: Optional[int] = Field(
        None, ge=0, le=100, description="Chance of playing next gameweek (%)"
    )

    # FPL specific data
    fpl_id: Optional[int] = Field(None, description="Original FPL element ID")
    team_code: Optional[int] = Field(None, description="FPL team code")
    event_points: Optional[int] = Field(None, ge=0, description="Points in current gameweek")
    value_form: Optional[float] = Field(None, description="FPL value form metric")
    value_season: Optional[float] = Field(None, description="FPL value season metric")

    # Additional metadata
    gameweek: Optional[int] = Field(None, ge=1, le=38, description="Current gameweek")
    fixture_difficulty: Optional[int] = Field(None, ge=1, le=5, description="Upcoming fixture difficulty")

    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Mohamed Salah",
                "web_name": "Salah",
                "position": "MID",
                "team": "Liverpool",
                "cost": 13.0,
                "points": 280,
                "points_per_cost": 21.5,
                "form": 8.2,
                "minutes": 2850,
                "goals_scored": 25,
                "assists": 12,
                "selected_by_percent": 45.2,
                "injury_status": "available",
                "fpl_id": 283
            }
        }


class PlayerDetailDTO(PlayerDTO):
    """
    Extended player DTO with additional details
    """
    # Extended statistics
    yellow_cards: Optional[int] = Field(None, ge=0, description="Yellow cards received")
    red_cards: Optional[int] = Field(None, ge=0, description="Red cards received")
    penalties_missed: Optional[int] = Field(None, ge=0, description="Penalties missed")
    penalties_saved: Optional[int] = Field(None, ge=0, description="Penalties saved (GK)")
    saves: Optional[int] = Field(None, ge=0, description="Saves made (GK)")

    # Historical performance
    previous_season_points: Optional[int] = Field(None, ge=0, description="Points from previous season")
    career_points: Optional[int] = Field(None, ge=0, description="Total career FPL points")

    # Advanced metrics
    expected_goals: Optional[float] = Field(None, ge=0, description="Expected goals (xG)")
    expected_assists: Optional[float] = Field(None, ge=0, description="Expected assists (xA)")
    expected_goal_involvements: Optional[float] = Field(None, ge=0, description="Expected goal involvements")

    # Fixture information
    next_fixture: Optional[Dict[str, Any]] = Field(None, description="Next fixture details")
    fixture_list: Optional[List[Dict[str, Any]]] = Field(None, description="Upcoming fixtures")

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Mohamed Salah",
                "position": "MID",
                "team": "Liverpool",
                "cost": 13.0,
                "points": 280,
                "form": 8.2,
                "yellow_cards": 2,
                "expected_goals": 18.5,
                "next_fixture": {
                    "opponent": "Man City",
                    "difficulty": 4,
                    "home": True
                }
            }
        }


class PlayersResponseDTO(BaseResponseDTO):
    """
    Response DTO for players list endpoint
    """
    players: List[PlayerDTO] = Field(description="List of players")
    total_count: int = Field(ge=0, description="Total number of players matching filters")

    # Filtering information
    filters_applied: Optional[Dict[str, Any]] = Field(None, description="Filters that were applied")

    # Pagination (for future enhancement)
    pagination: Optional[PaginationDTO] = Field(None, description="Pagination information")

    # Metadata
    data_source: str = Field(default="FPL_API", description="Source of the data")
    cache_status: Optional[str] = Field(None, description="Cache status")
    execution_time_ms: Optional[float] = Field(None, description="Query execution time")

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "players": [
                    {
                        "id": 1,
                        "name": "Mohamed Salah",
                        "position": "MID",
                        "team": "Liverpool",
                        "cost": 13.0,
                        "points": 280
                    }
                ],
                "total_count": 1,
                "filters_applied": {
                    "positions": ["MID"],
                    "min_cost": 10.0
                },
                "data_source": "FPL_API",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class PlayerDetailResponseDTO(BaseResponseDTO):
    """
    Response DTO for single player detail endpoint
    """
    data: PlayerDetailDTO = Field(description="Detailed player information")
    metadata: Optional[ResponseMetadataDTO] = Field(None, description="Response metadata")

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "data": {
                    "id": 1,
                    "name": "Mohamed Salah",
                    "position": "MID",
                    "team": "Liverpool",
                    "cost": 13.0,
                    "points": 280,
                    "form": 8.2
                },
                "metadata": {
                    "data_source": "FPL_API",
                    "execution_time_ms": 45.2
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }