"""Vinted user model."""

from dataclasses import dataclass
from typing import Optional

from ._image import VintedImage
from ._json_model import VintedJsonModel


@dataclass
class VintedUser(VintedJsonModel):
    """Represents a Vinted user/seller.

    Only the fields present in a search response are exposed.

    Note:
        Some attributes may be `None` if not present in the API response.
    """

    id: Optional[int] = None
    login: Optional[str] = None
    business: Optional[bool] = None
    profile_url: Optional[str] = None
    photo: Optional[VintedImage] = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.json_data is not None:
            if "photo" in self.json_data and self.json_data["photo"]:
                self.photo = VintedImage(json_data=self.json_data["photo"])
