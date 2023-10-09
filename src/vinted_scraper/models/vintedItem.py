from dataclasses import dataclass
from typing import Optional

from .vintedImage import VintedImage
from .vintedUser import VintedUser


@dataclass
class VintedItem:
    id: Optional[str] = None
    title: Optional[str] = None
    price: Optional[float] = None
    is_visible: Optional[int] = None
    discount: Optional[str] = None
    currency: Optional[str] = None
    brand_title: Optional[str] = None
    is_for_swap: Optional[bool] = None
    user: Optional[VintedUser] = None
    url: Optional[str] = None
    promoted: Optional[bool] = None
    photo: Optional[VintedImage] = None
    favourite_count: Optional[int] = None
    is_favourite: Optional[bool] = None
    badge: Optional[str] = None
    conversion: Optional[str] = None
    service_fee: Optional[float] = None
    total_item_price: Optional[float] = None
    view_count: Optional[int] = None
    size_title: Optional[str] = None
    content_source: Optional[str] = None

    def __init__(self, json_data=None):
        if json_data is not None:
            self.__dict__.update(json_data)
            if "user" in json_data:
                self.user = VintedUser(json_data["user"])
            if "photo" in json_data:
                self.photo = VintedImage(json_data["photo"])

        self.price = float(self.price) if isinstance(self.price, str) else self.price
        self.service_fee = (
            float(self.service_fee)
            if isinstance(self.service_fee, str)
            else self.service_fee
        )
        self.total_item_price = (
            float(self.total_item_price)
            if isinstance(self.total_item_price, str)
            else self.total_item_price
        )
