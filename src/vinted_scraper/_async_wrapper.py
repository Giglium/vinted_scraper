# jscpd:ignore-start
# pylint: disable=duplicate-code
"""Async Vinted wrapper for raw JSON responses."""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx

from .utils import (
    API_CATALOG_ITEMS,
    API_ITEMS,
    DEFAULT_RETRIES,
    HTTP_OK,
    HTTP_UNAUTHORIZED,
    RETRY_BASE_SLEEP,
    SESSION_COOKIE_NAME,
    extract_cookie_from_response,
    get_cookie_headers,
    get_curl_headers,
    get_httpx_config,
    get_random_user_agent,
    log_constructor,
    log_cookie_fetch_failed,
    log_cookie_fetched,
    log_cookie_retry,
    log_curl_request,
    log_curl_response,
    log_interaction,
    log_item,
    log_refresh_cookie,
    log_search,
    log_sleep,
    url_validator,
)

_log = logging.getLogger(__name__)


@dataclass
class AsyncVintedWrapper:
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

    baseurl: str
    session_cookie: Optional[Dict[str, str]] = None
    user_agent: Optional[str] = None
    config: Optional[Dict] = None
    cookie_names: Optional[List[str]] = None
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
        if not url_validator(self.baseurl):
            _log.error("'%s' is not a valid url", self.baseurl)
            raise RuntimeError(f"'{self.baseurl}' is not a valid url, please check it!")

        log_constructor(
            log=_log,
            self=self,
            baseurl=self.baseurl,
            user_agent=self.user_agent,
            session_cookie=self.session_cookie,
            config=self.config,
        )

        if self.user_agent is None:
            self.user_agent = get_random_user_agent()
        if self.cookie_names is None:
            self.cookie_names = [SESSION_COOKIE_NAME]
        self._client = httpx.AsyncClient(**get_httpx_config(self.baseurl, self.config))

    async def refresh_cookie(self, retries: int = DEFAULT_RETRIES) -> Dict[str, str]:
        """Manually refresh the session cookie asynchronously.

        Args:
            retries: Number of retry attempts (default: 3).

        Returns:
            Dictionary containing session cookies.

        Raises:
            RuntimeError: If cookies cannot be fetched after all retries.
        """
        log_refresh_cookie(_log)
        return await AsyncVintedWrapper.fetch_cookie(
            self._client,
            get_cookie_headers(self.baseurl, self.user_agent),
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
            log_interaction(_log, i, retries)
            response = await client.get("/", headers=headers)

            if response.status_code == HTTP_OK:
                cookies = extract_cookie_from_response(response, cookie_names)
                if cookies:
                    log_cookie_fetched(_log, str(cookies))
                    return cookies
                _log.warning("Cannot find session cookie in response")
            else:
                log_cookie_fetch_failed(_log, response.status_code, i, retries)
                sleep_time = RETRY_BASE_SLEEP**i
                log_sleep(_log, sleep_time)
                await asyncio.sleep(sleep_time)

        _log.error("Cannot fetch session cookie from %s", client.base_url)
        raise RuntimeError(
            f"Cannot fetch session cookie from {client.base_url}, because of "
            f"status code: {response.status_code if response is not None else 'none'}"
            "different from 200."
        )

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
        log_search(_log, params)
        return await self.curl(API_CATALOG_ITEMS, params=params)

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
        log_item(_log, item_id, params)
        return await self.curl(f"{API_ITEMS}/{item_id}", params=params)

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
        headers = get_curl_headers(self.baseurl, self.user_agent, self.session_cookie)

        log_curl_request(_log, self.baseurl, endpoint, headers, params)

        response = await self._client.get(
            endpoint,
            headers=get_curl_headers(
                self.baseurl, self.user_agent, self.session_cookie
            ),
            params=params,
        )

        log_curl_response(
            _log, endpoint, response.status_code, response.headers, response.text
        )

        # Success
        if response.status_code == HTTP_OK:
            try:
                return response.json()
            except ValueError as e:
                _log.error("Failed to parse JSON response from %s: %s", endpoint, e)
                raise RuntimeError(f"Invalid JSON response from {endpoint}: {e}") from e

        # Fetch (maybe is expired?) the session cookie again and retry the API call
        if response.status_code == HTTP_UNAUTHORIZED:
            log_cookie_retry(_log, response.status_code)
            self.session_cookie = await self.refresh_cookie()
            return await self.curl(endpoint, params)
        raise RuntimeError(
            f"Cannot perform API call to endpoint {endpoint}, error code: {response.status_code}"
        )

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
