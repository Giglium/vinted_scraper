"""Utility functions and constants for vinted_scraper.

This module provides common utilities used throughout the package.
"""

# pylint: disable=duplicate-code

from ._constants import (
    ANON_ID_HEADER,
    API_CATALOG_ITEMS,
    API_HOST_PREFIX,
    API_ITEM_PAGE,
    CSRF_MARKER,
    DEFAULT_RETRIES,
    DEFAULT_TIMEOUT,
    HEAD_END_TAG,
    HTTP_OK,
    HTTP_UNAUTHORIZED,
    RETRY_BASE_SLEEP,
    SESSION_COOKIE_NAME,
    STREAM_CHUNK_SIZE,
    WWW_HOST_PREFIX,
)
from ._headers import (
    api_base_url,
    format_cookie_header,
    get_cookie_headers,
    get_curl_headers,
    locale_from_base_url,
    site_base_url,
    url_validator,
)
from ._html import (
    ChunkAccumulator,
    extract_csrf_token,
    extract_locale_from_html,
    parse_item_page,
)
from ._httpx import (
    extract_anon_id_from_response,
    extract_cookie_from_response,
    get_httpx_config,
)
from ._log import (
    log_constructor,
    log_cookie_fetch_failed,
    log_cookie_retry,
    log_curl_request,
    log_curl_response,
    log_interaction,
    log_item,
    log_refresh_cookie,
    log_search,
    log_session_fetched,
    log_sleep,
)
from ._session import build_session, handle_session_failure, raise_session_error
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
    "WWW_HOST_PREFIX",
    "API_HOST_PREFIX",
    "ANON_ID_HEADER",
    "HEAD_END_TAG",
    "CSRF_MARKER",
    "STREAM_CHUNK_SIZE",
    "site_base_url",
    "api_base_url",
    "locale_from_base_url",
    "ChunkAccumulator",
    "extract_csrf_token",
    "extract_locale_from_html",
    "extract_anon_id_from_response",
    "extract_cookie_from_response",
    "get_httpx_config",
    "log_constructor",
    "log_cookie_fetch_failed",
    "log_session_fetched",
    "log_cookie_retry",
    "log_curl_request",
    "log_curl_response",
    "log_interaction",
    "log_item",
    "log_refresh_cookie",
    "log_search",
    "log_sleep",
    "build_session",
    "handle_session_failure",
    "raise_session_error",
    "format_cookie_header",
    "get_cookie_headers",
    "get_curl_headers",
    "get_random_user_agent",
    "parse_item_page",
    "url_validator",
]
