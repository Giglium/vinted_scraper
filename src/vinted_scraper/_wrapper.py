# jscpd:ignore-start
# pylint: disable=duplicate-code,too-many-instance-attributes
"""Vinted wrapper for raw JSON responses."""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx

from ._base_wrapper import BaseVintedWrapper
from .utils import (
    DEFAULT_RETRIES,
    HTTP_OK,
    HTTP_UNAUTHORIZED,
    log_cookie_retry,
    log_curl_request,
    log_curl_response,
    log_interaction,
    log_item,
    log_refresh_cookie,
    log_search,
    parse_item_page,
)

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
        log_refresh_cookie(_log)
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
            log_interaction(_log, i, retries)
            response = client.get("/", headers=headers)

            cookies = BaseVintedWrapper._process_cookie_response(response, cookie_names)
            if cookies:
                return cookies

            if response.status_code != HTTP_OK:
                sleep_time = BaseVintedWrapper._handle_cookie_failure(
                    response, i, retries
                )
                if i < retries - 1:
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
        log_search(_log, params)
        return self.curl(self._search_endpoint(), params=params)

    def item(self, item_id: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Read item metadata from the public item page (HTML).

        The JSON item endpoint (``/api/v2/items/{id}/details``) is blocked by the
        anti-bot protection and returns ``403`` (see
        https://github.com/Giglium/vinted_scraper/issues/59), so the item data is
        read from the public item page instead. Uses HTTP streaming to download
        only the ``<head>`` section, extracting OpenGraph meta tags without
        fetching the full page body.

        Args:
            item_id: The unique identifier of the item.
            fields: List of ``OgField`` values to extract. Defaults to all
                fields (``[OgField.TITLE, OgField.DESCRIPTION, OgField.URL,
                OgField.IMAGE]``).

        Returns:
            A dict always containing ``id``, plus keys ``title``,
            ``description``, ``url``, and ``image`` (each present only if
            found and requested).

        Raises:
            RuntimeError: If the item page cannot be fetched (non-200 status).
        """
        log_item(_log, item_id, fields)
        endpoint = self._item_endpoint(item_id)
        headers = self._build_page_headers()

        parts: List[str] = []
        with self._client.stream("GET", endpoint, headers=headers) as response:
            status_code = response.status_code
            if status_code == HTTP_OK:
                tail = ""
                for chunk in response.iter_text(chunk_size=4096):
                    parts.append(chunk)
                    # Check boundary: </head> may span two consecutive chunks
                    combined = tail + chunk.lower()
                    if "</head>" in combined:
                        break
                    tail = chunk[-6:].lower()
            else:
                response.read()
        head_html = "".join(parts)

        log_curl_response(_log, endpoint, status_code, response.headers, head_html)

        if status_code == HTTP_OK:
            return parse_item_page(item_id, head_html, fields)

        self._raise_curl_error(endpoint, status_code)

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
        log_curl_request(_log, self.baseurl, endpoint, headers, params)

        response = self._client.get(endpoint, headers=headers, params=params)

        log_curl_response(
            _log, endpoint, response.status_code, response.headers, response.text
        )

        if response.status_code == HTTP_OK:
            return self._handle_curl_response(response, endpoint)

        if response.status_code == HTTP_UNAUTHORIZED and _retries < DEFAULT_RETRIES:
            log_cookie_retry(_log, response.status_code)
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

    def __del__(self) -> None:  # pragma: no cover
        """Best-effort cleanup of the HTTP client on garbage collection.

        Prefer using the context manager (``with`` statement) for
        deterministic resource cleanup.
        """
        if hasattr(self, "_client") and not self._client.is_closed:
            self._client.close()


# jscpd:ignore-end
