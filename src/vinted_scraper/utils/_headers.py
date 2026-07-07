"""URL validation and HTTP header generation."""

import re
from typing import Dict, Optional

__all__ = [
    "url_validator",
    "get_cookie_headers",
    "get_curl_headers",
]

_URL_PATTERN = re.compile(r"^https://(www\.)?[\w.-]+\.\w{2,}$")


def url_validator(url: str) -> bool:
    """Validates if a URL is a valid base URL using regex.

    Args:
        url: URL string to validate.

    Returns:
        True if valid, False otherwise.
    """
    return bool(_URL_PATTERN.match(url))


def get_cookie_headers(base_url: str, user_agent: str) -> Dict:
    """Generates browser-like HTTP headers for cookie fetching.

    Args:
        base_url: Base URL of the website.
        user_agent: User agent string.

    Returns:
        Dictionary of HTTP headers.
    """
    return {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "DNT": "1",  # Do Not Track
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Origin": base_url,
        "Referer": base_url,
    }


def get_curl_headers(
    base_url: str, user_agent: str, session_cookies: Optional[Dict[str, str]]
) -> Dict:
    """Generates HTTP headers for Vinted JSON API requests.

    Uses a lean header set appropriate for API endpoints (no browser-specific
    navigation headers like ``Sec-Fetch-*`` or ``Upgrade-Insecure-Requests``).

    Args:
        base_url: Base URL of the website.
        user_agent: User agent string.
        session_cookies: Dictionary of session cookies.

    Returns:
        Dictionary of HTTP headers including Cookie header.
    """
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Origin": base_url,
        "Referer": base_url,
    }
    if session_cookies:
        headers["Cookie"] = "; ".join(f"{k}={v}" for k, v in session_cookies.items())
    return headers
