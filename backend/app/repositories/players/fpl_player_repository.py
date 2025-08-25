"""
FPL Player Repository - Pure Data Access Layer
ONLY responsible for HTTP calls and returning raw FPL API data
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from app.core.config import get_settings
from app.core.exceptions import FPLAPIException, RepositoryException


class FPLPlayerRepository:
    """
    Pure FPL API data repository.

    ONLY responsible for:
    - Making HTTP calls to FPL API
    - Basic error handling and retries  
    - Simple caching of raw API responses
    - Returning raw FPL API data

    NOT responsible for:
    - Data mapping to domain models (business concern)
    - Data validation (business concern)
    - Business logic or filtering
    - Complex error handling or statistics
    """

    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)

        # FPL API configuration
        self.fpl_base_url = self.settings.FPL_API_URL.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=self.settings.FPL_TIMEOUT)
        self.retry_attempts = self.settings.FPL_RETRY_ATTEMPTS

        # Simple caching of raw API responses
        self._bootstrap_cache: Optional[Dict[str, Any]] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(seconds=self.settings.FPL_CACHE_TTL)

        # HTTP session
        self._session: Optional[aiohttp.ClientSession] = None

    # ===== PUBLIC DATA ACCESS INTERFACE =====

    async def get_bootstrap_data(self) -> Dict[str, Any]:
        """
        Get raw bootstrap-static data from FPL API.
        Returns the raw API response - no mapping or processing.
        """
        try:
            # Check cache first
            if self._is_cache_valid():
                self.logger.debug("Repository: Returning cached bootstrap data")
                return self._bootstrap_cache.copy()

            # Fetch fresh data from FPL API
            self.logger.info("Repository: Fetching bootstrap data from FPL API")
            data = await self._fetch_fpl_data("bootstrap-static/")

            # Cache raw response
            self._bootstrap_cache = data
            self._cache_timestamp = datetime.utcnow()

            self.logger.info("Repository: Successfully fetched bootstrap data")
            return data

        except Exception as e:
            self.logger.error(f"Repository: Error fetching bootstrap data: {str(e)}")

            # Return stale cache if available
            if self._bootstrap_cache:
                self.logger.warning("Repository: Returning stale cached data due to error")
                return self._bootstrap_cache.copy()

            raise RepositoryException(
                message=f"Failed to fetch data from FPL API: {str(e)}",
                repository_type="fpl",
                operation="get_bootstrap_data"
            )

    async def get_player_details(self, fpl_player_id: int) -> Dict[str, Any]:
        """
        Get detailed player data from FPL API.
        Returns raw API response for specific player.
        """
        try:
            self.logger.debug(f"Repository: Fetching details for FPL player {fpl_player_id}")
            data = await self._fetch_fpl_data(f"element-summary/{fpl_player_id}/")
            return data

        except Exception as e:
            self.logger.error(f"Repository: Error fetching player details: {str(e)}")
            raise RepositoryException(
                message=f"Failed to fetch player details from FPL API: {str(e)}",
                repository_type="fpl",
                operation="get_player_details"
            )

    async def get_fixtures(self) -> Dict[str, Any]:
        """
        Get fixtures data from FPL API.
        Returns raw fixtures response.
        """
        try:
            self.logger.debug("Repository: Fetching fixtures data")
            data = await self._fetch_fpl_data("fixtures/")
            return data

        except Exception as e:
            self.logger.error(f"Repository: Error fetching fixtures: {str(e)}")
            raise RepositoryException(
                message=f"Failed to fetch fixtures from FPL API: {str(e)}",
                repository_type="fpl",
                operation="get_fixtures"
            )

    async def force_refresh(self) -> bool:
        """Force refresh of cached data"""
        try:
            data = await self._fetch_fpl_data("bootstrap-static/")
            self._bootstrap_cache = data
            self._cache_timestamp = datetime.utcnow()
            return True
        except Exception as e:
            self.logger.error(f"Repository: Force refresh failed: {str(e)}")
            return False

    async def test_connectivity(self) -> bool:
        """Test if FPL API is reachable"""
        try:
            await self._fetch_fpl_data("bootstrap-static/")
            return True
        except Exception:
            return False

    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about current cache state"""
        return {
            "has_cache": self._bootstrap_cache is not None,
            "cache_valid": self._is_cache_valid(),
            "cache_timestamp": self._cache_timestamp.isoformat() if self._cache_timestamp else None,
            "cache_age_seconds": (
                (datetime.utcnow() - self._cache_timestamp).total_seconds()
                if self._cache_timestamp else None
            )
        }

    # ===== PRIVATE HTTP METHODS =====

    async def _fetch_fpl_data(self, endpoint: str) -> Dict[str, Any]:
        """Make HTTP call to FPL API with basic retry logic"""
        url = f"{self.fpl_base_url}/{endpoint.lstrip('/')}"
        session = await self._get_session()

        for attempt in range(self.retry_attempts):
            try:
                self.logger.debug(f"Repository: HTTP GET {url} (attempt {attempt + 1})")

                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.debug(f"Repository: Successfully fetched data from {endpoint}")
                        return data
                    else:
                        error_msg = f"FPL API returned HTTP {response.status}"
                        if attempt < self.retry_attempts - 1:
                            self.logger.warning(f"Repository: {error_msg}, retrying...")
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            continue
                        raise FPLAPIException(error_msg, response.status)

            except aiohttp.ClientError as e:
                error_msg = f"HTTP connection error: {str(e)}"
                if attempt < self.retry_attempts - 1:
                    self.logger.warning(f"Repository: {error_msg}, retrying...")
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise FPLAPIException(error_msg)

            except asyncio.TimeoutError:
                error_msg = f"Request timeout after {self.settings.FPL_TIMEOUT}s"
                if attempt < self.retry_attempts - 1:
                    self.logger.warning(f"Repository: {error_msg}, retrying...")
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise FPLAPIException(error_msg)

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get HTTP session for API calls"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={
                    'User-Agent': f'FPL-Players-Service/{self.settings.API_VERSION}',
                    'Accept': 'application/json'
                }
            )
        return self._session

    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if not self._bootstrap_cache or not self._cache_timestamp:
            return False

        age = datetime.utcnow() - self._cache_timestamp
        return age < self._cache_ttl

    # ===== CLEANUP =====

    async def close(self) -> None:
        """Clean up HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
            self.logger.debug("Repository: HTTP session closed")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
