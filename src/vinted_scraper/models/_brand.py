"""Vinted brand model."""

from dataclasses import dataclass
from typing import Optional

from ._json_model import VintedJsonModel


@dataclass
class VintedBrand(VintedJsonModel):
    """Represents a brand on Vinted.

    Note:
        Some attributes may be `None` if not present in the API response.
    """

    id: Optional[int] = None
    title: Optional[str] = None
    slug: Optional[str] = None
    path: Optional[str] = None
    is_favourite: Optional[bool] = None
