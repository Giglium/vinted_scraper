# pylint: disable=line-too-long, too-many-arguments
"""
Most of the log function will placed here.
If a log function required a specific package it will be putted in that package utils.
Es. httpx logger will be put in the httpx utils.
"""

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
    """
    Construct a log message for the constructor of an object.

    :param log: the logger object to use for the log message
    :param self: the object being created
    :param baseurl: the baseurl to log
    :param user_agent: the user_agent to log
    :param session_cookie: the session cookie to log
    :param config: the configuration to log
    :return: None
    """
    log.debug(
        "Initializing %s(baseurl=%s, user_agent=%s, session_cookie=%s, config=%s)",
        self.__class__.__name__,
        baseurl,
        user_agent[:50] + "..." if user_agent else None,
        "provided" if session_cookie else "auto-fetch",
        config,
    )


def log_interaction(log: Logger, i: int, retries: int) -> None:
    """
    Log retry attempt for cookie fetch.

    :param log: the logger object to use for the log message
    :param i: the current attempt number
    :param retries: the total number of retries allowed
    :return: None
    """
    log.debug("Cookie fetch attempt %d/%d", i + 1, retries)


def log_sleep(log: Logger, time: int) -> None:
    """
    Log a message indicating the duration of sleep.

    :param log: the logger object to use for the log message
    :param time: the duration of sleep in seconds
    :return: None
    """
    log.debug("Sleeping for %d seconds", time)


def log_refresh_cookie(log: Logger) -> None:
    """
    Log a message indicating the cookie refresh.

    :param log: the logger object to use for the log message
    :return: None
    """
    log.debug("Refreshing session cookie")


def log_search(log: Logger, params: Optional[Dict]) -> None:
    """
    Log a message indicating a search API call.

    :param log: the logger object to use for the log message
    :param params: the search parameters (can be None)
    :return: None
    """
    log.debug("Calling search() with params: %s", params)


def log_item(log: Logger, item_id: str, params: Optional[Dict]) -> None:
    """
    Log a message indicating an item retrieval API call.

    :param log: the logger object to use for the log message
    :param item_id: the item ID to retrieve
    :param params: the query parameters (can be None)
    :return: None
    """
    log.debug("Calling item(item_id=%s, params=%s)", item_id, params)


def log_curl(log: Logger, endpoint: str, params: Optional[Dict]) -> None:
    """
    Log a message indicating an internal HTTP request (deprecated, use log_curl_request).

    :param log: the logger object to use for the log message
    :param endpoint: the endpoint being called
    :param params: the query parameters (can be None)
    :return: None
    """
    log.debug("Calling endpoint %s with params %s", endpoint, params)


def _build_curl_command(url: str, headers: Dict[str, str]) -> str:
    """
    Build a bash curl command string from the request details.

    :param url: the full URL of the request
    :param headers: the headers dictionary
    :return: a curl command string that can be executed in bash
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
    """
    Log a detailed message for an HTTP request including a reproducible curl command.

    :param log: the logger object to use for the log message
    :param base_url: the base URL of the API
    :param endpoint: the endpoint being called
    :param headers: the request headers
    :param params: the query parameters (can be None)
    :return: None
    """
    if not log.isEnabledFor(logging.DEBUG):
        return

    # Build full URL with query params
    full_url = f"{base_url}{endpoint}"
    if params:
        full_url = f"{full_url}?{urlencode(params)}"

    curl_cmd = _build_curl_command(full_url, headers)
    log.debug("API Request: GET %s with params %s", endpoint, params)
    log.debug("Curl command:\n%s", curl_cmd)


def log_curl_response(
    log: Logger,
    endpoint: str,
    status_code: int,
    headers: Any,
    body: Optional[str] = None,
) -> None:
    """
    Log a detailed message for an HTTP response including status code, headers, and body.

    :param log: the logger object to use for the log message
    :param endpoint: the endpoint that was called
    :param status_code: the HTTP status code of the response
    :param headers: the response headers
    :param body: the response body (can be None to skip body logging)
    :return: None
    """
    if not log.isEnabledFor(logging.DEBUG):
        return

    log.debug("API Response: %s - Status: %d", endpoint, status_code)
    log.debug("Response Headers: %s", dict(headers))
    if body is not None:
        # Truncate body if too long (over 1000 chars)
        if len(body) > 1000:
            log.debug("Response Body (truncated): %s...", body[:1000])
        else:
            log.debug("Response Body: %s", body)


def log_cookie_fetched(log: Logger, cookie_value: str) -> None:
    """
    Log successful cookie fetch.

    :param log: the logger object to use for the log message
    :param cookie_value: the fetched cookie value
    :return: None
    """
    log.debug("Session cookie fetched successfully: %s", cookie_value[:20] + "...")


def log_cookie_retry(log: Logger, status_code: int) -> None:
    """
    Log cookie refresh due to 401 error.

    :param log: the logger object to use for the log message
    :param status_code: the HTTP status code that triggered the retry
    :return: None
    """
    log.debug("Received %d status, refreshing session cookie and retrying", status_code)


def log_cookie_fetch_failed(
    log: Logger, status_code: Optional[int], attempt: int, retries: int
) -> None:
    """
    Log failed cookie fetch attempt.

    :param log: the logger object to use for the log message
    :param status_code: the HTTP status code received
    :param attempt: the current attempt number
    :param retries: the total number of retries allowed
    :return: None
    """
    log.debug(
        "Cookie fetch failed (attempt %d/%d) with status %s",
        attempt + 1,
        retries,
        status_code or "unknown",
    )
