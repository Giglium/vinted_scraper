"""
All common function will be placed here
"""

import json
import os
import random
import re
from functools import lru_cache
from typing import Dict, List, Optional


@lru_cache(maxsize=1)
def _load_agents() -> List[Dict]:
    """Load user agents from JSON file (cached)."""
    with open(
        os.path.join(os.path.dirname(__file__), "agents.json"), "r", encoding="utf-8"
    ) as file:
        return json.load(file)


def get_random_user_agent() -> str:
    """
    Returns a random user agent from a predefined list of user agents.

    :return: A user agent
    """
    return random.choice(_load_agents())["ua"]


_URL_PATTERN = re.compile(r"^(https?://)?(www\.)?[\w.-]+\.\w{2,}$")


def url_validator(url: str) -> bool:
    """
    Statically check if a given url is a valid base url, using a regex.

    :param url: The url to validate
    :return: True if the url is valid, False otherwise
    """
    return bool(_URL_PATTERN.match(url))


def get_cookie_headers(base_url: str, user_agent: str) -> Dict:
    """
    Generate browser-like HTTP headers.

    :param base_url: The base url of the website
    :param user_agent: The user agent to use
    :return: A dictionary of headers
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
    """
    Generate browser-like HTTP headers.

    :param base_url: The base url of the website
    :param user_agent: The user agent to use
    :param session_cookies: Dictionary of session cookies
    :return: A dictionary of headers
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
