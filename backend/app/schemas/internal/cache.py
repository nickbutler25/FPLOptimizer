"""
Cache-related internal DTOs
Data structures for caching operations and statistics
"""

from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List, Union, Generic, TypeVar
from pydantic import BaseModel, Field, validator
from enum import Enum
import json

T = TypeVar('T')


class CacheStatus(str, Enum):
    """Cache entry status enumeration"""
    VALID = "valid"
    EXPIRED = "expired"
    STALE = "stale"
    MISSING = "missing"
    ERROR = "error"


class CacheOperationType(str, Enum):
    """Cache operation types"""
    GET = "get"
    SET = "set"
    DELETE = "delete"
    CLEAR = "clear"
    REFRESH = "refresh"
    EVICT = "evict"


class CacheBackend(str, Enum):
    """Cache backend types"""
    MEMORY = "memory"
    REDIS = "redis"
    MEMCACHED = "memcached"
    DATABASE = "database"
    FILE = "file"


class CacheEntryDTO(BaseModel):
    """
    Individual cache entry with metadata
    """
    key: str = Field(description="Cache key identifier")
    value: Any = Field(description="Cached value (any serializable type)")

    # Timing information
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Entry creation timestamp")
    expires_at: datetime = Field(description="Entry expiration timestamp")
    last_accessed: datetime = Field(default_factory=datetime.utcnow, description="Last access timestamp")

    # Usage statistics
    hit_count: int = Field(default=0, ge=0, description="Number of times this entry was accessed")
    miss_count: int = Field(default=0, ge=0, description="Number of times this key was requested but not found")

    # Size and metadata
    size_bytes: Optional[int] = Field(None, ge=0, description="Entry size in bytes")
    tags: List[str] = Field(default_factory=list, description="Cache tags for grouping/invalidation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    # Cache-specific fields
    ttl_seconds: int = Field(ge=0, description="Time to live in seconds")
    priority: int = Field(default=1, ge=1, le=10, description="Cache priority (1=lowest, 10=highest)")

    @validator('expires_at', always=True)
    def calculate_expires_at(cls, v, values):
        """Calculate expiration time if not provided"""
        if 'created_at' in values and 'ttl_seconds' in values:
            return values['created_at'] + timedelta(seconds=values['ttl_seconds'])
        return v

    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return datetime.utcnow() > self.expires_at

    @property
    def is_stale(self, stale_threshold_hours: int = 1) -> bool:
        """Check if cache entry is stale (old but not expired)"""
        age = datetime.utcnow() - self.created_at
        return age > timedelta(hours=stale_threshold_hours)

    @property
    def remaining_ttl_seconds(self) -> int:
        """Get remaining TTL in seconds"""
        remaining = self.expires_at - datetime.utcnow()
        return max(0, int(remaining.total_seconds()))

    @property
    def age_seconds(self) -> int:
        """Get entry age in seconds"""
        age = datetime.utcnow() - self.created_at
        return int(age.total_seconds())

    def refresh_access(self) -> None:
        """Update last accessed time and increment hit count"""
        self.last_accessed = datetime.utcnow()
        self.hit_count += 1

    def extend_ttl(self, additional_seconds: int) -> None:
        """Extend the TTL by additional seconds"""
        self.expires_at += timedelta(seconds=additional_seconds)
        self.ttl_seconds += additional_seconds

    class Config:
        schema_extra = {
            "example": {
                "key": "players:all:filters:mid_8.0_12.0",
                "value": {"players": [{"id": 1, "name": "Player"}]},
                "created_at": "2024-01-15T10:30:00Z",
                "expires_at": "2024-01-15T11:30:00Z",
                "hit_count": 5,
                "size_bytes": 1024,
                "ttl_seconds": 3600,
                "tags": ["players", "filters"]
            }
        }


class CacheStatsDTO(BaseModel):
    """
    Comprehensive cache statistics and performance metrics
    """
    # Basic metrics
    total_entries: int = Field(ge=0, description="Total number of cache entries")
    active_entries: int = Field(ge=0, description="Number of non-expired entries")
    expired_entries: int = Field(ge=0, description="Number of expired entries")

    # Hit/miss statistics
    total_hits: int = Field(ge=0, description="Total cache hits")
    total_misses: int = Field(ge=0, description="Total cache misses")
    hit_rate: float = Field(ge=0, le=1, description="Cache hit rate (0-1)")

    # Memory usage
    total_memory_bytes: int = Field(ge=0, description="Total memory usage in bytes")
    average_entry_size_bytes: float = Field(ge=0, description="Average entry size in bytes")
    memory_limit_bytes: Optional[int] = Field(None, description="Memory limit if applicable")
    memory_usage_percent: Optional[float] = Field(None, ge=0, le=100, description="Memory usage percentage")

    # Performance metrics
    average_get_time_ms: float = Field(ge=0, description="Average GET operation time")
    average_set_time_ms: float = Field(ge=0, description="Average SET operation time")
    operations_per_second: float = Field(ge=0, description="Operations per second")

    # Entry lifecycle
    eviction_count: int = Field(ge=0, description="Number of entries evicted")
    expiration_count: int = Field(ge=0, description="Number of entries expired")
    manual_deletion_count: int = Field(ge=0, description="Number of manually deleted entries")

    # Time-based metrics
    oldest_entry_age_seconds: Optional[int] = Field(None, description="Age of oldest entry")
    newest_entry_age_seconds: Optional[int] = Field(None, description="Age of newest entry")
    average_entry_age_seconds: Optional[float] = Field(None, description="Average entry age")

    # Backend information
    backend_type: CacheBackend = Field(description="Cache backend type")
    backend_version: Optional[str] = Field(None, description="Backend version")
    backend_info: Dict[str, Any] = Field(default_factory=dict, description="Backend-specific information")

    # Collection period
    stats_start_time: datetime = Field(description="Statistics collection start time")
    stats_end_time: datetime = Field(description="Statistics collection end time")
    collection_duration_seconds: float = Field(ge=0, description="Stats collection duration")

    @validator('hit_rate', always=True)
    def calculate_hit_rate(cls, v, values):
        """Calculate hit rate from hits and misses"""
        if 'total_hits' in values and 'total_misses' in values:
            total = values['total_hits'] + values['total_misses']
            if total > 0:
                return values['total_hits'] / total
        return 0.0

    @validator('memory_usage_percent', always=True)
    def calculate_memory_usage_percent(cls, v, values):
        """Calculate memory usage percentage"""
        if 'total_memory_bytes' in values and 'memory_limit_bytes' in values:
            if values['memory_limit_bytes'] and values['memory_limit_bytes'] > 0:
                return (values['total_memory_bytes'] / values['memory_limit_bytes']) * 100
        return None

    @validator('collection_duration_seconds', always=True)
    def calculate_collection_duration(cls, v, values):
        """Calculate statistics collection duration"""
        if 'stats_start_time' in values and 'stats_end_time' in values:
            duration = values['stats_end_time'] - values['stats_start_time']
            return duration.total_seconds()
        return v

    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate"""
        return 1.0 - self.hit_rate

    @property
    def efficiency_score(self) -> float:
        """Calculate cache efficiency score (0-1)"""
        factors = [
            self.hit_rate,  # Higher hit rate is better
            min(1.0, self.operations_per_second / 1000),  # Higher ops/sec is better (capped at 1000)
        ]

        # Memory efficiency factor
        if self.memory_usage_percent is not None:
            # Penalty for very high memory usage
            memory_factor = 1.0 if self.memory_usage_percent < 80 else (100 - self.memory_usage_percent) / 20
            factors.append(max(0, memory_factor))

        return sum(factors) / len(factors)

    @property
    def health_status(self) -> str:
        """Get cache health status"""
        if self.efficiency_score >= 0.8:
            return "Excellent"
        elif self.efficiency_score >= 0.6:
            return "Good"
        elif self.efficiency_score >= 0.4:
            return "Fair"
        else:
            return "Poor"

    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "total_entries": 1500,
                "active_entries": 1200,
                "expired_entries": 300,
                "total_hits": 8500,
                "total_misses": 1500,
                "hit_rate": 0.85,
                "total_memory_bytes": 52428800,
                "average_entry_size_bytes": 2048.5,
                "backend_type": "redis",
                "operations_per_second": 450.2
            }
        }


class CacheOperationDTO(BaseModel):
    """
    Individual cache operation record
    """
    operation_type: CacheOperationType = Field(description="Type of cache operation")
    key: str = Field(description="Cache key")

    # Timing
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Operation timestamp")
    duration_ms: float = Field(ge=0, description="Operation duration in milliseconds")

    # Operation details
    success: bool = Field(description="Whether operation was successful")
    error_message: Optional[str] = Field(None, description="Error message if failed")

    # Data information
    value_size_bytes: Optional[int] = Field(None, ge=0, description="Size of value in bytes")
    ttl_seconds: Optional[int] = Field(None, ge=0, description="TTL for SET operations")

    # Context
    tags: List[str] = Field(default_factory=list, description="Operation tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        use_enum_values = True


class CacheConfigDTO(BaseModel):
    """
    Cache configuration parameters
    """
    # Backend configuration
    backend_type: CacheBackend = Field(description="Cache backend type")
    connection_string: Optional[str] = Field(None, description="Backend connection string")

    # Capacity settings
    max_entries: Optional[int] = Field(None, gt=0, description="Maximum number of entries")
    max_memory_bytes: Optional[int] = Field(None, gt=0, description="Maximum memory usage")

    # TTL settings
    default_ttl_seconds: int = Field(default=3600, gt=0, description="Default TTL in seconds")
    max_ttl_seconds: Optional[int] = Field(None, gt=0, description="Maximum allowed TTL")

    # Eviction policy
    eviction_policy: str = Field(default="lru", description="Cache eviction policy")
    eviction_threshold: float = Field(default=0.8, gt=0, le=1, description="Eviction threshold (0-1)")

    # Performance settings
    compression_enabled: bool = Field(default=False, description="Enable value compression")
    serialization_format: str = Field(default="json", description="Value serialization format")

    # Monitoring
    statistics_enabled: bool = Field(default=True, description="Enable statistics collection")
    metrics_interval_seconds: int = Field(default=60, gt=0, description="Metrics collection interval")

    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "backend_type": "redis",
                "max_entries": 10000,
                "max_memory_bytes": 104857600,
                "default_ttl_seconds": 3600,
                "eviction_policy": "lru",
                "compression_enabled": True,
                "statistics_enabled": True
            }
        }


class CacheHealthDTO(BaseModel):
    """
    Cache system health assessment
    """
    # Overall health
    is_healthy: bool = Field(description="Overall cache health status")
    health_score: float = Field(ge=0, le=1, description="Health score (0-1)")
    status_message: str = Field(description="Human-readable status message")

    # Connectivity
    is_connected: bool = Field(description="Whether cache backend is connected")
    connection_latency_ms: Optional[float] = Field(None, ge=0, description="Connection latency")
    last_successful_operation: Optional[datetime] = Field(None, description="Last successful operation")

    # Performance health
    hit_rate_healthy: bool = Field(description="Whether hit rate is acceptable")
    response_time_healthy: bool = Field(description="Whether response times are healthy")
    memory_usage_healthy: bool = Field(description="Whether memory usage is healthy")

    # Capacity health
    storage_available: bool = Field(description="Whether storage space is available")
    within_memory_limits: bool = Field(description="Whether within memory limits")
    eviction_rate_acceptable: bool = Field(description="Whether eviction rate is acceptable")

    # Warnings and recommendations
    warnings: List[str] = Field(default_factory=list, description="Health warnings")
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")

    # Check metadata
    check_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    check_duration_ms: float = Field(ge=0, description="Health check duration")

    @validator('health_score', always=True)
    def calculate_health_score(cls, v, values):
        """Calculate overall health score based on multiple factors"""
        factors = []

        # Connection factor (critical)
        if 'is_connected' in values:
            factors.append(1.0 if values['is_connected'] else 0.0)

        # Performance factors
        health_checks = [
            'hit_rate_healthy',
            'response_time_healthy',
            'memory_usage_healthy',
            'storage_available',
            'within_memory_limits',
            'eviction_rate_acceptable'
        ]

        for check in health_checks:
            if check in values:
                factors.append(1.0 if values[check] else 0.5)

        # Calculate weighted average
        if factors:
            return sum(factors) / len(factors)
        return 0.0

    @property
    def health_grade(self) -> str:
        """Get health grade based on score"""
        if self.health_score >= 0.9:
            return "A"
        elif self.health_score >= 0.8:
            return "B"
        elif self.health_score >= 0.7:
            return "C"
        elif self.health_score >= 0.6:
            return "D"
        else:
            return "F"