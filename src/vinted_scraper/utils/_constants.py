"""Constants used throughout vinted_scraper."""

# Change str to final when 3.7+ support is dropped, because final was introduced from 3.8.
SESSION_COOKIE_NAME: str = "access_token_web"

# HTTP Configuration
DEFAULT_TIMEOUT: float = 10.0
DEFAULT_RETRIES: int = 3
RETRY_BASE_SLEEP: int = 2

# HTTP Status Codes
HTTP_OK: int = 200
HTTP_UNAUTHORIZED: int = 401

# API Base Path
API_BASE_PATH: str = "/api/v2"

# API Endpoints
API_CATALOG_ITEMS: str = f"{API_BASE_PATH}/catalog/items"
API_ITEMS: str = f"{API_BASE_PATH}/items"
