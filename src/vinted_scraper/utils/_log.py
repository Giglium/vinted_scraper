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
        f"Initializing {self.__class__.__name__}(baseurl={baseurl}, "
        f"user_agent={user_agent[:50] + '...' if user_agent else None}, "
        f"session_cookie={'provided' if session_cookie else 'auto-fetch'}, "
        f"config={config})"
    )


def log_interaction(log: Logger, i: int, retries: int) -> None:
    """
    Log retry attempt for cookie fetch.

    :param log: the logger object to use for the log message
    :param i: the current attempt number
    :param retries: the total number of retries allowed
    :return: None
    """
    log.debug(f"Cookie fetch attempt {i + 1}/{retries}")


def log_sleep(log: Logger, time: int) -> None:
    """
    Log a message indicating the duration of sleep.

    :param log: the logger object to use for the log message
    :param time: the duration of sleep in seconds
    :return: None
    """
    log.debug(f"Sleeping for {time} seconds")


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
    log.debug(f"Calling search() with params: {params}")


def log_item(log: Logger, item_id: str, params: Optional[Dict]) -> None:
    """
    Log a message indicating an item retrieval API call.

    :param log: the logger object to use for the log message
    :param item_id: the item ID to retrieve
    :param params: the query parameters (can be None)
    :return: None
    """
    log.debug(f"Calling item(item_id={item_id}, params={params})")


def log_curl(log: Logger, endpoint: str, params: Optional[Dict]) -> None:
    """
    Log a message indicating an internal HTTP request (deprecated, use log_curl_request).

    :param log: the logger object to use for the log message
    :param endpoint: the endpoint being called
    :param params: the query parameters (can be None)
    :return: None
    """
    log.debug(f"Calling endpoint {endpoint} with params {params}")


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
    log.debug(f"API Request: GET {endpoint} with params {params}")
    log.debug(f"Curl command:\n{curl_cmd}")


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

    log.debug(f"API Response: {endpoint} - Status: {status_code}")
    log.debug(f"Response Headers: {dict(headers)}")
    if body is not None:
        # Truncate body if too long (over 1000 chars)
        if len(body) > 1000:
            log.debug(f"Response Body (truncated): {body[:1000]}...")
        else:
            log.debug(f"Response Body: {body}")


def log_cookie_fetched(log: Logger, cookie_value: str) -> None:
    """
    Log successful cookie fetch.

    :param log: the logger object to use for the log message
    :param cookie_value: the fetched cookie value
    :return: None
    """
    log.debug(f"Session cookie fetched successfully: {cookie_value[:20]}...")


def log_cookie_retry(log: Logger, status_code: int) -> None:
    """
    Log cookie refresh due to 401 error.

    :param log: the logger object to use for the log message
    :param status_code: the HTTP status code that triggered the retry
    :return: None
    """
    log.debug(f"Received {status_code} status, refreshing session cookie and retrying")


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
        f"Cookie fetch failed (attempt {attempt + 1}/{retries}) with status {status_code or 'unknown'}"
    )
