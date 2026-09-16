"""Constants used throughout vinted_scraper."""

from typing import Final

SESSION_COOKIE_NAME: Final = "access_token_web"

# HTTP Configuration
DEFAULT_TIMEOUT: Final = 10.0
DEFAULT_RETRIES: Final = 3
RETRY_BASE_SLEEP: Final = 2

# HTTP Status Codes
HTTP_OK: Final = 200
HTTP_UNAUTHORIZED: Final = 401

API_CATALOG_ITEMS: Final = "/svc-catalogue/items"
API_ITEM_PAGE: Final = "/items/{item_id}"

WWW_HOST_PREFIX: Final = "www."
API_HOST_PREFIX: Final = "api."

ANON_ID_HEADER: Final = "X-Anon-Id"

HEAD_END_TAG: Final = "</head>"
CSRF_MARKER: Final = "CSRF_TOKEN"
STREAM_CHUNK_SIZE: Final = 4096

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
]
