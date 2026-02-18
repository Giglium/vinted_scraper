# pylint: disable=missing-module-docstring,missing-class-docstring
from dataclasses import dataclass
from typing import List, Optional

from ._json_model import VintedJsonModel


@dataclass
class VintedDiscount(VintedJsonModel):
    minimal_item_count: Optional[int] = None
    fraction: Optional[float] = None

    def __post_init__(self) -> None:
        if self.json_data is not None:
            self.minimal_item_count = int(self.json_data.get("minimal_item_count", 0))
            self.fraction = float(self.json_data.get("fraction", 0.0))


@dataclass
class VintedBundleDiscount(VintedJsonModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    enabled: Optional[bool] = None
    minimal_item_count: Optional[int] = None
    fraction: Optional[float] = None
    discounts: Optional[List[VintedDiscount]] = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.json_data is not None:
            if "discounts" in self.json_data:
                self.discounts = [
                    VintedDiscount(json_data=discount)
                    for discount in self.json_data.get("discounts")
                ]
