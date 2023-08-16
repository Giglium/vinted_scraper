import json
from typing import List, Optional


class VintedUser:
    """
    A class that represent a User. Note if an attribute is null this means that it wasn't found the scrap.
    """

    def __init__(self, data):
        self.id: Optional[int] = data.get("id", None)
        self.login: Optional[str] = data.get("login", None)
        self.business: Optional[str] = data.get("business", None)
        self.profile_url: Optional[str] = data.get("profile_url", None)
        self.photo: Optional[VintedPhoto] = (
            VintedPhoto(data["photo"]) if data.get("photo") else None
        )
        self.item_count: Optional[int] = data.get("item_count", None)
        self.followers_count: Optional[int] = data.get("followers_count", None)
        self.following_count: Optional[int] = data.get("following_count", None)
        self.positive_feedback_count: Optional[int] = data.get(
            "positive_feedback_count", None
        )
        self.neutral_feedback_count: Optional[int] = data.get(
            "neutral_feedback_count", None
        )
        self.negative_feedback_count: Optional[int] = data.get(
            "negative_feedback_count", None
        )
        self.feedback_count: Optional[int] = data.get("feedback_count", None)
        self.feedback_reputation: Optional[float] = data.get(
            "feedback_reputation", None
        )
        self.city: Optional[str] = data.get("city", None)
        self.last_logged_on_ts: Optional[int] = data.get("last_logged_on_ts", None)
        self.locale: Optional[str] = data.get("locale", None)

    def __str__(self):  # pragma: no cover
        return json.dumps(self, default=lambda o: o.__dict__, indent=1)

    def __eq__(self, other):  # pragma: no cover
        if not isinstance(other, VintedUser):
            return False
        return self.__dict__ == other.__dict__


class VintedPhoto:
    """
    A class that represent a web image. Note if an attribute is null this means that it wasn't found the scrap.
    """

    def __init__(self, data):
        self.id: Optional[int] = data.get("id", None)
        self.url: Optional[str] = data.get("url", None)
        self.image_no: Optional[int] = data.get("image_no", None)
        self.dominant_color: Optional[str] = data.get("dominant_color", None)
        self.dominant_color_opaque: Optional[str] = data.get(
            "dominant_color_opaque", None
        )
        self.is_main: Optional[bool] = data.get("is_main", None)
        self.is_suspicious: Optional[bool] = data.get("is_suspicious", None)
        self.full_size_url: Optional[str] = data.get("full_size_url", None)

    def __str__(self):  # pragma: no cover
        return json.dumps(self, default=lambda o: o.__dict__)

    def __eq__(self, other):  # pragma: no cover
        if not isinstance(other, VintedPhoto):
            return False
        return self.__dict__ == other.__dict__


class VintedBrand:
    """
    A class that represent a brand. Note if an attribute is null this means that it wasn't found the scrap.
    """

    def __init__(self, data):
        self.title: Optional[str] = data.get("title", None)
        self.slug: Optional[str] = data.get("slug", None)
        self.path: Optional[str] = data.get("path", None)

    def __str__(self):  # pragma: no cover
        return json.dumps(self, default=lambda o: o.__dict__)

    def __eq__(self, other):  # pragma: no cover
        if not isinstance(other, VintedBrand):
            return False
        return self.__dict__ == other.__dict__


class VintedItem:
    """
    A class that represent an Item. Note if an attribute is null this means that it wasn't found the scrap.
    """

    def __init__(self, data):
        self.id: Optional[int] = data.get("id", None)
        self.title: Optional[str] = data.get("title", None)
        self.description: Optional[str] = data.get("description", None)
        self.is_reserved: Optional[bool] = data.get("is_reserved", None)
        self.is_closed: Optional[bool] = data.get("is_closed", None)
        self.is_for_swap: Optional[bool] = data.get("is_for_swap", None)
        self.active_bid_count: Optional[int] = data.get("active_bid_count", None)
        self.item_closing_action: Optional[str] = data.get("item_closing_action", None)
        self.created_at_ts: Optional[int] = data.get("created_at_ts", None)
        self.photos: List[VintedPhoto] = [
            VintedPhoto(p) for p in data.get("photos", [])
        ]
        self.thumbnail: Optional[VintedPhoto] = (
            VintedPhoto(data["photo"]) if data.get("photo") else None
        )
        self.price: Optional[float] = (
            float(data["price"]["amount"]) if data.get("price") is not None else None
        )
        self.currency: Optional[str] = (
            data["price"]["currency_code"] if data.get("price") is not None else None
        )
        self.favourite_count: Optional[int] = data.get("favourite_count", None)
        self.is_favourite: Optional[bool] = data.get("is_favourite", None)
        self.view_count: Optional[int] = data.get("view_count", None)
        self.url: Optional[str] = data.get("url", None)
        self.status: Optional[str] = data.get("status", None)
        self.service_fee: Optional[float] = (
            float(data["service_fee"]["amount"])
            if data.get("service_fee") is not None
            else None
        )
        self.total_item_price: Optional[float] = (
            float(data["total_item_price"]["amount"])
            if data.get("total_item_price") is not None
            else None
        )
        self.user: Optional[VintedUser] = (
            VintedUser(data["user"]) if data.get("user") else None
        )
        self.brand_dto: Optional[VintedBrand] = (
            VintedBrand(data.get("brand_dto"))
            if data.get("brand_dto")
            else VintedBrand({"title": data.get("brand_title")})
            if data.get("brand_title")
            else None
        )
        self.color1: Optional[str] = data.get("color1", None)
        self.color2: Optional[str] = data.get("color2", None)
        self.description_attributes: List[str] = data.get("description_attributes", [])
        self.localization: Optional[str] = data.get("localization", None)

    def __str__(self):  # pragma: no cover
        return json.dumps(self, default=lambda o: o.__dict__, indent=2)

    def __eq__(self, other):  # pragma: no cover
        if not isinstance(other, VintedItem):
            return False
        return self.__dict__ == other.__dict__
