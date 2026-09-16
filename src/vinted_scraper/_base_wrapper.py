"""Base Vinted wrapper with shared logic for sync and async variants."""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, NoReturn, Optional, Tuple

from .models import VintedSession
from .utils import (
    API_CATALOG_ITEMS,
    API_ITEM_PAGE,
    SESSION_COOKIE_NAME,
    api_base_url,
    format_cookie_header,
    get_cookie_headers,
    get_curl_headers,
    get_httpx_config,
    get_random_user_agent,
    log_constructor,
    site_base_url,
    url_validator,
)

_log = logging.getLogger(__name__)


@dataclass
class BaseVintedWrapper:
    """Shared base for synchronous and asynchronous Vinted API wrappers.

    Contains all non-I/O logic: URL validation, defaults, header building,
    response handling, and retry/cookie logic.

    Attributes:
        baseurl: Vinted domain URL (e.g., "https://www.vinted.com").
        session: The API identity (cookies + CSRF token + anonymous id) as a
            ``VintedSession``. Auto-fetched when None or empty.
        user_agent: Custom user agent string. Auto-generated if None.
        config: httpx client configuration dict.
        cookie_names: List of cookie names to extract.
            Defaults to ["access_token_web"].
    """

    baseurl: str
    session: Optional[VintedSession] = None
    user_agent: Optional[str] = None
    config: Optional[Dict] = None
    cookie_names: Optional[List[str]] = None

    def _needs_session(self) -> bool:
        """Return whether a session must be fetched from the landing page.

        Returns:
            ``True`` when the session is unset or empty.
        """
        return self.session is None or self.session.is_empty()

    def _validate_and_init(self) -> Tuple[Dict, Dict]:
        """Validate base URL, set defaults, and return both httpx configs.

        Called by subclass ``__post_init__`` implementations.

        Returns:
            Tuple ``(site_config, api_config)``, each suitable for passing to
            ``httpx.Client`` or ``httpx.AsyncClient``.

        Raises:
            RuntimeError: If the base URL is invalid.
        """
        if not url_validator(self.baseurl):
            _log.error("'%s' is not a valid url", self.baseurl)
            raise RuntimeError(f"'{self.baseurl}' is not a valid url, please check it!")

        log_constructor(
            log=_log,
            self=self,
            baseurl=self.baseurl,
            user_agent=self.user_agent,
            session=self.session,
            config=self.config,
        )

        if self.user_agent is None:
            self.user_agent = get_random_user_agent()
        if self.cookie_names is None:
            self.cookie_names = [SESSION_COOKIE_NAME]

        assert self.cookie_names is not None  # nosec: guaranteed by above

        # Normalize to the www. site form; derive the api. host from it.
        self.baseurl = site_base_url(self.baseurl)
        api_base = api_base_url(self.baseurl)

        return (
            get_httpx_config(self.baseurl, self.config),
            get_httpx_config(api_base, self.config),
        )

    # -- curl helpers ---------------------------------------------------------

    def _build_curl_headers(self) -> Dict[str, str]:
        """Build headers for an API request.

        Returns:
            Header dictionary.
        """
        return get_curl_headers(self.baseurl, self.user_agent, self.session)

    def _build_page_headers(self) -> Dict[str, str]:
        """Build browser-like headers for an item page (document) request.

        Returns:
            Header dictionary including the session cookie, if available.
        """
        headers = get_cookie_headers(self.baseurl, self.user_agent)
        cookies = self.session.cookies if self.session else {}
        cookie_str = format_cookie_header(cookies)
        if cookie_str:
            headers["Cookie"] = cookie_str
        return headers

    @staticmethod
    def _handle_curl_response(response, endpoint: str) -> Dict[str, Any]:
        """Process a successful (200) curl response.

        Args:
            response: httpx response object.
            endpoint: The endpoint that was called.

        Returns:
            Parsed JSON dict.

        Raises:
            RuntimeError: If JSON parsing fails.
        """
        try:
            return response.json()
        except ValueError as e:
            _log.error("Failed to parse JSON response from %s: %s", endpoint, e)
            raise RuntimeError(f"Invalid JSON response from {endpoint}: {e}") from e

    @staticmethod
    def _raise_curl_error(endpoint: str, status_code: int) -> NoReturn:
        """Raise for a non-200/non-401 curl response.

        Args:
            endpoint: The endpoint that was called.
            status_code: HTTP status code received.

        Raises:
            RuntimeError: Always.
        """
        raise RuntimeError(
            f"Cannot perform API call to endpoint {endpoint}, error code: {status_code}"
        )

    # -- search / item helpers ------------------------------------------------

    @staticmethod
    def _search_endpoint() -> str:
        """Return the catalog search endpoint (relative path)."""
        return API_CATALOG_ITEMS

    @staticmethod
    def _item_endpoint(item_id: str) -> str:
        """Return the public item page (HTML) endpoint for the given item_id.

        The JSON item endpoint (``/api/v2/items/{id}/details``) is blocked by the
        anti-bot protection and returns ``403`` (see
        https://github.com/Giglium/vinted_scraper/issues/59). This public item
        page is a plain document navigation and is not blocked the same way; the
        item metadata is read from its OpenGraph ``<head>`` tags.

        Args:
            item_id: The unique identifier of the item.
        """
        return API_ITEM_PAGE.format(item_id=item_id)

    def _get_cookie_headers(self) -> Dict:
        """Build headers for the cookie-fetch request.

        Returns:
            Dictionary of HTTP headers.
        """
        return get_cookie_headers(self.baseurl, self.user_agent)
