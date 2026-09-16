"""URL validation and HTTP header generation."""

import re
from typing import Dict

from ._constants import API_HOST_PREFIX, WWW_HOST_PREFIX

__all__ = [
    "url_validator",
    "site_base_url",
    "api_base_url",
    "locale_from_base_url",
    "format_cookie_header",
    "get_cookie_headers",
    "get_curl_headers",
]

_URL_PATTERN = re.compile(r"^https://(www\.)?[\w.-]+\.\w{2,}$")

# Fallback ``Locale`` values keyed by top-level domain, used only when the
# locale could not be read from the landing page's ``<html lang>`` tag (see
# ``utils/_html.py::extract_locale_from_html``).
_DEFAULT_LOCALE = "en-US"
_LOCALE_FALLBACK: Dict[str, str] = {
    "com": "en-US",
    "co.uk": "en-GB",
    "at": "de-AT",
    "be": "fr-BE",
    "cz": "cs-CZ",
    "de": "de-DE",
    "dk": "da-DK",
    "ee": "et-EE",
    "es": "es-ES",
    "fi": "fi-FI",
    "fr": "fr-FR",
    "gr": "el-GR",
    "hr": "hr-HR",
    "hu": "hu-HU",
    "ie": "en-IE",
    "it": "it-IT",
    "lt": "lt-LT",
    "lu": "fr-LU",
    "nl": "nl-NL",
    "pl": "pl-PL",
    "pt": "pt-PT",
    "ro": "ro-RO",
    "se": "sv-SE",
    "sk": "sk-SK",
    "si": "sl-SI",
}


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


def _strip_www(host: str) -> str:
    """Return ``host`` without a leading ``www.`` prefix."""
    if host.startswith(WWW_HOST_PREFIX):
        return host[len(WWW_HOST_PREFIX) :]
    return host


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
    host = _strip_www(host)
    return f"{scheme}{sep}{API_HOST_PREFIX}{host}"


def locale_from_base_url(base_url: str) -> str:
    """Best-effort ``Locale`` value guessed from a base URL's top-level domain.

    Args:
        base_url: The site base URL, with or without ``www.``.

    Returns:
        The guessed ``Locale`` header value (e.g. ``"it-IT"``, ``"en-US"``).
    """
    _, _, host = _split(base_url)
    labels = _strip_www(host).split(".")
    # Check the compound TLD (e.g. "co.uk") before the single-label TLD.
    compound = ".".join(labels[-2:])
    if compound in _LOCALE_FALLBACK:
        return _LOCALE_FALLBACK[compound]
    return _LOCALE_FALLBACK.get(labels[-1], _DEFAULT_LOCALE)


def format_cookie_header(cookies: Dict[str, str]) -> str:
    """Serialize a cookie mapping into a ``Cookie`` header value.

    Args:
        cookies: Cookies keyed by name.

    Returns:
        The ``"k=v; k=v"`` header string (empty when there are no cookies).
    """
    return "; ".join(f"{k}={v}" for k, v in cookies.items())


def get_cookie_headers(base_url: str, user_agent: str, locale: str) -> Dict:
    """Generates browser-like HTTP headers for cookie fetching.

    Args:
        base_url: Base URL of the website.
        user_agent: User agent string.
        locale: The ``Locale`` tag driving ``Accept-Language`` (e.g.
            ``"it-IT"``).

    Returns:
        Dictionary of HTTP headers.
    """
    return {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": f"{locale},en;q=0.5",
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
    base_url: str,
    user_agent: str,
    locale: str,
    session=None,
) -> Dict:
    """Generates HTTP headers for Vinted JSON API requests.

    Args:
        base_url: Base URL of the website.
        user_agent: User agent string.
        locale: The ``Locale`` header value (e.g. ``"it-IT"``), which also
            drives ``Accept-Language``.
        session: A ``VintedSession`` supplying cookies, CSRF token and anonymous
            id, or ``None`` when no identity is available yet.

    Returns:
        Dictionary of HTTP headers including the Cookie header and, when
        available, the CSRF token and anonymous id.
    """
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": f"{locale},en;q=0.5",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Origin": base_url,
        "Referer": base_url,
        "Locale": locale,
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
