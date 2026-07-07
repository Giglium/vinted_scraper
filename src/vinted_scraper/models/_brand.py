"""Vinted brand model."""

from dataclasses import dataclass
from typing import Optional

from ._json_model import VintedJsonModel


@dataclass
class VintedBrand(VintedJsonModel):
    """Represents a brand on Vinted.

    Search responses only provide the brand name (``brand_title``), so only
    ``title`` is exposed.

    Note:
        Some attributes may be `None` if not present in the API response.
    """

    title: Optional[str] = None
