# pylint: disable=missing-module-docstring,missing-class-docstring,too-many-instance-attributes
from dataclasses import dataclass
from typing import List, Optional

from ._vinted_brand import VintedBrand
from ._vinted_image import VintedImage
from ._vinted_user import VintedUser


@dataclass
class VintedItem:
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

    def __init__(self, json_data=None):
        if json_data is not None:
            self.__dict__.update(json_data)

            if "user" in json_data and json_data["user"]:
                self.user = VintedUser(json_data["user"])

            # Handle both 'photo' and 'photos'
            if "photo" in json_data and json_data["photo"]:
                self.photos = [VintedImage(json_data["photo"])]
            if "photos" in json_data and json_data["photos"]:
                self.photos = [VintedImage(i) for i in json_data["photos"]]

            if "brand_dto" in json_data and json_data["brand_dto"]:
                self.brand = VintedBrand(json_data["brand_dto"])
            elif "brand_title" in json_data and json_data["brand_title"]:
                self.brand = VintedBrand()
                self.brand.title = json_data["brand_title"]

            if isinstance(json_data.get("price"), dict):
                self.price = float(json_data["price"]["amount"])
                self.currency = json_data["price"]["currency_code"]
            elif isinstance(json_data.get("price"), str):
                self.price = float(json_data["price"])

            if isinstance(json_data.get("service_fee"), dict):
                self.service_fee = float(json_data["service_fee"]["amount"])
            elif isinstance(json_data.get("service_fee"), str):
                self.service_fee = float(json_data["service_fee"])

            if isinstance(json_data.get("total_item_price"), dict):
                self.total_item_price = float(json_data["total_item_price"]["amount"])
            elif isinstance(json_data.get("total_item_price"), str):
                self.total_item_price = float(json_data["total_item_price"])
