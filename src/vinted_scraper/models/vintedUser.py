from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .vintedBundleDiscount import VintedBundleDiscount
from .vintedImage import VintedImage
from .vintedPaymentMethod import VintedPaymentMethod


@dataclass
class VintedUser:
    id: Optional[str] = None
    login: Optional[str] = None
    business: Optional[bool] = None
    profile_url: Optional[str] = None
    photo: Optional[VintedImage] = None
    anon_id: Optional[str] = None
    real_name: Optional[str] = None
    email: Optional[str] = None
    birthday: Optional[str] = None
    gender: Optional[str] = None
    item_count: Optional[int] = None
    msg_template_count: Optional[int] = None
    given_item_count: Optional[int] = None
    taken_item_count: Optional[int] = None
    favourite_topic_count: Optional[int] = None
    forum_msg_count: Optional[int] = None
    forum_topic_count: Optional[int] = None
    followers_count: Optional[int] = None
    following_count: Optional[int] = None
    following_brands_count: Optional[int] = None
    positive_feedback_count: Optional[int] = None
    neutral_feedback_count: Optional[int] = None
    negative_feedback_count: Optional[int] = None
    meeting_transaction_count: Optional[int] = None
    account_status: Optional[int] = None
    email_bounces: Optional[str] = None
    feedback_reputation: Optional[float] = None
    feedback_count: Optional[int] = None
    account_ban_date: Optional[str] = None
    is_account_ban_permanent: Optional[bool] = None
    is_forum_ban_permanent: Optional[bool] = None
    is_on_holiday: Optional[bool] = None
    is_publish_photos_agreed: Optional[bool] = None
    expose_location: Optional[bool] = None
    third_party_tracking: Optional[bool] = None
    default_address: Optional[str] = None
    last_loged_on_ts: Optional[str] = None
    city_id: Optional[str] = None
    city: Optional[str] = None
    country_id: Optional[int] = None
    country_code: Optional[str] = None
    country_iso_code: Optional[str] = None
    country_title: Optional[str] = None
    contacts_permission: Optional[str] = None
    contacts: Optional[str] = None
    path: Optional[str] = None
    moderator: Optional[bool] = None
    is_catalog_moderator: Optional[bool] = None
    is_catalog_role_marketing_photos: Optional[bool] = None
    hide_feedback: Optional[bool] = None
    can_post_big_forum_photos: Optional[bool] = None
    allow_direct_messaging: Optional[bool] = None
    bundle_discount: Optional[VintedBundleDiscount] = None
    donation_configuration: Optional[str] = None
    fundraiser: Optional[str] = None
    has_ship_fast_badge: Optional[bool] = None
    total_items_count: Optional[int] = None
    about: Optional[str] = None
    verification: Optional[Dict[str, Any]] = None
    closet_promoted_until: Optional[str] = None
    avg_response_time: Optional[str] = None
    carrier_ids: Optional[List[int]] = None
    carriers_without_custom_ids: Optional[List[int]] = None
    locale: Optional[str] = None
    updated_on: Optional[int] = None
    is_hated: Optional[bool] = None
    hates_you: Optional[bool] = None
    is_favourite: Optional[bool] = None
    share_profile_url: Optional[str] = None
    facebook_user_id: Optional[str] = None
    is_online: Optional[bool] = None
    has_promoted_closet: Optional[bool] = None
    can_view_profile: Optional[bool] = None
    can_bundle: Optional[bool] = None
    country_title_local: Optional[str] = None
    last_loged_on: Optional[str] = None
    accepted_pay_in_methods: Optional[List[VintedPaymentMethod]] = None
    localization: Optional[str] = None
    is_bpf_price_prominence_applied: Optional[bool] = None

    def __init__(self, json_data=None):
        if json_data is not None:
            self.__dict__.update(json_data)

            if "photo" in json_data:
                self.photo = VintedImage(json_data.get("photo"))

            if "bundle_discount" in json_data:
                self.bundle_discount = VintedBundleDiscount(
                    json_data.get("bundle_discount")
                )

            if "accepted_pay_in_methods" in json_data:
                self.bundle_discount = [
                    VintedPaymentMethod(method)
                    for method in json_data.get("accepted_pay_in_methods")
                ]
