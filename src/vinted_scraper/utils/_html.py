"""HTML parsing helpers (OpenGraph meta tags and the CSRF token)."""

import html as _html
import re
from typing import Any, Dict, List, Optional

from ..models import OgField
from ._constants import CSRF_MARKER

__all__ = [
    "parse_item_page",
    "extract_csrf_token",
    "ChunkAccumulator",
]

# The API requires a CSRF token that Vinted embeds in the landing page HTML
# next to a ``CSRF_TOKEN`` marker, e.g. ``"CSRF_TOKEN":"<uuid>"``.
_CSRF_RE = re.compile(
    re.escape(CSRF_MARKER) + r'"\s*:\s*"'
    r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r'[0-9a-fA-F]{4}-[0-9a-fA-F]{12})"'
)


class ChunkAccumulator:
    """Collects streamed text chunks until a stop marker appears.

    Encapsulates the boundary bookkeeping shared by the sync and async
    streaming loops: chunks are accumulated and the marker is matched
    case-insensitively even when it spans two consecutive chunks, so callers
    can stop reading as soon as the marker is seen and never download the rest
    of the body.

    Args:
        stop_marker: The (lower-cased internally) marker that ends the read.
    """

    def __init__(self, stop_marker: str) -> None:
        self._stop_marker = stop_marker.lower()
        # Overlap kept between chunks so a marker split across a boundary is
        # still detected.
        self._tail_size = max(len(self._stop_marker) - 1, 0)
        self._parts: List[str] = []
        self._tail = ""

    def add(self, chunk: str) -> bool:
        """Append a chunk and report whether the stop marker has been seen.

        Args:
            chunk: The next text chunk read from the stream.

        Returns:
            ``True`` if the stop marker is now present (caller should stop).
        """
        self._parts.append(chunk)
        combined = self._tail + chunk.lower()
        if self._stop_marker in combined:
            return True
        self._tail = combined[-self._tail_size :] if self._tail_size else ""
        return False

    @property
    def text(self) -> str:
        """The concatenation of every chunk added so far."""
        return "".join(self._parts)


def extract_csrf_token(html: str) -> Optional[str]:
    """Extract the CSRF token from a page's HTML.

    Runs a single regex over the streamed HTML fragment, so the caller only
    needs to read up to the ``CSRF_TOKEN`` marker rather than the whole page.

    Args:
        html: The HTML content (the fragment up to the marker is sufficient).

    Returns:
        The CSRF token (a UUID), or ``None`` if not present.
    """
    match = _CSRF_RE.search(html)
    return match.group(1) if match else None


def _build_og_re(tag: str) -> List[re.Pattern]:
    """Build compiled regexes for an OpenGraph meta tag.

    Returns two patterns to handle both attribute orders:
    1. ``property/name`` before ``content``
    2. ``content`` before ``property/name``

    Args:
        tag: The OG tag name (e.g., ``"og:description"``).

    Returns:
        List of compiled regexes, each with one capture group for the
        content value.
    """
    escaped = re.escape(tag)
    return [
        # property/name first, content second
        re.compile(
            rf'<meta[^>]+(?:property|name)="{escaped}"[^>]+content="([^"]*)"',
            re.IGNORECASE,
        ),
        # content first, property/name second
        re.compile(
            rf'<meta[^>]+content="([^"]*)"[^>]+(?:property|name)="{escaped}"',
            re.IGNORECASE,
        ),
    ]


_OG_RE: Dict[str, List[re.Pattern]] = {
    OgField.DESCRIPTION: _build_og_re("og:description"),
    OgField.URL: _build_og_re("og:url"),
    OgField.IMAGE: _build_og_re("og:image"),
}


def _extract_og(html: str, field: str) -> Optional[str]:
    """Extract and unescape an OG tag value from HTML.

    Tries multiple regex patterns to handle different attribute orders.

    Args:
        html: HTML content to search.
        field: The ``OgField`` value to look for.

    Returns:
        The unescaped content string, or ``None`` if not found/empty.
    """
    patterns = _OG_RE.get(field)
    if patterns is None:
        return None
    for pattern in patterns:
        match = pattern.search(html)
        if match and match.group(1).strip():
            return _html.unescape(match.group(1)).strip()
    return None


def parse_item_page(
    item_id: str, html: str, fields: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Extract item metadata from OpenGraph meta tags in an item page.

    Always returns a dict containing ``id``. Additional fields are populated
    from the page's OG tags based on the ``fields`` parameter.

    ``title`` is derived from the first segment of ``og:description`` before
    the ``" - "`` separator.

    Args:
        item_id: The item identifier.
        html: The HTML content (head section is sufficient).
        fields: ``OgField`` values to extract. Defaults to all fields.

    Returns:
        A dict with ``id`` and any requested fields that were found.
    """
    if fields is None:
        fields = list(OgField)

    result: Dict[str, Any] = {"id": item_id}

    description = _extract_og(html, OgField.DESCRIPTION)
    if description is None:
        return result

    if " - " in description:
        title_part, description_part = description.split(" - ", 1)
        if OgField.TITLE in fields:
            result[OgField.TITLE] = title_part.strip()
        if OgField.DESCRIPTION in fields:
            result[OgField.DESCRIPTION] = description_part.strip()
    else:
        if OgField.DESCRIPTION in fields:
            result[OgField.DESCRIPTION] = description

    if OgField.URL in fields:
        url = _extract_og(html, OgField.URL)
        if url:
            result[OgField.URL] = url

    if OgField.IMAGE in fields:
        image = _extract_og(html, OgField.IMAGE)
        if image:
            result[OgField.IMAGE] = image

    return result
