"""Vinted high resolution image model."""

from dataclasses import dataclass
from typing import Optional

from ._json_model import VintedJsonModel


@dataclass
class VintedHighResolution(VintedJsonModel):
    """Represents high resolution image metadata.

    Note:
        Some attributes may be `None` if not present in the API response.
    """

    id: Optional[str] = None
    timestamp: Optional[int] = None
    orientation: Optional[str] = None
