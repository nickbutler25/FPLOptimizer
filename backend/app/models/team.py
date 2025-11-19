"""Team domain model."""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.team_pick import TeamPick


class Team(BaseModel):
    """FPL Team domain model."""

    # Pydantic v2 configuration
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,  # Allow both field name and alias
        # IMPORTANT: Use field names (not aliases) when serializing
        by_alias=False,
    )

    id: int = Field(..., description="Team entry ID")
    name: str = Field(..., description="Team name")
    player_first_name: str = Field(..., description="Manager first name")
    player_last_name: str = Field(..., description="Manager last name")
    started_event: int = Field(..., description="Gameweek started")
    summary_overall_points: int = Field(..., description="Total points")
    summary_overall_rank: int = Field(..., description="Overall rank")
    summary_event_points: int = Field(..., description="Current gameweek points")
    summary_event_rank: int = Field(..., description="Current gameweek rank")
    current_event: int = Field(..., description="Current gameweek")

    # These fields have different names in FPL API, so we use aliases
    total_transfers: int = Field(..., alias="last_deadline_total_transfers", description="Total transfers made")
    bank: int = Field(..., alias="last_deadline_bank", description="Bank balance in £0.1m units")
    team_value: int = Field(..., alias="last_deadline_value", description="Team value in £0.1m units")

    # Transfers structure from FPL API
    transfers: Optional[dict] = Field(None, description="Transfer information including free transfers")

    picks: Optional[List[TeamPick]] = Field(None, description="Current team picks")
