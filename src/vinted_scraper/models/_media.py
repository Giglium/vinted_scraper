"""Vinted media model."""

from dataclasses import dataclass
from typing import Optional

from ._json_model import VintedJsonModel


@dataclass
class VintedMedia(VintedJsonModel):
    """Represents a media thumbnail or variant.

    Note:
        Some attributes may be `None` if not present in the API response.
    """

    type: Optional[str] = None
    url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    original_size: Optional[str] = None
