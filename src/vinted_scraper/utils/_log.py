# pylint: disable=line-too-long, too-many-arguments
"""Logging utilities for vinted_scraper."""

import logging
from logging import Logger
from typing import Any, Dict, Optional
from urllib.parse import urlencode


def log_constructor(
    *,
    log: Logger,
    self: object,
    baseurl: str,
    user_agent: Optional[str],
    session_cookie: Optional[str],
    config: Optional[Dict],
) -> None:
    """Logs initialization of VintedScraper/VintedWrapper.

    Args:
        log: Logger instance.
        self: The object being initialized.
        baseurl: Base URL being used.
        user_agent: User agent string (truncated in log).
        session_cookie: Session cookie (logged as 'provided' or 'auto-fetch').
        config: Configuration dictionary.
    """
    log.debug(
        f"Initializing {self.__class__.__name__}(baseurl={baseurl}, "
        f"user_agent={user_agent[:50] + '...' if user_agent else None}, "
        f"session_cookie={'provided' if session_cookie else 'auto-fetch'}, "
        f"config={config})"
    )


def log_interaction(log: Logger, i: int, retries: int) -> None:
    """Logs cookie fetch retry attempt.

    Args:
        log: Logger instance.
        i: Current attempt number (0-indexed).
        retries: Total number of retries allowed.
    """
    log.debug(f"Cookie fetch attempt {i + 1}/{retries}")


def log_sleep(log: Logger, time: int) -> None:
    """Logs sleep duration between retries.

    Args:
        log: Logger instance.
        time: Sleep duration in seconds.
    """
    log.debug(f"Sleeping for {time} seconds")


def log_refresh_cookie(log: Logger) -> None:
    """Logs session cookie refresh action.

    Args:
        log: Logger instance.
    """
    log.debug("Refreshing session cookie")


def log_search(log: Logger, params: Optional[Dict]) -> None:
    """Logs search() method call with parameters.

    Args:
        log: Logger instance.
        params: Search parameters dictionary.
    """
    log.debug(f"Calling search() with params: {params}")


def log_item(log: Logger, item_id: str, params: Optional[Dict]) -> None:
    """Logs item() method call with item ID and parameters.

    Args:
        log: Logger instance.
        item_id: Item identifier.
        params: Query parameters dictionary.
    """
    log.debug(f"Calling item(item_id={item_id}, params={params})")


def log_curl(log: Logger, endpoint: str, params: Optional[Dict]) -> None:
    """Logs HTTP request (deprecated, use log_curl_request).

    Args:
        log: Logger instance.
        endpoint: API endpoint path.
        params: Query parameters dictionary.
    """
    log.debug(f"Calling endpoint {endpoint} with params {params}")


def _build_curl_command(url: str, headers: Dict[str, str]) -> str:
    """Builds executable curl command from request details.

    Args:
        url: Full request URL.
        headers: Request headers dictionary.

    Returns:
        Formatted curl command string.
    """
    curl_parts = ["curl"]
    for key, value in headers.items():
        # Escape single quotes in header values
        escaped_value = value.replace("'", "'\\''")
        curl_parts.append(f"-H '{key}: {escaped_value}'")
    curl_parts.append(f"'{url}'")
    return " \\\n  ".join(curl_parts)


def log_curl_request(
    log: Logger,
    base_url: str,
    endpoint: str,
    headers: Dict[str, str],
    params: Optional[Dict],
) -> None:
    """Logs detailed HTTP request with reproducible curl command.

    Args:
        log: Logger instance.
        base_url: API base URL.
        endpoint: API endpoint path.
        headers: Request headers.
        params: Query parameters dictionary.
    """
    if not log.isEnabledFor(logging.DEBUG):
        return

    # Build full URL with query params
    full_url = f"{base_url}{endpoint}"
    if params:
        full_url = f"{full_url}?{urlencode(params)}"

    curl_cmd = _build_curl_command(full_url, headers)
    log.debug(f"API Request: GET {endpoint} with params {params}")
    log.debug(f"Curl command:\n{curl_cmd}")


def log_curl_response(
    log: Logger,
    endpoint: str,
    status_code: int,
    headers: Any,
    body: Optional[str] = None,
) -> None:
    """Logs detailed HTTP response with status, headers, and body.

    Args:
        log: Logger instance.
        endpoint: API endpoint that was called.
        status_code: HTTP status code.
        headers: Response headers.
        body: Response body (truncated if over 1000 chars).
    """
    if not log.isEnabledFor(logging.DEBUG):
        return

    log.debug(f"API Response: {endpoint} - Status: {status_code}")
    log.debug(f"Response Headers: {dict(headers)}")
    if body is not None:
        # Truncate body if too long (over 1000 chars)
        if len(body) > 1000:
            log.debug(f"Response Body (truncated): {body[:1000]}...")
        else:
            log.debug(f"Response Body: {body}")


def log_cookie_fetched(log: Logger, cookie_value: str) -> None:
    """Logs successful cookie fetch.

    Args:
        log: Logger instance.
        cookie_value: Fetched cookie value (truncated in log).
    """
    log.debug(f"Session cookie fetched successfully: {cookie_value[:20]}...")


def log_cookie_retry(log: Logger, status_code: int) -> None:
    """Logs cookie refresh due to 401 Unauthorized.

    Args:
        log: Logger instance.
        status_code: HTTP status code that triggered retry.
    """
    log.debug(f"Received {status_code} status, refreshing session cookie and retrying")


def log_cookie_fetch_failed(
    log: Logger, status_code: Optional[int], attempt: int, retries: int
) -> None:
    """Logs failed cookie fetch attempt.

    Args:
        log: Logger instance.
        status_code: HTTP status code received.
        attempt: Current attempt number (0-indexed).
        retries: Total number of retries allowed.
    """
    log.debug(
        f"Cookie fetch failed (attempt {attempt + 1}/{retries}) with status {status_code or 'unknown'}"
    )
