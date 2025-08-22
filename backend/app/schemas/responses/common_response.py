"""
Common response DTOs used across multiple endpoints
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.base import BaseResponseDTO, ResponseMetadataDTO


class ApiResponseDTO(BaseResponseDTO):
    """
    Generic API response wrapper for single data items
    """
    data: Optional[Any] = Field(None, description="Response data")
    metadata: Optional[ResponseMetadataDTO] = Field(None, description="Response metadata")

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "data": {"id": 1, "name": "Example"},
                "timestamp": "2024-01-15T10:30:00Z",
                "metadata": {
                    "data_source": "FPL_API",
                    "cache_status": "hit",
                    "execution_time_ms": 150.5
                }
            }
        }


class ListResponseDTO(BaseResponseDTO):
    """
    Generic list response with pagination support
    """
    data: List[Any] = Field(default_factory=list, description="List of data items")
    total_count: int = Field(ge=0, description="Total number of items")
    metadata: Optional[ResponseMetadataDTO] = Field(None, description="Response metadata")

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "data": [{"id": 1}, {"id": 2}],
                "total_count": 2,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class ErrorResponseDTO(BaseResponseDTO):
    """
    Error response with detailed error information
    """
    status: str = Field(default="error", const=True)
    error_code: str = Field(description="Machine-readable error code")
    details: Optional[str] = Field(None, description="Detailed error description")
    field_errors: Optional[List[Dict[str, Any]]] = Field(None, description="Field-specific validation errors")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional error context")

    class Config:
        schema_extra = {
            "example": {
                "status": "error",
                "message": "Validation failed",
                "error_code": "VALIDATION_ERROR",
                "details": "One or more fields contain invalid values",
                "field_errors": [
                    {
                        "field": "min_cost",
                        "message": "Must be less than max_cost",
                        "value": 10.0
                    }
                ],
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }