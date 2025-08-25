"""
Base schemas and common types used across all DTOs
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


class ApiStatus(str, Enum):
    """API response status enumeration"""
    SUCCESS = "success"
    ERROR = "error"
    DEGRADED = "degraded"


class SortOrder(str, Enum):
    """Sort order enumeration"""
    ASC = "asc"
    DESC = "desc"


class CacheStatus(str, Enum):
    """Cache status enumeration"""
    HIT = "hit"
    MISS = "miss"
    STALE = "stale"
    EXPIRED = "expired"


class DataSource(str, Enum):
    """Data source enumeration"""
    FPL_API = "FPL_API"
    CACHE = "CACHE"
    DATABASE = "DATABASE"
    MOCK = "MOCK"


class BaseResponseDTO(BaseModel):
    """Base response DTO with common fields"""
    status: ApiStatus
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    message: Optional[str] = None

    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "status": "success",
                "timestamp": "2024-01-15T10:30:00Z",
                "message": "Request processed successfully"
            }
        }


class PaginationDTO(BaseModel):
    """Pagination information"""
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, le=100, description="Items per page")
    total_count: int = Field(ge=0, description="Total number of items")
    total_pages: int = Field(ge=0, description="Total number of pages")
    has_next_page: bool = Field(description="Whether there are more pages")
    has_previous_page: bool = Field(description="Whether there are previous pages")

    @validator('total_pages', always=True)
    def calculate_total_pages(cls, v, values):
        if 'total_count' in values and 'page_size' in values:
            import math
            return math.ceil(values['total_count'] / values['page_size'])
        return v

    @validator('has_next_page', always=True)
    def calculate_has_next_page(cls, v, values):
        if 'page' in values and 'total_pages' in values:
            return values['page'] < values['total_pages']
        return False

    @validator('has_previous_page', always=True)
    def calculate_has_previous_page(cls, v, values):
        if 'page' in values:
            return values['page'] > 1
        return False


class ResponseMetadataDTO(BaseModel):
    """Response metadata with performance and source information"""
    data_source: DataSource = Field(description="Source of the data")
    cache_status: Optional[CacheStatus] = Field(None, description="Cache hit/miss status")
    execution_time_ms: Optional[float] = Field(None, ge=0, description="Execution time in milliseconds")
    api_version: str = Field(default="1.0.0", description="API version")
    rate_limit_remaining: Optional[int] = Field(None, ge=0, description="Remaining rate limit")
    rate_limit_reset: Optional[str] = Field(None, description="Rate limit reset timestamp")
    request_id: Optional[str] = Field(None, description="Unique request identifier")
