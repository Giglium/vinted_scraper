"""HTTP utilities for httpx client configuration and cookie handling."""

from typing import Dict, List, Optional

import httpx

from ._constants import DEFAULT_TIMEOUT


def get_httpx_config(baseurl: str, config: Optional[Dict] = None) -> Dict:
    """Returns configuration dictionary for httpx.Client.

    Provides default configuration (base_url, timeout, follow_redirects)
    and merges with custom config if provided.

    Args:
        baseurl: The base URL for the httpx client.
        config: Optional custom configuration to merge with defaults.

    Returns:
        Dictionary containing httpx client configuration.
    """
    default_config = {
        "base_url": baseurl,
        "timeout": httpx.Timeout(DEFAULT_TIMEOUT),
        "follow_redirects": True,
    }

    return {**default_config, **(config or {})}


def extract_cookie_from_response(
    response: httpx.Response, cookie_names: List[str]
) -> Dict[str, str]:
    """Extracts specified cookies from httpx response.

    Args:
        response: The httpx response object.
        cookie_names: List of cookie names to extract.

    Returns:
        Dictionary with cookie names as keys and values.
    """
    return {
        name: response.cookies.get(name)
        for name in cookie_names
        if response.cookies.get(name)
    }
