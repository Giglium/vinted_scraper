from dataclasses import dataclass
from typing import Optional


@dataclass
class VintedBrand:
    id: Optional[str] = None
    title: Optional[str] = None
    slug: Optional[str] = None
    favourite_count: Optional[int] = None
    pretty_favourite_count: Optional[str] = None
    item_count: Optional[int] = None
    pretty_item_count: Optional[str] = None
    is_visible_in_listings: Optional[bool] = None
    requires_authenticity_check: Optional[bool] = None
    is_luxury: Optional[bool] = None
    path: Optional[str] = None
    url: Optional[str] = None
    is_favourite: Optional[bool] = None

    def __init__(self, json_data=None):
        if json_data is not None:
            self.__dict__.update(json_data)
