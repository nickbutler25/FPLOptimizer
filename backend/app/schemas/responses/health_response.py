"""
Health check response DTOs
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.schemas.base import BaseResponseDTO


class HealthResponseDTO(BaseResponseDTO):
    """
    Comprehensive health check response
    """
    service: str = Field(default="FPL Players Service", description="Service name")
    version: str = Field(description="API version")
    environment: Optional[str] = Field(None, description="Environment (dev/staging/prod)")

    # External dependencies
    fpl_api_status: str = Field(description="FPL API connectivity status")
    fpl_response_time_ms: Optional[float] = Field(None, description="FPL API response time")
    fpl_api_healthy: bool = Field(description="Whether FPL API is healthy")

    # Repository health
    repository_status: Optional[str] = Field(None, description="Repository status")
    repository_type: Optional[str] = Field(None, description="Type of repository in use")
    cached_players: Optional[int] = Field(None, description="Number of cached players")

    # Cache information
    cache_status: Optional[str] = Field(None, description="Cache status")
    data_freshness: Optional[str] = Field(None, description="Data freshness indicator")
    last_cache_refresh: Optional[str] = Field(None, description="Last cache refresh timestamp")

    # System health
    system_cpu_percent: Optional[float] = Field(None, description="CPU usage percentage")
    system_memory_percent: Optional[float] = Field(None, description="Memory usage percentage")
    system_disk_percent: Optional[float] = Field(None, description="Disk usage percentage")
    system_healthy: Optional[bool] = Field(None, description="Overall system health")

    # Performance metrics
    health_check_duration_ms: Optional[float] = Field(None, description="Health check execution time")

    # Error information (when status is not healthy)
    error: Optional[str] = Field(None, description="Error message if unhealthy")
    error_details: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "service": "FPL Players Service",
                "version": "1.0.0",
                "environment": "production",
                "fpl_api_status": "connected",
                "fpl_response_time_ms": 250.5,
                "fpl_api_healthy": True,
                "repository_status": "functional",
                "cached_players": 587,
                "cache_status": "valid",
                "data_freshness": "fresh",
                "system_cpu_percent": 15.2,
                "system_memory_percent": 45.8,
                "system_healthy": True,
                "health_check_duration_ms": 180.3,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class StatusResponseDTO(BaseResponseDTO):
    """
    Detailed status information response
    """
    service: str = Field(description="Service name")
    version: str = Field(description="API version")
    environment: str = Field(description="Current environment")
    debug_mode: bool = Field(description="Whether debug mode is enabled")

    # Architecture information
    architecture: Dict[str, Any] = Field(description="Architecture and design information")

    # Configuration details
    configuration: Dict[str, Any] = Field(description="Service configuration")

    # Runtime information
    runtime: Dict[str, Any] = Field(description="Runtime and system information")

    # Health metrics
    health_metrics: Dict[str, Any] = Field(description="Health check metrics")

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "service": "FPL Players Service",
                "version": "1.0.0",
                "environment": "production",
                "debug_mode": False,
                "architecture": {
                    "pattern": "Clean Architecture with Repository Pattern",
                    "layers": ["API", "Business", "Repository", "Domain"]
                },
                "configuration": {
                    "repository_type": "fpl",
                    "cache_ttl_seconds": 3600
                },
                "runtime": {
                    "uptime_seconds": 86400,
                    "memory_usage_mb": 125.6
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class ReadinessResponseDTO(BaseModel):
    """
    Readiness probe response
    """
    ready: bool = Field(description="Whether service is ready to accept traffic")
    timestamp: str = Field(description="Check timestamp")
    checks: Dict[str, Any] = Field(description="Individual readiness checks")
    error: Optional[str] = Field(None, description="Error message if not ready")

    class Config:
        schema_extra = {
            "example": {
                "ready": True,
                "timestamp": "2024-01-15T10:30:00Z",
                "checks": {
                    "fpl_api_ready": True,
                    "repository_ready": True,
                    "data_available": True
                }
            }
        }


class MetricsResponseDTO(BaseModel):
    """
    Application metrics response
    """
    timestamp: str = Field(description="Metrics collection timestamp")
    health: Dict[str, Any] = Field(description="Health check metrics")
    repository: Dict[str, Any] = Field(description="Repository performance metrics")
    system: Dict[str, Any] = Field(description="System resource metrics")
    application: Dict[str, Any] = Field(description="Application-specific metrics")

    class Config:
        schema_extra = {
            "example": {
                "timestamp": "2024-01-15T10:30:00Z",
                "health": {
                    "total_checks": 1250,
                    "last_check_duration_ms": 180.5
                },
                "repository": {
                    "type": "fpl",
                    "cached_players": 587
                },
                "system": {
                    "cpu_percent": 15.2,
                    "memory_percent": 45.8
                },

                    "version": "1.0.0",
                    "uptime_seconds": 86400
                }
            }
        }
