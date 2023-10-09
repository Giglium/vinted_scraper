from dataclasses import dataclass
from typing import Optional

from .vintedImage import VintedImage


@dataclass
class VintedUser:
    id: Optional[str] = None
    login: Optional[str] = None
    business: Optional[bool] = None
    profile_url: Optional[str] = None
    photo: Optional[VintedImage] = None

    def __init__(self, json_data=None):
        if json_data is not None:
            self.__dict__.update(json_data)
            if "photo" in json_data:
                self.photo = VintedImage(json_data["photo"])
