"""FPL API HTTP client with retry logic."""

import logging
from typing import Any, Dict
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.exceptions import ExternalAPIException

logger = logging.getLogger(__name__)


class FPLClient:
    """HTTP client for Fantasy Premier League API."""

    def __init__(self, client: httpx.AsyncClient, base_url: str, max_retries: int = 3):
        """Initialize FPL client.

        Args:
            client: HTTPX async client instance
            base_url: Base URL for FPL API
            max_retries: Maximum number of retry attempts
        """
        self.client = client
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        reraise=True,
    )
    async def get(self, endpoint: str) -> Dict[str, Any]:
        """Make GET request to FPL API with retry logic.

        Args:
            endpoint: API endpoint (without base URL)

        Returns:
            JSON response as dictionary

        Raises:
            ExternalAPIException: If request fails after retries
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.info(f"Making request to FPL API: {url}")

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Successfully retrieved data from: {url}")
            return data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from FPL API: {e.response.status_code} - {url}")
            raise ExternalAPIException(
                f"FPL API returned error: {e.response.status_code}"
            ) from e

        except httpx.TimeoutException as e:
            logger.error(f"Timeout requesting FPL API: {url}")
            raise ExternalAPIException("FPL API request timed out") from e

        except httpx.NetworkError as e:
            logger.error(f"Network error requesting FPL API: {url}")
            raise ExternalAPIException("Network error connecting to FPL API") from e

        except Exception as e:
            logger.error(f"Unexpected error requesting FPL API: {url} - {str(e)}")
            raise ExternalAPIException(f"Unexpected error: {str(e)}") from e

    async def get_bootstrap_static(self) -> Dict[str, Any]:
        """Get bootstrap-static data (all players, teams, gameweeks).

        Returns:
            Bootstrap static data containing players, teams, events, etc.
        """
        return await self.get("/bootstrap-static/")

    async def get_entry(self, entry_id: int) -> Dict[str, Any]:
        """Get team entry data.

        Args:
            entry_id: FPL team entry ID

        Returns:
            Team entry data
        """
        return await self.get(f"/entry/{entry_id}/")

    async def get_entry_picks(self, entry_id: int, event: int) -> Dict[str, Any]:
        """Get team picks for a specific gameweek.

        Args:
            entry_id: FPL team entry ID
            event: Gameweek number

        Returns:
            Team picks for the gameweek
        """
        return await self.get(f"/entry/{entry_id}/event/{event}/picks/")

    async def get_entry_transfers(self, entry_id: int) -> Dict[str, Any]:
        """Get team transfer history and info.

        Args:
            entry_id: FPL team entry ID

        Returns:
            Transfer history and remaining free transfers
        """
        return await self.get(f"/entry/{entry_id}/transfers/")

    async def get_my_team(self, entry_id: int) -> Dict[str, Any]:
        """Get my team info including free transfers.

        Args:
            entry_id: FPL team entry ID

        Returns:
            Team info including picks, chips, and transfers object with free transfer limit
        """
        return await self.get(f"/my-team/{entry_id}/")

    async def get_fixtures(self) -> list[Dict[str, Any]]:
        """Get all fixtures with difficulty ratings.

        Returns:
            List of all fixtures with team IDs, difficulty ratings, and home/away info
        """
        return await self.get("/fixtures/")

    async def get_element_summary(self, element_id: int) -> Dict[str, Any]:
        """Get detailed player summary including gameweek history.

        Args:
            element_id: Player element ID

        Returns:
            Player summary with gameweek-by-gameweek history and fixtures
        """
        return await self.get(f"/element-summary/{element_id}/")

    async def get_entry_history(self, entry_id: int) -> Dict[str, Any]:
        """Get team's gameweek-by-gameweek history.

        Args:
            entry_id: FPL team entry ID

        Returns:
            Historical data for each gameweek including transfers, chips used, etc.
        """
        return await self.get(f"/entry/{entry_id}/history/")
