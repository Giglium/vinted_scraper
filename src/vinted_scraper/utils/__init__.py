"""Utility functions and constants for vinted_scraper.

This module provides common utilities used throughout the package.
"""

# pylint: disable=duplicate-code

from ._constants import (
    API_CATALOG_ITEMS,
    API_ITEM_PAGE,
    DEFAULT_RETRIES,
    DEFAULT_TIMEOUT,
    HTTP_OK,
    HTTP_UNAUTHORIZED,
    RETRY_BASE_SLEEP,
    SESSION_COOKIE_NAME,
)
from ._headers import get_cookie_headers, get_curl_headers, url_validator
from ._httpx import extract_cookie_from_response, get_httpx_config
from ._log import (
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
)
from ._og import parse_item_page
from ._user_agent import get_random_user_agent

__all__ = [
    "SESSION_COOKIE_NAME",
    "DEFAULT_TIMEOUT",
    "DEFAULT_RETRIES",
    "RETRY_BASE_SLEEP",
    "HTTP_OK",
    "HTTP_UNAUTHORIZED",
    "API_CATALOG_ITEMS",
    "API_ITEM_PAGE",
    "extract_cookie_from_response",
    "get_httpx_config",
    "log_constructor",
    "log_cookie_fetch_failed",
    "log_cookie_fetched",
    "log_cookie_retry",
    "log_curl_request",
    "log_curl_response",
    "log_interaction",
    "log_item",
    "log_refresh_cookie",
    "log_search",
    "log_sleep",
    "get_cookie_headers",
    "get_curl_headers",
    "get_random_user_agent",
    "parse_item_page",
    "url_validator",
]
