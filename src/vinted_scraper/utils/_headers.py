"""URL validation and HTTP header generation."""

import re
from typing import Dict

from ._constants import API_HOST_PREFIX, WWW_HOST_PREFIX

__all__ = [
    "url_validator",
    "site_base_url",
    "api_base_url",
    "format_cookie_header",
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


def _split(base_url: str):
    """Split a base URL into ``(scheme, sep, host)`` via ``rpartition``."""
    return base_url.rpartition("://")


def site_base_url(base_url: str) -> str:
    """Return the site base URL on the ``www.`` host.

    Accepts a base URL with or without the ``www.`` prefix and always returns
    the ``www.`` form (e.g. both ``https://vinted.com`` and
    ``https://www.vinted.com`` -> ``https://www.vinted.com``).

    Args:
        base_url: The site base URL, with or without ``www.``.

    Returns:
        The base URL on the ``www.`` host.
    """
    scheme, sep, host = _split(base_url)
    if not host.startswith(WWW_HOST_PREFIX):
        host = WWW_HOST_PREFIX + host
    return f"{scheme}{sep}{host}"


def api_base_url(base_url: str) -> str:
    """Return the API base URL on the ``api.`` host.

    The API (which serves the ``svc-catalogue`` service) is hosted on the
    ``api.`` sibling of the site host. The base URL is accepted with or without
    the ``www.`` prefix and the host is rewritten to ``api.`` (e.g. both
    ``https://vinted.com`` and ``https://www.vinted.com`` ->
    ``https://api.vinted.com``).

    Args:
        base_url: The site base URL, with or without ``www.``.

    Returns:
        The API base URL (e.g. ``https://api.vinted.com``).
    """
    scheme, sep, host = _split(base_url)
    if host.startswith(WWW_HOST_PREFIX):
        host = host[len(WWW_HOST_PREFIX) :]
    return f"{scheme}{sep}{API_HOST_PREFIX}{host}"


def format_cookie_header(cookies: Dict[str, str]) -> str:
    """Serialize a cookie mapping into a ``Cookie`` header value.

    Args:
        cookies: Cookies keyed by name.

    Returns:
        The ``"k=v; k=v"`` header string (empty when there are no cookies).
    """
    return "; ".join(f"{k}={v}" for k, v in cookies.items())


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


def get_curl_headers(base_url: str, user_agent: str, session=None) -> Dict:
    """Generates HTTP headers for Vinted JSON API requests.

    Args:
        base_url: Base URL of the website.
        user_agent: User agent string.
        session: A ``VintedSession`` supplying cookies, CSRF token and anonymous
            id, or ``None`` when no identity is available yet.

    Returns:
        Dictionary of HTTP headers including the Cookie header and, when
        available, the CSRF token and anonymous id.
    """
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Origin": base_url,
        "Referer": base_url,
        "Locale": "en-US",
        "Platform": "web",
        "X-Next-App": "marketplace-web",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }
    if session is None:
        return headers
    if session.cookies:
        headers["Cookie"] = format_cookie_header(session.cookies)
    if session.csrf_token:
        headers["X-Csrf-Token"] = session.csrf_token
    if session.anon_id:
        headers["X-Anon-Id"] = session.anon_id
    return headers
