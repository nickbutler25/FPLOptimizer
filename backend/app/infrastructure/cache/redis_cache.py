"""Redis cache implementation."""

import json
import logging
from typing import Any, Optional
import redis.asyncio as redis

from app.core.exceptions import CacheException

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache implementation with async support."""

    def __init__(self, redis_url: str, ttl: int = 300):
        """Initialize Redis cache.

        Args:
            redis_url: Redis connection URL
            ttl: Default time-to-live in seconds
        """
        self.redis_url = redis_url
        self.ttl = ttl
        self._client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self._client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            await self._client.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Cache will be disabled.")
            self._client = None

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._client:
            await self._client.close()
            logger.info("Disconnected from Redis")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self._client:
            return None

        try:
            value = await self._client.get(key)
            if value:
                logger.debug(f"Cache hit for key: {key}")
                return json.loads(value)
            logger.debug(f"Cache miss for key: {key}")
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if not specified)

        Returns:
            True if successful, False otherwise
        """
        if not self._client:
            return False

        try:
            serialized_value = json.dumps(value)
            cache_ttl = ttl if ttl is not None else self.ttl
            await self._client.setex(key, cache_ttl, serialized_value)
            logger.debug(f"Cached key: {key} with TTL: {cache_ttl}s")
            return True
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self._client:
            return False

        try:
            await self._client.delete(key)
            logger.debug(f"Deleted cache key: {key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False

    async def clear(self) -> bool:
        """Clear all cache entries.

        Returns:
            True if successful, False otherwise
        """
        if not self._client:
            return False

        try:
            await self._client.flushdb()
            logger.info("Cleared all cache entries")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False