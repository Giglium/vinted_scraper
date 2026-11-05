# pylint: disable=too-many-instance-attributes
"""Vinted user model."""

from dataclasses import dataclass
from typing import Optional

from ._image import VintedImage
from ._json_model import VintedJsonModel


@dataclass
class VintedUser(VintedJsonModel):
    """Represents a Vinted user/seller.

    The first fields come from a search response; the rest come from the full
    profile (:meth:`VintedScraper.get_user` / :meth:`VintedWrapper.get_raw_user`).

    Note:
        Some attributes may be `None` if not present in the API response.
    """

    id: Optional[int] = None
    anon_id: Optional[str] = None
    login: Optional[str] = None
    real_name: Optional[str] = None
    email: Optional[str] = None
    business: Optional[bool] = None
    business_account_id: Optional[int] = None
    business_account: Optional[dict] = None
    profile_url: Optional[str] = None
    share_profile_url: Optional[str] = None
    path: Optional[str] = None
    photo: Optional[VintedImage] = None
    about: Optional[str] = None
    birthday: Optional[str] = None
    country_id: Optional[int] = None
    country_code: Optional[str] = None
    country_iso_code: Optional[str] = None
    country_title: Optional[str] = None
    country_title_local: Optional[str] = None
    city: Optional[str] = None
    city_id: Optional[int] = None
    expose_location: Optional[bool] = None
    default_address: Optional[dict] = None
    locale: Optional[str] = None
    iso_locale_code: Optional[str] = None
    localization: Optional[str] = None
    currency: Optional[str] = None
    item_count: Optional[int] = None
    total_items_count: Optional[int] = None
    given_item_count: Optional[int] = None
    taken_item_count: Optional[int] = None
    followers_count: Optional[int] = None
    following_count: Optional[int] = None
    following_brands_count: Optional[int] = None
    is_favourite: Optional[bool] = None
    hates_you: Optional[bool] = None
    is_hated: Optional[bool] = None
    feedback_count: Optional[int] = None
    feedback_reputation: Optional[float] = None
    positive_feedback_count: Optional[int] = None
    neutral_feedback_count: Optional[int] = None
    negative_feedback_count: Optional[int] = None
    hide_feedback: Optional[bool] = None
    is_online: Optional[bool] = None
    last_loged_on: Optional[str] = None
    last_loged_on_ts: Optional[str] = None
    is_on_holiday: Optional[bool] = None
    account_status: Optional[int] = None
    is_deleted: Optional[bool] = None
    is_account_banned: Optional[bool] = None
    account_ban_date: Optional[str] = None
    action_restriction: Optional[str] = None
    can_view_profile: Optional[bool] = None
    moderator: Optional[bool] = None
    is_catalog_moderator: Optional[bool] = None
    allow_direct_messaging: Optional[bool] = None
    avg_response_time: Optional[int] = None
    msg_template_count: Optional[int] = None
    can_bundle: Optional[bool] = None
    bundle_discount: Optional[dict] = None
    fundraiser: Optional[dict] = None
    updated_on: Optional[int] = None
    verification: Optional[dict] = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.json_data is not None:
            if "photo" in self.json_data and self.json_data["photo"]:
                self.photo = VintedImage(json_data=self.json_data["photo"])
