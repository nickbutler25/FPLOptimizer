"""
Cache-related internal DTOs
"""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator


class CacheEntryDTO(BaseModel):
    """
    Internal cache entry structure
    """
    key: str = Field(description="Cache key")
    value: Any = Field(description="Cached value")
    expires_at: datetime = Field(description="Expiration timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    hit_count: int = Field(default=0, ge=0, description="Number of cache hits")

    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return datetime.utcnow() > self.expires_at

    @property
    def ttl_seconds(self) -> int:
        """Get remaining TTL in seconds"""
        remaining = self.expires_at - datetime.utcnow()
        return max(0, int(remaining.total_seconds()))


class CacheStatsDTO(BaseModel):
    """
    Cache statistics DTO
    """
    total_entries: int = Field(ge=0, description="Total number of cache entries")
    expired_entries: int = Field(ge=0, description="Number of expired entries")
    total_hits: int = Field(ge=0, description="Total cache hits")
    total_misses: int = Field(ge=0, description="Total cache misses")
    hit_rate: float = Field(ge=0, le=1, description="Cache hit rate")
    memory_usage_bytes: Optional[int] = Field(None, description="Memory usage in bytes")

    @field_validator('hit_rate', always=True)
    def calculate_hit_rate(cls, v, values):
        if 'total_hits' in values and 'total_misses' in values:
            total = values['total_hits'] + values['total_misses']