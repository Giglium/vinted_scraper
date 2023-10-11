from dataclasses import dataclass
from typing import List, Optional

from .vintedBrand import VintedBrand
from .vintedImage import VintedImage
from .vintedPaymentMethod import VintedPaymentMethod
from .vintedUser import VintedUser


@dataclass
class VintedItem:
    id: Optional[str] = None
    title: Optional[str] = None
    price: Optional[float] = None
    is_visible: Optional[int] = None
    discount: Optional[str] = None
    currency: Optional[str] = None
    brand: Optional[VintedBrand] = None
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
    accepted_pay_in_methods: Optional[List[VintedPaymentMethod]] = None
    user_id: Optional[str] = None
    description: Optional[str] = None
    brand_id: Optional[int] = None
    size_id: Optional[str] = None
    status_id: Optional[int] = None
    disposal_conditions: Optional[int] = None
    owner_id: Optional[str] = None
    country_id: Optional[int] = None
    catalog_id: Optional[int] = None
    color1_id: Optional[str] = None
    color2_id: Optional[str] = None
    package_size_id: Optional[int] = None
    is_hidden: Optional[int] = None
    is_reserved: Optional[int] = None
    reserved_for_user_id: Optional[str] = None
    is_unisex: Optional[int] = None
    is_closed: Optional[int] = None
    active_bid_count: Optional[int] = None
    moderation_status: Optional[int] = None
    last_push_up_at: Optional[str] = None
    package_size_standard: Optional[bool] = None
    item_closing_action: Optional[str] = None
    related_catalog_ids: Optional[List[int]] = None
    related_catalogs_enabled: Optional[bool] = None
    size: Optional[str] = None
    composition: Optional[str] = None
    extra_conditions: Optional[str] = None
    is_for_sell: Optional[bool] = None
    is_for_give_away: Optional[bool] = None
    is_handicraft: Optional[bool] = None
    is_processing: Optional[bool] = None
    is_draft: Optional[bool] = None
    label: Optional[str] = None
    real_value_numeric: Optional[float] = None
    original_price_numeric: Optional[float] = None
    created_at_ts: Optional[str] = None
    updated_at_ts: Optional[str] = None
    user_updated_at_ts: Optional[str] = None
    push_up_interval: Optional[int] = None
    can_be_sold: Optional[bool] = None
    can_feedback: Optional[bool] = None
    item_reservation_id: Optional[str] = None
    receiver_id: Optional[str] = None
    promoted_until: Optional[str] = None
    vas_gallery_promoted_until: Optional[str] = None
    vas_gallery_promoted_created_at: Optional[str] = None
    discount_price_numeric: Optional[float] = None
    author: Optional[str] = None
    book_title: Optional[str] = None
    isbn: Optional[str] = None
    measurement_width: Optional[str] = None
    measurement_length: Optional[str] = None
    measurement_unit: Optional[str] = None
    transaction_permitted: Optional[bool] = None
    video_game_rating_id: Optional[str] = None
    item_attributes: Optional[List[str]] = None
    is_story_uploaded: Optional[bool] = None
    discount_price: Optional[float] = None
    can_edit: Optional[bool] = None
    can_delete: Optional[bool] = None
    can_reserve: Optional[bool] = None
    can_mark_as_sold: Optional[bool] = None
    can_transfer: Optional[bool] = None
    instant_buy: Optional[bool] = None
    can_close: Optional[bool] = None
    can_buy: Optional[bool] = None
    can_bundle: Optional[bool] = None
    can_ask_seller: Optional[bool] = None
    can_favourite: Optional[bool] = None
    user_login: Optional[str] = None
    city_id: Optional[int] = None
    city: Optional[str] = None
    country: Optional[str] = None
    is_mobile: Optional[bool] = None
    bump_badge_visible: Optional[bool] = None
    path: Optional[str] = None
    created_at: Optional[str] = None
    color1: Optional[str] = None
    color2: Optional[str] = None
    description_attributes: Optional[List[str]] = None
    video_game_rating: Optional[str] = None
    status: Optional[str] = None
    performance: Optional[str] = None
    stats_visible: Optional[bool] = None
    can_push_up: Optional[bool] = None
    can_vas_gallery_promote: Optional[bool] = None
    vas_gallery_promoted: Optional[bool] = None
    size_guide_faq_entry_id: Optional[str] = None
    localization: Optional[str] = None
    is_upload_story_button_visible: Optional[bool] = None
    offline_verification: Optional[bool] = None
    offline_verification_fee: Optional[float] = None

    def __init__(self, json_data=None):
        if json_data is not None:
            self.__dict__.update(json_data)

            if "user" in json_data:
                self.user = VintedUser(json_data.get("user"))

            if "photo" in json_data:
                self.photo = VintedImage(json_data.get("photo"))

            if "accepted_pay_in_methods" in json_data:
                self.accepted_pay_in_methods = [
                    VintedPaymentMethod(method)
                    for method in json_data.get("accepted_pay_in_methods")
                ]

            if "brand_dto" in json_data:
                self.brand = VintedBrand(json_data.get("brand_dto"))
            elif "brand_title" in json_data:
                self.brand = VintedBrand()
                self.brand.title = json_data.get("brand_title")

        if type(json_data.get("price")) is dict:
            self.price = float(json_data.get("price")["amount"])
            self.currency = json_data.get("price")["currency_code"]
        else:
            self.price = (
                float(self.price) if isinstance(self.price, str) else self.price
            )

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
