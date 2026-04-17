# jscpd:ignore-start
# pylint: disable=duplicate-code
"""Async Vinted wrapper for raw JSON responses."""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx

from ._base_wrapper import BaseVintedWrapper
from .utils import DEFAULT_RETRIES, HTTP_OK, HTTP_UNAUTHORIZED

_log = logging.getLogger(__name__)


@dataclass
class AsyncVintedWrapper(BaseVintedWrapper):
    """Asynchronous Vinted API wrapper returning raw JSON responses.

    Handles cookie management, retries, and async HTTP requests automatically.
    Returns raw JSON dictionaries instead of typed objects.

    Attributes:
        baseurl: Vinted domain URL (e.g., "https://www.vinted.com").
        session_cookie: Session cookie dict. Auto-fetched if None.
        user_agent: Custom user agent string. Auto-generated if None.
        config: httpx client configuration dict.
        cookie_names: List of cookie names to extract. Defaults to ["access_token_web"].

    Example:
        See https://github.com/Giglium/vinted_scraper/blob/main/examples/async_wrapper.py
    """

    _client: httpx.AsyncClient = field(init=False, repr=False)

    @classmethod
    async def create(
        cls,
        baseurl: str,
        user_agent: Optional[str] = None,
        config: Optional[Dict] = None,
        cookie_names: Optional[List[str]] = None,
    ):
        """Factory method to create an AsyncVintedWrapper instance.

        Use this instead of direct instantiation to automatically fetch the session cookie.

        Args:
            baseurl: Vinted domain URL (e.g., "https://www.vinted.com").
            user_agent: Custom user agent string. Auto-generated if None.
            config: httpx client configuration dict.
            cookie_names: List of cookie names to extract. Defaults to ["access_token_web"].

        Returns:
            Initialized AsyncVintedWrapper instance with fetched cookies.
        """
        _log.debug("Creating the async wrapper using the factory method")
        self = cls(
            baseurl, user_agent=user_agent, config=config, cookie_names=cookie_names
        )
        self.session_cookie = await self.refresh_cookie()
        return self

    def __post_init__(self) -> None:
        """Initialize AsyncVintedWrapper after dataclass initialization.

        Validates the base URL, sets up user agent, and initializes httpx async client.

        Raises:
            RuntimeError: If the base URL is invalid.

        Note:
            Use the create() factory method instead of direct instantiation to
            automatically fetch the session cookie.
        """
        httpx_config = self._validate_and_init()
        self._client = httpx.AsyncClient(**httpx_config)

    async def refresh_cookie(self, retries: int = DEFAULT_RETRIES) -> Dict[str, str]:
        """Manually refresh the session cookie asynchronously.

        Args:
            retries: Number of retry attempts (default: 3).

        Returns:
            Dictionary containing session cookies.

        Raises:
            RuntimeError: If cookies cannot be fetched after all retries.
        """
        self._log_refresh_cookie()
        return await AsyncVintedWrapper.fetch_cookie(
            self._client,
            self._get_cookie_headers(),
            self.cookie_names,
            retries,
        )

    @staticmethod
    async def fetch_cookie(
        client: httpx.AsyncClient,
        headers: Dict,
        cookie_names: List[str],
        retries: int = DEFAULT_RETRIES,
    ) -> Dict[str, str]:
        """Fetch session cookies from Vinted using async HTTP GET request.

        Args:
            client: httpx.AsyncClient instance.
            headers: HTTP headers dictionary.
            cookie_names: List of cookie names to extract.
            retries: Number of retry attempts (default: 3).

        Returns:
            Dictionary of extracted session cookies.

        Raises:
            RuntimeError: If cookies cannot be fetched after all retries.
        """
        response = None

        for i in range(retries):
            BaseVintedWrapper._log_cookie_interaction(i, retries)
            response = await client.get("/", headers=headers)

            cookies = BaseVintedWrapper._process_cookie_response(response, cookie_names)
            if cookies:
                return cookies

            if response.status_code != HTTP_OK:
                sleep_time = BaseVintedWrapper._handle_cookie_failure(
                    response, i, retries
                )
                await asyncio.sleep(sleep_time)

        BaseVintedWrapper._raise_cookie_error(client.base_url, response)

    async def search(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Search for items on Vinted asynchronously.

        Args:
            params: Query parameters. Common parameters:
                - search_text: Search query
                - page: Page number
                - per_page: Items per page
                - price_from: Minimum price
                - price_to: Maximum price
                - order: Sort order
                - catalog_ids: Category IDs
                - brand_ids: Brand IDs
                - size_ids: Size IDs

        Returns:
            Dictionary containing JSON response with search results.
        """
        self._log_search(params)
        return await self.curl(self._search_endpoint(), params=params)

    async def item(self, item_id: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Retrieve detailed information about a specific item asynchronously.

        Args:
            item_id: The unique identifier of the item.
            params: Optional query parameters.

        Returns:
            Dictionary containing JSON response with item details.

        Raises:
            RuntimeError: If the item is not found or API returns an error.

        Note:
            It returns a 403 error after a few uses.
            See: https://github.com/Giglium/vinted_scraper/issues/59
        """
        self._log_item(item_id, params)
        return await self.curl(self._item_endpoint(item_id), params=params)

    async def curl(
        self, endpoint: str, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Send an async HTTP GET request to any Vinted API endpoint.

        Automatically handles headers, cookies, retries, and error responses.

        Args:
            endpoint: API endpoint path (e.g., "/api/v2/users/username").
            params: Optional query parameters.

        Returns:
            Dictionary containing the parsed JSON response.

        Raises:
            RuntimeError: If response status is not 200 or JSON parsing fails.
        """
        headers = self._build_curl_headers()
        self._log_curl_request(endpoint, headers, params)

        response = await self._client.get(endpoint, headers=headers, params=params)

        self._log_curl_response(
            endpoint, response.status_code, response.headers, response.text
        )

        if response.status_code == HTTP_OK:
            return self._handle_curl_response(response, endpoint)

        if response.status_code == HTTP_UNAUTHORIZED:
            self._log_cookie_retry(response.status_code)
            self.session_cookie = await self.refresh_cookie()
            return await self.curl(endpoint, params)

        self._raise_curl_error(endpoint, response.status_code)

    async def __aenter__(self) -> "AsyncVintedWrapper":  # pragma: no cover
        """Enter async context manager.

        Returns:
            Self for use in async with statement.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # pragma: no cover
        """Exit async context manager and close HTTP client.

        Args:
            exc_type: Exception type (unused).
            exc_val: Exception value (unused).
            exc_tb: Exception traceback (unused).
        """
        await self._client.aclose()


# jscpd:ignore-end
