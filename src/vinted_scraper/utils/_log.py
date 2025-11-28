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
    user_agent: str,
    session_cookie: str,
    config: Dict,
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
    if log.isEnabledFor(logging.DEBUG):
        log.debug(
            f"Create object {self.__class__.__name__} with baseurl {baseurl}, agent {user_agent}, session_cookie {session_cookie} and config {config}"  # noqa E501
        )


def log_interaction(log: Logger, i: int) -> None:
    """
    Construct a log message for log that print the current interaction

    :param log: the logger object to use for the log message
    :param i: the number of the interaction
    :return: None
    """
    if log.isEnabledFor(logging.DEBUG):
        log.debug(f"Interaction {i}")


def log_sleep(log: Logger, time: int) -> None:
    """
    Log a message indicating the duration of sleep.

    :param log: the logger object to use for the log message
    :param time: the duration of sleep in seconds
    :return: None
    """

    if log.isEnabledFor(logging.DEBUG):
        log.debug(f"Sleeping for {time} seconds")


def log_refresh_cookie(log: Logger) -> None:
    """
    Log a message indicating the cookie refresh.

    :param log: the logger object to use for the log message
    :return: None
    """
    if log.isEnabledFor(logging.DEBUG):
        log.debug("refreshing the cookie")


def log_search(log: Logger, params: Optional[Dict]) -> None:
    """
    Log a message indicating a search API call.

    :param log: the logger object to use for the log message
    :param params: the search parameters (can be None)
    :return: None
    """
    if log.isEnabledFor(logging.DEBUG):
        log.debug(f"Searching with params {params}")


def log_item(log: Logger, item_id: str, params: Optional[Dict]) -> None:
    """
    Log a message indicating an item retrieval API call.

    :param log: the logger object to use for the log message
    :param item_id: the item ID to retrieve
    :param params: the query parameters (can be None)
    :return: None
    """
    if log.isEnabledFor(logging.DEBUG):
        log.debug(f"Fetching item {item_id} with params {params}")


def log_curl(log: Logger, endpoint: str, params: Optional[Dict]) -> None:
    """
    Log a message indicating an internal HTTP request (deprecated, use log_curl_request).

    :param log: the logger object to use for the log message
    :param endpoint: the endpoint being called
    :param params: the query parameters (can be None)
    :return: None
    """
    if log.isEnabledFor(logging.DEBUG):
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
    if log.isEnabledFor(logging.DEBUG):
        # Build full URL with query params
        full_url = f"{base_url}/api/v2{endpoint}"
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
    if log.isEnabledFor(logging.DEBUG):
        log.debug(f"API Response: {endpoint} - Status: {status_code}")
        log.debug(f"Response Headers: {dict(headers)}")
        if body is not None:
            # Truncate body if too long (over 1000 chars)
            if len(body) > 1000:
                log.debug(f"Response Body (truncated): {body[:1000]}...")
            else:
                log.debug(f"Response Body: {body}")
