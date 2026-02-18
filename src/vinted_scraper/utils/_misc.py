"""Miscellaneous utility functions.

This module provides common utilities including:
- Random user agent selection
- URL validation
- HTTP header generation
"""

import json
import os
import random
import re
from functools import lru_cache
from typing import Dict, List, Optional


@lru_cache(maxsize=1)
def _load_agents() -> List[Dict]:
    """Loads user agents from JSON file (cached).

    Returns:
        List of user agent dictionaries.
    """
    with open(
        os.path.join(os.path.dirname(__file__), "agents.json"), "r", encoding="utf-8"
    ) as file:
        return json.load(file)


def get_random_user_agent() -> str:
    """Returns a random user agent string.

    Selects randomly from a predefined list of browser user agents.

    Returns:
        Random user agent string.
    """
    return random.choice(_load_agents())["ua"]


_URL_PATTERN = re.compile(r"^(https?://)?(www\.)?[\w.-]+\.\w{2,}$")


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
    """Generates browser-like HTTP headers for API requests.

    Args:
        base_url: Base URL of the website.
        user_agent: User agent string.
        session_cookies: Dictionary of session cookies.

    Returns:
        Dictionary of HTTP headers including Cookie header.
    """
    cookie_str = "; ".join(f"{k}={v}" for k, v in (session_cookies or {}).items())
    return {
        "User-Agent": user_agent,
        "Accept": "application/json, text/plain, */*",
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
        "Cookie": cookie_str,
    }
