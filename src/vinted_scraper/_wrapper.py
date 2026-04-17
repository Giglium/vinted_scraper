# jscpd:ignore-start
# pylint: disable=duplicate-code,too-many-instance-attributes
"""Vinted wrapper for raw JSON responses."""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx

from ._base_wrapper import BaseVintedWrapper
from .utils import DEFAULT_RETRIES, HTTP_OK, HTTP_UNAUTHORIZED

_log = logging.getLogger(__name__)


@dataclass
class VintedWrapper(BaseVintedWrapper):
    """Synchronous Vinted API wrapper returning raw JSON responses.

    Handles cookie management, retries, and HTTP requests automatically.
    Returns raw JSON dictionaries instead of typed objects.

    Attributes:
        baseurl: Vinted domain URL (e.g., "https://www.vinted.com").
        session_cookie: Session cookie dict. Auto-fetched if None.
        user_agent: Custom user agent string. Auto-generated if None.
        config: httpx client configuration dict.
        cookie_names: List of cookie names to extract. Defaults to ["access_token_web"].

    Example:
        See https://github.com/Giglium/vinted_scraper/blob/main/examples/wrapper.py
    """

    _client: httpx.Client = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize VintedWrapper after dataclass initialization.

        Validates the base URL, sets up user agent, initializes httpx client,
        and fetches session cookies if not provided.

        Raises:
            RuntimeError: If the base URL is invalid.
        """
        httpx_config = self._validate_and_init()
        self._client = httpx.Client(**httpx_config)
        if self.session_cookie is None:
            self.session_cookie = self.refresh_cookie()

    def refresh_cookie(self, retries: int = DEFAULT_RETRIES) -> Dict[str, str]:
        """Manually refresh the session cookie.

        Args:
            retries: Number of retry attempts (default: 3).

        Returns:
            Dictionary containing session cookies.

        Raises:
            RuntimeError: If cookies cannot be fetched after all retries.
        """
        self._log_refresh_cookie()
        return VintedWrapper.fetch_cookie(
            self._client,
            self._get_cookie_headers(),
            self.cookie_names,
            retries,
        )

    @staticmethod
    def fetch_cookie(
        client: httpx.Client,
        headers: Dict,
        cookie_names: List[str],
        retries: int = DEFAULT_RETRIES,
    ) -> Dict[str, str]:
        """Fetch session cookies from Vinted using HTTP GET request.

        Args:
            client: httpx.Client instance.
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
            response = client.get("/", headers=headers)

            cookies = BaseVintedWrapper._process_cookie_response(response, cookie_names)
            if cookies:
                return cookies

            if response.status_code != HTTP_OK:
                sleep_time = BaseVintedWrapper._handle_cookie_failure(
                    response, i, retries
                )
                time.sleep(sleep_time)

        BaseVintedWrapper._raise_cookie_error(client.base_url, response)

    def search(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Search for items on Vinted.

        Args:
            params: Query parameters. Common parameters:
                - search_text (str): Search query
                - page (int): Page number
                - per_page (int): Items per page
                - price_from (float): Minimum price
                - price_to (float): Maximum price
                - order (str): Sort order
                - catalog_ids (str): Category IDs
                - brand_ids (str): Brand IDs
                - size_ids (str): Size IDs

        Returns:
            Dictionary containing JSON response with search results.
        """
        self._log_search(params)
        return self.curl(self._search_endpoint(), params=params)

    def item(self, item_id: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Retrieve detailed information about a specific item.

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
        return self.curl(self._item_endpoint(item_id), params=params)

    def curl(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        *,
        _retries: int = 0,
    ) -> Dict[str, Any]:
        """Send a custom HTTP GET request to any Vinted API endpoint.

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

        response = self._client.get(endpoint, headers=headers, params=params)

        self._log_curl_response(
            endpoint, response.status_code, response.headers, response.text
        )

        if response.status_code == HTTP_OK:
            return self._handle_curl_response(response, endpoint)

        if response.status_code == HTTP_UNAUTHORIZED and _retries < DEFAULT_RETRIES:
            self._log_cookie_retry(response.status_code)
            self.session_cookie = self.refresh_cookie()
            return self.curl(endpoint, params, _retries=_retries + 1)

        self._raise_curl_error(endpoint, response.status_code)

    def __enter__(self) -> "VintedWrapper":
        """Enter context manager.

        Returns:
            Self for use in with statement.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # pragma: no cover
        """Exit context manager and close HTTP client.

        Args:
            exc_type: Exception type (unused).
            exc_val: Exception value (unused).
            exc_tb: Exception traceback (unused).
        """
        self._client.close()


# jscpd:ignore-end
