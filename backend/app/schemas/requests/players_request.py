"""
Player-related request DTOs with minimal validation
API layer focuses on HTTP parsing, business layer handles validation
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class GetPlayersRequestDTO(BaseModel):
    """
    Request DTO for getting players - minimal validation at API layer
    Business service performs comprehensive validation
    """
    positions: Optional[List[str]] = Field(
        None,
        description="List of player positions",
        example=["MID", "FWD"]
    )
    teams: Optional[List[str]] = Field(
        None,
        description="List of team names",
        example=["Liverpool", "Man City"]
    )
    min_cost: Optional[float] = Field(
        None,
        description="Minimum player cost in millions",
        example=8.0
    )
    max_cost: Optional[float] = Field(
        None,
        description="Maximum player cost in millions",
        example=12.0
    )
    min_points: Optional[int] = Field(
        None,
        description="Minimum total points",
        example=100
    )
    max_points: Optional[int] = Field(
        None,
        description="Maximum total points",
        example=300
    )
    min_form: Optional[float] = Field(
        None,
        description="Minimum form rating",
        example=5.0
    )
    available_only: Optional[bool] = Field(
        False,
        description="Only include available players"
    )
    min_minutes: Optional[int] = Field(
        None,
        description="Minimum minutes played",
        example=500
    )
    min_selected_percent: Optional[float] = Field(
        None,
        description="Minimum ownership percentage",
        example=10.0
    )
    max_selected_percent: Optional[float] = Field(
        None,
        description="Maximum ownership percentage",
        example=50.0
    )
    search_term: Optional[str] = Field(
        None,
        max_length=100,
        description="Search term for player names or teams",
        example="salah"
    )

    # Pagination (for future enhancement)
    page: Optional[int] = Field(
        1,
        ge=1,
        description="Page number for pagination"
    )
    page_size: Optional[int] = Field(
        50,
        ge=1,
        le=100,
        description="Number of items per page"
    )

    # Sorting (for future enhancement)
    sort_by: Optional[str] = Field(
        None,
        description="Field to sort by",
        example="points"
    )
    sort_order: Optional[str] = Field(
        "desc",
        description="Sort order: asc or desc"
    )

    class Config:
        extra = "forbid"  # Reject unknown fields
        schema_extra = {
            "example": {
                "positions": ["MID", "FWD"],
                "teams": ["Liverpool", "Arsenal"],
                "min_cost": 8.0,
                "max_cost": 12.0,
                "available_only": True,
                "search_term": "salah"
            }
        }


class GetPlayerRequestDTO(BaseModel):
    """
    Request DTO for getting single player
    """
    player_id: int = Field(
        ...,
        ge=1,
        description="Unique player identifier",
        example=1
    )
    include_details: Optional[bool] = Field(
        True,
        description="Include detailed player statistics"
    )
    include_fixtures: Optional[bool] = Field(
        False,
        description="Include upcoming fixtures information"
    )
    include_history: Optional[bool] = Field(
        False,
        description="Include historical performance data"
    )

    class Config:
        extra = "forbid"
        schema_extra = {
            "example": {
                "player_id": 1,
                "include_details": True,
                "include_fixtures": False
            }
        }