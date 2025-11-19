"""API response schemas."""

from typing import Generic, TypeVar, Optional, List, Dict
from pydantic import BaseModel, Field

from app.models.player import Player
from app.models.team import Team

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """Base response schema with generic data type."""

    success: bool = Field(..., description="Whether request was successful")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[T] = Field(None, description="Response data")

    class Config:
        """Pydantic config."""

        from_attributes = True


class ErrorDetail(BaseModel):
    """Error detail schema."""

    field: Optional[str] = Field(None, description="Field that caused error")
    message: str = Field(..., description="Error message")
    type: Optional[str] = Field(None, description="Error type")


class ErrorResponse(BaseModel):
    """Error response schema."""

    success: bool = Field(default=False, description="Always false for errors")
    message: str = Field(..., description="Error message")
    errors: Optional[List[ErrorDetail]] = Field(None, description="Detailed errors")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Validation error",
                "errors": [{"field": "team_id", "message": "Team not found", "type": "not_found"}],
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Environment")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {"status": "healthy", "version": "1.0.0", "environment": "production"}
        }


class PlayersResponse(BaseResponse[List[Player]]):
    """Response schema for players list."""

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Players retrieved successfully",
                "data": [
                    {
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
                    }
                ],
            }
        }


class TeamResponse(BaseResponse[Team]):
    """Response schema for team data."""

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Team retrieved successfully",
                "data": {
                    "id": 123456,
                    "name": "My FPL Team",
                    "player_first_name": "John",
                    "player_last_name": "Doe",
                    "summary_overall_points": 1234,
                    "summary_overall_rank": 500000,
                },
            }
        }


class TransferRecommendation(BaseModel):
    """Single transfer recommendation (player in or out)."""

    player_id: int = Field(..., description="Player ID")
    player_name: str = Field(..., description="Player name")
    position: Optional[str] = Field(None, description="Player position")
    cost: Optional[float] = Field(None, description="Player cost in millions (for transfers in)")


class WeeklyTransferSolution(BaseModel):
    """Transfer solution for a single gameweek."""

    gameweek: int = Field(..., description="Gameweek number (0-indexed from current)")
    transfers_in: List[TransferRecommendation] = Field(..., description="Players to transfer in")
    transfers_out: List[TransferRecommendation] = Field(..., description="Players to transfer out")
    expected_points: float = Field(..., description="Expected points for this gameweek")
    transfer_cost: int = Field(..., description="Points penalty for paid transfers")
    free_transfers_used: int = Field(..., description="Number of free transfers used")
    free_transfers_remaining: int = Field(..., description="Free transfers remaining after this week")


class TransferPlanData(BaseModel):
    """Complete transfer plan data."""

    current_gameweek: int = Field(..., description="Current gameweek number")
    weekly_solutions: List[WeeklyTransferSolution] = Field(..., description="Weekly transfer recommendations")
    total_expected_points: float = Field(..., description="Total expected points across all weeks (after costs)")
    total_transfer_cost: int = Field(..., description="Total points penalty from all transfers")
    current_expected_points: float = Field(..., description="Expected points with current squad (no transfers)")
    improvement: float = Field(..., description="Total improvement in points from transfers")


class TransferPlanResponse(BaseResponse[TransferPlanData]):
    """Response schema for transfer plan."""

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Transfer plan generated successfully",
                "data": {
                    "weekly_solutions": [
                        {
                            "gameweek": 0,
                            "transfers_in": [{"player_id": 123, "player_name": "Haaland", "position": "Forward", "cost": 14.5}],
                            "transfers_out": [{"player_id": 456, "player_name": "Watkins", "position": "Forward"}],
                            "expected_points": 45.2,
                            "transfer_cost": 0,
                            "free_transfers_used": 1,
                            "free_transfers_remaining": 1,
                        }
                    ],
                    "total_expected_points": 215.4,
                    "total_transfer_cost": 8,
                    "current_expected_points": 200.0,
                    "improvement": 15.4,
                },
            }
        }
