# pylint: disable=too-many-instance-attributes
"""Vinted user model."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ._bundle_discount import VintedBundleDiscount
from ._image import VintedImage
from ._json_model import VintedJsonModel


@dataclass
class VintedUser(VintedJsonModel):
    """Represents a Vinted user/seller with profile and activity information.

    Note:
        Some attributes may be `None` if not present in the API response.
    """

    id: Optional[int] = None
    login: Optional[str] = None
    business: Optional[bool] = None
    profile_url: Optional[str] = None
    photo: Optional[VintedImage] = None
    item_count: Optional[int] = None
    feedback_count: Optional[int] = None
    feedback_reputation: Optional[float] = None
    moderator: Optional[bool] = None
    can_bundle: Optional[bool] = None
    bundle_discount: Optional[VintedBundleDiscount] = None
    country_id: Optional[int] = None
    country_title_local: Optional[str] = None
    last_loged_on_ts: Optional[str] = None
    last_logged_on_ts: Optional[str] = None
    is_on_holiday: Optional[bool] = None
    expose_location: Optional[bool] = None
    city: Optional[str] = None
    locale: Optional[str] = None
    followers_count: Optional[int] = None
    following_count: Optional[int] = None
    is_banned: Optional[bool] = None
    is_favourite: Optional[bool] = None
    seller_badges: Optional[List[Dict[str, Any]]] = None
    hates_you: Optional[bool] = None
    is_hated: Optional[bool] = None
    can_view_profile: Optional[bool] = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.json_data is not None:
            if "photo" in self.json_data and self.json_data["photo"]:
                self.photo = VintedImage(json_data=self.json_data["photo"])
            if (
                "bundle_discount" in self.json_data
                and self.json_data["bundle_discount"]
            ):
                self.bundle_discount = VintedBundleDiscount(
                    json_data=self.json_data["bundle_discount"]
                )
