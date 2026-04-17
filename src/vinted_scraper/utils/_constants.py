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

# API Base Path
API_BASE_PATH: Final = "/api/v2"

# API Endpoints
API_CATALOG_ITEMS: Final = f"{API_BASE_PATH}/catalog/items"
API_ITEMS: Final = f"{API_BASE_PATH}/items"
