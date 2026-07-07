"""Vinted models package.

This package contains all data model classes for Vinted API responses.

Classes:
    VintedJsonModel: Base class for all models.
    VintedItem: Item/listing information.
    VintedUser: User/seller information.
    VintedBrand: Brand information.
    VintedImage: Image data and URLs.
    VintedMedia: Media thumbnails.
    VintedHighResolution: High-res image metadata.
"""

from ._brand import VintedBrand
from ._high_resolution import VintedHighResolution
from ._image import VintedImage
from ._item import VintedItem
from ._json_model import VintedJsonModel
from ._media import VintedMedia
from ._og_field import OgField
from ._user import VintedUser

__all__ = [
    "OgField",
    "VintedJsonModel",
    "VintedBrand",
    "VintedHighResolution",
    "VintedImage",
    "VintedItem",
    "VintedMedia",
    "VintedUser",
]
