# pylint: disable=too-many-instance-attributes
"""Vinted item model."""

from dataclasses import dataclass
from typing import List, Optional, Tuple

from ._brand import VintedBrand
from ._image import VintedImage
from ._json_model import VintedJsonModel
from ._user import VintedUser


def _parse_price(value) -> Optional[float]:
    """Parse a price value from the API response.

    Args:
        value: Price as a dict (with "amount" key), a numeric type, a string,
            or None.

    Returns:
        Parsed float price, or None if the value is not a recognised format
        or cannot be converted to a number.
    """
    try:
        if isinstance(value, dict):
            return float(value["amount"])
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            return float(value)
    except (ValueError, KeyError):
        return None
    return None


def _parse_price_with_currency(
    value,
) -> Tuple[Optional[float], Optional[str]]:
    """Parse a price value and optional currency from the API response.

    Handles the dict format ``{"amount": "9.99", "currency_code": "EUR"}``
    as well as plain numeric/string values (currency will be ``None``).

    Args:
        value: Price as a dict (with "amount" and optionally "currency_code"
            keys), a numeric type, a string, or None.

    Returns:
        Tuple of (price, currency). Either or both may be ``None`` if the
        value cannot be parsed or the currency is not present.
    """
    try:
        if isinstance(value, dict):
            price = float(value["amount"])
            currency = value.get("currency_code")
            return price, currency
        if isinstance(value, (int, float)):
            return float(value), None
        if isinstance(value, str):
            return float(value), None
    except (ValueError, KeyError):
        return None, None
    return None, None


@dataclass
class VintedItem(VintedJsonModel):
    """Represents a Vinted marketplace item with all its attributes.

    Only the fields that can be populated from a search response
    (:meth:`VintedScraper.search`) or the public item page
    (:meth:`VintedScraper.item`) are exposed. The item metadata read from the
    page is limited to ``title``, ``description``, ``url`` and ``image``.

    Note:
        Some attributes may be `None` if not present in the API response.
    """

    id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    currency: Optional[str] = None
    photos: Optional[List[VintedImage]] = None
    price: Optional[float] = None
    conversion: Optional[str] = None
    favourite_count: Optional[int] = None
    is_favourite: Optional[bool] = None
    view_count: Optional[int] = None
    user: Optional[VintedUser] = None
    promoted: Optional[bool] = None
    brand: Optional[VintedBrand] = None
    path: Optional[str] = None
    url: Optional[str] = None
    image: Optional[str] = None
    status: Optional[str] = None
    service_fee: Optional[float] = None
    total_item_price: Optional[float] = None
    is_visible: Optional[bool] = None
    brand_title: Optional[str] = None
    size_title: Optional[str] = None
    content_source: Optional[str] = None
    item_box: Optional[dict] = None
    search_tracking_params: Optional[dict] = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.json_data is not None:
            if "user" in self.json_data and self.json_data["user"]:
                self.user = VintedUser(json_data=self.json_data["user"])

            if "photo" in self.json_data and self.json_data["photo"]:
                self.photos = [VintedImage(json_data=self.json_data["photo"])]
            if "photos" in self.json_data and self.json_data["photos"]:
                self.photos = [
                    VintedImage(json_data=i) for i in self.json_data["photos"]
                ]

            if "brand_title" in self.json_data and self.json_data["brand_title"]:
                self.brand = VintedBrand()
                self.brand.title = self.json_data["brand_title"]

            self.price, currency = _parse_price_with_currency(
                self.json_data.get("price")
            )
            if currency is not None:
                self.currency = currency

            self.service_fee = _parse_price(self.json_data.get("service_fee"))
            self.total_item_price = _parse_price(self.json_data.get("total_item_price"))
