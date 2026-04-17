"""Base Vinted wrapper with shared logic for sync and async variants."""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, NoReturn, Optional

from .utils import (
    API_CATALOG_ITEMS,
    API_ITEMS,
    HTTP_OK,
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
class BaseVintedWrapper:
    """Shared base for synchronous and asynchronous Vinted API wrappers.

    Contains all non-I/O logic: URL validation, defaults, header building,
    response handling, and retry/cookie logic.

    Attributes:
        baseurl: Vinted domain URL (e.g., "https://www.vinted.com").
        session_cookie: Session cookie dict. Auto-fetched if None.
        user_agent: Custom user agent string. Auto-generated if None.
        config: httpx client configuration dict.
        cookie_names: List of cookie names to extract.
            Defaults to ["access_token_web"].
    """

    baseurl: str
    session_cookie: Optional[Dict[str, str]] = None
    user_agent: Optional[str] = None
    config: Optional[Dict] = None
    cookie_names: Optional[List[str]] = None

    def _validate_and_init(self) -> Dict:
        """Validate base URL, set defaults, and return httpx config.

        Called by subclass ``__post_init__`` implementations.

        Returns:
            Dictionary suitable for passing to ``httpx.Client`` or
            ``httpx.AsyncClient``.

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
            session_cookie=self.session_cookie,
            config=self.config,
        )

        if self.user_agent is None:
            self.user_agent = get_random_user_agent()
        if self.cookie_names is None:
            self.cookie_names = [SESSION_COOKIE_NAME]

        return get_httpx_config(self.baseurl, self.config)

    # -- cookie helpers -------------------------------------------------------

    @staticmethod
    def _process_cookie_response(
        response, cookie_names: List[str]
    ) -> Optional[Dict[str, str]]:
        """Extract cookies from a successful response.

        Args:
            response: httpx response object.
            cookie_names: Cookie names to look for.

        Returns:
            Cookie dict if found, else ``None``.
        """
        if response.status_code == HTTP_OK:
            cookies = extract_cookie_from_response(response, cookie_names)
            if cookies:
                log_cookie_fetched(_log, str(cookies))
                return cookies
            _log.warning("Cannot find session cookie in response")
        return None

    @staticmethod
    def _handle_cookie_failure(response, attempt: int, retries: int) -> float:
        """Log a failed cookie attempt and return the sleep duration.

        Args:
            response: httpx response object.
            attempt: Current attempt number (0-indexed).
            retries: Total retry count.

        Returns:
            Seconds to sleep before the next attempt.
        """
        log_cookie_fetch_failed(_log, response.status_code, attempt, retries)
        sleep_time = RETRY_BASE_SLEEP**attempt
        log_sleep(_log, sleep_time)
        return sleep_time

    @staticmethod
    def _raise_cookie_error(base_url, response) -> NoReturn:
        """Raise after all cookie-fetch retries are exhausted.

        Args:
            base_url: The base URL that was targeted.
            response: Last httpx response (may be ``None``).

        Raises:
            RuntimeError: Always.
        """
        _log.error("Cannot fetch session cookie from %s", base_url)
        raise RuntimeError(
            f"Cannot fetch session cookie from {base_url}, because of "
            f"status code: {response.status_code if response is not None else 'none'}"
            "different from 200."
        )

    # -- curl helpers ---------------------------------------------------------

    def _build_curl_headers(self) -> Dict[str, str]:
        """Build headers for an API request.

        Returns:
            Header dictionary.
        """
        return get_curl_headers(self.baseurl, self.user_agent, self.session_cookie)

    def _log_curl_request(
        self, endpoint: str, headers: Dict[str, str], params: Optional[Dict]
    ) -> None:
        """Log an outgoing API request.

        Args:
            endpoint: API endpoint path.
            headers: Request headers.
            params: Query parameters dictionary.
        """
        log_curl_request(_log, self.baseurl, endpoint, headers, params)

    @staticmethod
    def _log_curl_response(endpoint: str, status_code: int, headers, text: str) -> None:
        """Log an incoming API response.

        Args:
            endpoint: API endpoint that was called.
            status_code: HTTP status code.
            headers: Response headers.
            text: Response body text.
        """
        log_curl_response(_log, endpoint, status_code, headers, text)

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
        """Return the catalog search endpoint."""
        return API_CATALOG_ITEMS

    @staticmethod
    def _item_endpoint(item_id: str) -> str:
        """Return the item details endpoint for the given item_id.

        Args:
            item_id: The unique identifier of the item.
        """
        return f"{API_ITEMS}/{item_id}/details"

    def _log_search(self, params: Optional[Dict]) -> None:
        """Log a search call.

        Args:
            params: Search parameters dictionary.
        """
        log_search(_log, params)

    def _log_item(self, item_id: str, params: Optional[Dict]) -> None:
        """Log an item call.

        Args:
            item_id: Item identifier.
            params: Query parameters dictionary.
        """
        log_item(_log, item_id, params)

    def _log_refresh_cookie(self) -> None:
        """Log a cookie refresh."""
        log_refresh_cookie(_log)

    def _get_cookie_headers(self) -> Dict:
        """Build headers for the cookie-fetch request.

        Returns:
            Dictionary of HTTP headers.
        """
        return get_cookie_headers(self.baseurl, self.user_agent)

    @staticmethod
    def _log_cookie_interaction(attempt: int, retries: int) -> None:
        """Log a cookie-fetch attempt.

        Args:
            attempt: Current attempt number (0-indexed).
            retries: Total number of retries allowed.
        """
        log_interaction(_log, attempt, retries)

    @staticmethod
    def _log_cookie_retry(status_code: int) -> None:
        """Log a 401-triggered cookie retry.

        Args:
            status_code: HTTP status code that triggered retry.
        """
        log_cookie_retry(_log, status_code)
