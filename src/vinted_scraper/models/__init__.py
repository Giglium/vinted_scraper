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
    VintedBundleDiscount: Bundle discount settings.
    VintedDiscount: Individual discount tier.
"""

from ._brand import VintedBrand
from ._bundle_discount import VintedBundleDiscount
from ._discount import VintedDiscount
from ._high_resolution import VintedHighResolution
from ._image import VintedImage
from ._item import VintedItem
from ._json_model import VintedJsonModel
from ._media import VintedMedia
from ._user import VintedUser

__all__ = [
    "VintedJsonModel",
    "VintedBrand",
    "VintedBundleDiscount",
    "VintedDiscount",
    "VintedHighResolution",
    "VintedImage",
    "VintedItem",
    "VintedMedia",
    "VintedUser",
]
