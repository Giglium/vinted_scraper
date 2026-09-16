# jscpd:ignore-start
# pylint: disable=duplicate-code,too-many-instance-attributes
"""Vinted wrapper for raw JSON responses."""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import httpx

from ._base_wrapper import BaseVintedWrapper
from .models import VintedSession
from .utils import (
    CSRF_MARKER,
    DEFAULT_RETRIES,
    HEAD_END_TAG,
    HTTP_OK,
    HTTP_UNAUTHORIZED,
    STREAM_CHUNK_SIZE,
    ChunkAccumulator,
    build_session,
    handle_session_failure,
    log_cookie_retry,
    log_curl_request,
    log_curl_response,
    log_interaction,
    log_item,
    log_refresh_cookie,
    log_search,
    parse_item_page,
    raise_session_error,
)

_log = logging.getLogger(__name__)


@dataclass
class VintedWrapper(BaseVintedWrapper):
    """Synchronous Vinted API wrapper returning raw JSON responses.

    Handles cookie management, retries, and HTTP requests automatically.
    Returns raw JSON dictionaries instead of typed objects.

    Attributes:
        baseurl: Vinted domain URL (e.g., "https://www.vinted.com").
        session: API identity (VintedSession). Auto-fetched if None or empty.
        user_agent: Custom user agent string. Auto-generated if None.
        config: httpx client configuration dict.
        cookie_names: List of cookie names to extract. Defaults to ["access_token_web"].
        locale: Optional ``Locale`` override (e.g. "en-US"). Read from the
            landing page when None, falling back to a guess from ``baseurl``.

    Example:
        See https://github.com/Giglium/vinted_scraper/blob/main/examples/wrapper.py
    """

    _client: httpx.Client = field(init=False, repr=False)
    _api_client: httpx.Client = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize VintedWrapper after dataclass initialization.

        Validates the base URL, sets up user agent, initializes the two httpx
        clients (site host and ``api.`` host), and fetches the session identity
        (cookie + tokens) when none of its parts were provided.

        Raises:
            RuntimeError: If the base URL is invalid.
        """
        site_config, api_config = self._validate_and_init()
        self._client = httpx.Client(**site_config)
        self._api_client = httpx.Client(**api_config)
        if self._needs_session():
            self.refresh_session()

    def refresh_session(self, retries: int = DEFAULT_RETRIES) -> VintedSession:
        """Manually refresh the session cookie and API tokens.

        Args:
            retries: Number of retry attempts (default: 3).

        Returns:
            The ``VintedSession`` returned by :meth:`fetch_session`.

        Raises:
            RuntimeError: If cookies cannot be fetched after all retries.
        """
        log_refresh_cookie(_log)
        session = VintedWrapper.fetch_session(
            self._client,
            self._get_cookie_headers(),
            self.cookie_names,
            retries,
        )
        self.session = session
        return session

    @staticmethod
    def fetch_session(
        client: httpx.Client,
        headers: Dict,
        cookie_names: List[str],
        retries: int = DEFAULT_RETRIES,
    ) -> VintedSession:
        """Fetch the full session identity from Vinted's landing page.

        Args:
            client: httpx.Client instance.
            headers: HTTP headers dictionary.
            cookie_names: List of cookie names to extract.
            retries: Number of retry attempts (default: 3).

        Returns:
            A ``VintedSession`` with the cookies, CSRF token and anonymous id.

        Raises:
            RuntimeError: If cookies cannot be fetched after all retries.
        """
        response = None

        for i in range(retries):
            log_interaction(_log, i, retries)
            html, response = VintedWrapper._stream_until(
                client, "/", headers, CSRF_MARKER
            )

            if response.status_code == HTTP_OK:
                session = build_session(response, html, cookie_names)
                if session.is_usable():
                    return session

            sleep_time = handle_session_failure(response, i, retries)
            if i < retries - 1:
                time.sleep(sleep_time)

        raise_session_error(client.base_url, response)

    @staticmethod
    def _stream_until(
        client: httpx.Client, url: str, headers: Dict, stop_marker: str
    ) -> Tuple[str, httpx.Response]:
        """Stream ``url``, reading only up to ``stop_marker``.

        Shared by :meth:`item` (stops at ``</head>``) and the session fetch
        (stops at the CSRF marker) so that neither downloads the full page body.
        The chunk-boundary bookkeeping lives in :class:`ChunkAccumulator`.

        Args:
            client: httpx.Client instance.
            url: The URL or endpoint path to request.
            headers: Request headers for the GET.
            stop_marker: The text marker that ends the read.

        Returns:
            Tuple of ``(html, response)``. ``html`` is empty for non-200
            responses.
        """
        acc = ChunkAccumulator(stop_marker)
        with client.stream("GET", url, headers=headers) as response:
            if response.status_code == HTTP_OK:
                for chunk in response.iter_text(chunk_size=STREAM_CHUNK_SIZE):
                    if acc.add(chunk):
                        break
            else:
                response.read()
        return acc.text, response

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
        return self.curl(self._search_endpoint(), params=params, api_endpoint=True)

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

        head_html, response = VintedWrapper._stream_until(
            self._client, endpoint, headers, HEAD_END_TAG
        )
        status_code = response.status_code

        log_curl_response(_log, endpoint, status_code, response.headers, head_html)

        if status_code == HTTP_OK:
            return parse_item_page(item_id, head_html, fields)

        self._raise_curl_error(endpoint, status_code)

    def curl(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        *,
        api_endpoint: bool = False,
        _retries: int = 0,
    ) -> Dict[str, Any]:
        """Send a custom HTTP GET request to a relative Vinted API endpoint.

        The ``endpoint`` is always relative and is concatenated with the chosen
        client's ``base_url``: the ``api.`` host when ``api_endpoint`` is True,
        otherwise the site (``www.``) host. Automatically handles headers,
        cookies, retries, and error responses.

        Args:
            endpoint: Relative API endpoint path (e.g., "/api/v2/users/name").
            params: Optional query parameters.
            api_endpoint: Route the request to the ``api.`` host instead of the
                site host.

        Returns:
            Dictionary containing the parsed JSON response.

        Raises:
            RuntimeError: If response status is not 200 or JSON parsing fails.
        """
        client = self._api_client if api_endpoint else self._client
        headers = self._build_curl_headers()
        log_curl_request(_log, str(client.base_url), endpoint, headers, params)

        response = client.get(endpoint, headers=headers, params=params)

        log_curl_response(
            _log, endpoint, response.status_code, response.headers, response.text
        )

        if response.status_code == HTTP_OK:
            return self._handle_curl_response(response, endpoint)

        if response.status_code == HTTP_UNAUTHORIZED and _retries < DEFAULT_RETRIES:
            log_cookie_retry(_log, response.status_code)
            self.refresh_session()
            return self.curl(
                endpoint, params, api_endpoint=api_endpoint, _retries=_retries + 1
            )

        self._raise_curl_error(endpoint, response.status_code)

    def __enter__(self) -> "VintedWrapper":
        """Enter context manager.

        Returns:
            Self for use in with statement.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # pragma: no cover
        """Exit context manager and close both HTTP clients.

        Args:
            exc_type: Exception type (unused).
            exc_val: Exception value (unused).
            exc_tb: Exception traceback (unused).
        """
        self._client.close()
        self._api_client.close()

    def __del__(self) -> None:  # pragma: no cover
        """Best-effort cleanup of the HTTP clients on garbage collection.

        Prefer using the context manager (``with`` statement) for
        deterministic resource cleanup.
        """
        for attr in ("_client", "_api_client"):
            client = getattr(self, attr, None)
            if client is not None and not client.is_closed:
                client.close()


# jscpd:ignore-end
