"""
Internal filter DTOs used between layers
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from app.domain.enums.position import Position
from app.domain.enums.injury_status import InjuryStatus


class PlayerFiltersDTO(BaseModel):
    """
    Internal filter DTO used between API and business layers
    Contains validated and parsed filter criteria
    """
    positions: Optional[List[Position]] = Field(None, description="Validated position enums")
    teams: Optional[List[str]] = Field(None, description="Team names")
    min_cost: Optional[float] = Field(None, ge=3.0, le=15.0, description="Minimum cost")
    max_cost: Optional[float] = Field(None, ge=3.0, le=15.0, description="Maximum cost")
    min_points: Optional[int] = Field(None, ge=0, description="Minimum points")
    max_points: Optional[int] = Field(None, ge=0, description="Maximum points")
    min_form: Optional[float] = Field(None, ge=0, le=10, description="Minimum form")
    injury_status: Optional[List[InjuryStatus]] = Field(None, description="Allowed injury statuses")
    available_only: Optional[bool] = Field(False, description="Only available players")
    min_minutes: Optional[int] = Field(None, ge=0, description="Minimum minutes")
    min_selected_percent: Optional[float] = Field(None, ge=0, le=100, description="Minimum ownership")
    max_selected_percent: Optional[float] = Field(None, ge=0, le=100, description="Maximum ownership")
    search_term: Optional[str] = Field(None, description="Search term")

    @field_validator('max_cost')
    def validate_cost_range(cls, v, values):
        if v is not None and 'min_cost' in values and values['min_cost'] is not None:
            if v < values['min_cost']:
                raise ValueError('max_cost must be greater than or equal to min_cost')
        return v

    @field_validator('max_points')
    def validate_points_range(cls, v, values):
        if v is not None and 'min_points' in values and values['min_points'] is not None:
            if v < values['min_points']:
                raise ValueError('max_points must be greater than or equal to min_points')
        return v

    @field_validator('max_selected_percent')
    def validate_ownership_range(cls, v, values):
        if v is not None and 'min_selected_percent' in values and values['min_selected_percent'] is not None:
            if v < values['min_selected_percent']:
                raise ValueError('max_selected_percent must be greater than or equal to min_selected_percent')
        return v

    class Config:
        use_enum_values = True


class PlayerSortDTO(BaseModel):
    """
    Internal sort criteria DTO
    """
    field: str = Field(description="Field to sort by")
    order: str = Field(description="Sort order (asc/desc)")

    @field_validator('order')
    def validate_sort_order(cls, v):
        if v.lower() not in ['asc', 'desc']:
            raise ValueError('Sort order must be asc or desc')
        return v.lower()