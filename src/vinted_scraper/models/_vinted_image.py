# pylint: disable=missing-module-docstring,missing-class-docstring,too-many-instance-attributes
from dataclasses import dataclass
from typing import List, Optional

from ._vinted_high_resolution import VintedHighResolution
from ._vinted_media import VintedMedia


@dataclass
class VintedImage:
    id: Optional[int] = None
    image_no: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    temp_uuid: Optional[str] = None
    url: Optional[str] = None
    dominant_color: Optional[str] = None
    dominant_color_opaque: Optional[str] = None
    thumbnails: Optional[List[VintedMedia]] = None
    is_main: Optional[bool] = None
    is_suspicious: Optional[bool] = None
    orientation: Optional[str] = None
    high_resolution: Optional[VintedHighResolution] = None
    full_size_url: Optional[str] = None
    is_hidden: Optional[bool] = None
    extra: Optional[dict] = None

    def __init__(self, json_data=None):
        if json_data is not None:
            self.__dict__.update(json_data)
            if "high_resolution" in json_data and json_data["high_resolution"]:
                self.high_resolution = VintedHighResolution(
                    json_data["high_resolution"]
                )
            if "thumbnails" in json_data and json_data["thumbnails"]:
                self.thumbnails = [
                    VintedMedia(media) for media in json_data["thumbnails"]
                ]
