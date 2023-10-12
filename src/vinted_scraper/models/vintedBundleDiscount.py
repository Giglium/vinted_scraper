from dataclasses import dataclass
from typing import List, Optional


@dataclass
class VintedDiscount:
    minimal_item_count: Optional[int] = None
    fraction: Optional[float] = None

    def __init__(self, json_data=None):
        if json_data is not None:
            self.__dict__.update(json_data)


@dataclass
class VintedBundleDiscount:
    id: Optional[str] = None
    user_id: Optional[str] = None
    enabled: Optional[bool] = None
    minimal_item_count: Optional[int] = None
    fraction: Optional[float] = None
    discounts: Optional[List[VintedDiscount]] = None

    def __init__(self, json_data=None):
        if json_data is not None:
            self.__dict__.update(json_data)

            if "discounts" in json_data:
                self.discounts = [
                    VintedDiscount(discount) for discount in json_data.get("discounts")
                ]
