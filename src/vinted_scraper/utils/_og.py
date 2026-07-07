"""OpenGraph meta tag extraction from HTML."""

import html as _html
import re
from typing import Any, Dict, List, Optional

from ..models import OgField

__all__ = [
    "parse_item_page",
]


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
