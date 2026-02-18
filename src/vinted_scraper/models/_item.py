# pylint: disable=too-many-instance-attributes
"""Vinted item model."""

from dataclasses import dataclass
from typing import List, Optional

from ._brand import VintedBrand
from ._image import VintedImage
from ._json_model import VintedJsonModel
from ._user import VintedUser


@dataclass
class VintedItem(VintedJsonModel):
    """Represents a Vinted marketplace item with all its attributes.

    Note:
        Some attributes may be `None` if not present in the API response.
    """

    id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status_id: Optional[int] = None
    disposal_conditions: Optional[int] = None
    catalog_id: Optional[int] = None
    is_hidden: Optional[bool] = None
    is_reserved: Optional[bool] = None
    is_closed: Optional[bool] = None
    is_draft: Optional[bool] = None
    is_processing: Optional[bool] = None
    item_closing_action: Optional[str] = None
    currency: Optional[str] = None
    photos: Optional[List[VintedImage]] = None
    price: Optional[float] = None
    transaction_permitted: Optional[bool] = None
    reservation: Optional[str] = None
    offline_verification: Optional[bool] = None
    offer_price: Optional[float] = None
    conversion: Optional[str] = None
    is_cross_currency_payment: Optional[bool] = None
    favourite_count: Optional[int] = None
    is_favourite: Optional[bool] = None
    view_count: Optional[int] = None
    user: Optional[VintedUser] = None
    can_edit: Optional[bool] = None
    can_delete: Optional[bool] = None
    can_reserve: Optional[bool] = None
    instant_buy: Optional[bool] = None
    can_buy: Optional[bool] = None
    can_bundle: Optional[bool] = None
    promoted: Optional[bool] = None
    brand: Optional[VintedBrand] = None
    path: Optional[str] = None
    url: Optional[str] = None
    color1: Optional[str] = None
    status: Optional[str] = None
    localization: Optional[str] = None
    item_alert: Optional[str] = None
    service_fee: Optional[float] = None
    offline_verification_fee: Optional[float] = None
    total_item_price: Optional[float] = None
    can_push_up: Optional[bool] = None
    stats_visible: Optional[bool] = None
    is_visible: Optional[bool] = None
    brand_title: Optional[str] = None
    size_title: Optional[str] = None
    content_source: Optional[str] = None
    badge: Optional[str] = None
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

            if "brand_dto" in self.json_data and self.json_data["brand_dto"]:
                self.brand = VintedBrand(json_data=self.json_data["brand_dto"])
            elif "brand_title" in self.json_data and self.json_data["brand_title"]:
                self.brand = VintedBrand()
                self.brand.title = self.json_data["brand_title"]

            if isinstance(self.json_data.get("price"), dict):
                self.price = float(self.json_data["price"]["amount"])
                self.currency = self.json_data["price"]["currency_code"]
            elif isinstance(self.json_data.get("price"), str):
                self.price = float(self.json_data["price"])

            if isinstance(self.json_data.get("service_fee"), dict):
                self.service_fee = float(self.json_data["service_fee"]["amount"])
            elif isinstance(self.json_data.get("service_fee"), str):
                self.service_fee = float(self.json_data["service_fee"])

            if isinstance(self.json_data.get("total_item_price"), dict):
                self.total_item_price = float(
                    self.json_data["total_item_price"]["amount"]
                )
            elif isinstance(self.json_data.get("total_item_price"), str):
                self.total_item_price = float(self.json_data["total_item_price"])
