"""Miscellaneous utility functions.

This module provides common utilities including:
- Random user agent selection
- URL validation
- HTTP header generation
"""

import html as _html
import json
import os
import random
import re
import sys
from functools import lru_cache
from typing import Any, Dict, List, Optional

if sys.version_info >= (3, 9):
    from importlib.resources import files


@lru_cache(maxsize=1)
def _load_agents() -> List[Dict]:
    """Loads user agents from JSON file (cached).

    Uses importlib.resources for reliable access to package data,
    which works correctly even when the package is installed from
    a wheel, zip, or frozen environment.

    Returns:
        List of user agent dictionaries.
    """
    if sys.version_info >= (3, 9):
        data = files(__package__).joinpath("agents.json").read_text(encoding="utf-8")
    else:
        # Fallback for Python 3.8
        with open(
            os.path.join(os.path.dirname(__file__), "agents.json"),
            "r",
            encoding="utf-8",
        ) as file:
            data = file.read()
    return json.loads(data)


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


# <script type="application/ld+json"> ... </script> blocks
_LD_JSON_RE = re.compile(
    r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)
# <meta property="og:description" content="..."> fallback
_OG_DESCRIPTION_RE = re.compile(
    r'<meta[^>]+(?:property|name)="og:description"[^>]+content="([^"]*)"',
    re.IGNORECASE,
)


def _iter_ld_json_objects(data: Any):
    """Yield every object contained in a parsed JSON-LD payload.

    JSON-LD can be a single object, a list of objects, or an object holding an
    ``@graph`` list. This flattens all of those cases.

    Args:
        data: The value returned by ``json.loads`` on a JSON-LD block.

    Yields:
        Each ``dict`` object found in the payload.
    """
    stack = [data]
    while stack:
        node = stack.pop()
        if isinstance(node, list):
            stack.extend(node)
        elif isinstance(node, dict):
            graph = node.get("@graph")
            if isinstance(graph, list):
                stack.extend(graph)
            yield node


def parse_item_page(page_html: str) -> Optional[Dict[str, Any]]:
    """Extract the schema.org ``Product`` metadata from an item page's HTML.

    Vinted embeds each item page with a ``<script type="application/ld+json">``
    block describing the item as a schema.org ``Product`` (with ``name``,
    ``description``, ``brand``, ``offers``, ``image`` ...). This is useful as a
    fallback when the JSON API item endpoint is blocked (see
    https://github.com/Giglium/vinted_scraper/issues/59), because the HTML page
    is a plain document navigation and is not blocked the same way.

    Args:
        page_html: The raw HTML of an item page (e.g. ``/items/{id}``).

    Returns:
        The schema.org ``Product`` object as a dict, or, if no such block is
        present, ``{"description": ...}`` built from the ``og:description`` meta
        tag. Returns ``None`` when no description can be found at all.
    """
    for block in _LD_JSON_RE.findall(page_html):
        try:
            data = json.loads(block.strip())
        except (ValueError, TypeError):
            continue
        for obj in _iter_ld_json_objects(data):
            obj_type = obj.get("@type")
            is_product = obj_type == "Product" or (
                isinstance(obj_type, list) and "Product" in obj_type
            )
            if is_product:
                return obj

    match = _OG_DESCRIPTION_RE.search(page_html)
    if match and match.group(1).strip():
        return {"description": _html.unescape(match.group(1)).strip()}

    return None
