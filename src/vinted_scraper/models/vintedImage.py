from dataclasses import dataclass
from typing import List, Optional

from .vintedHighResolution import VintedHighResolution
from .vintedMedia import VintedMedia


@dataclass
class VintedImage:
    id: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    temp_uuid: Optional[str] = None
    url: Optional[str] = None
    dominant_color: Optional[str] = None
    dominant_color_opaque: Optional[str] = None
    thumbnails: Optional[List[VintedMedia]] = None
    is_suspicious: Optional[bool] = None
    orientation: Optional[str] = None
    high_resolution: Optional[VintedHighResolution] = None
    full_size_url: Optional[str] = None
    is_hidden: Optional[bool] = None

    def __init__(self, json_data=None):
        if json_data is not None:
            self.__dict__.update(json_data)

            high_resolution_data = json_data.get("high_resolution")
            if high_resolution_data:
                self.high_resolution = VintedHighResolution(high_resolution_data)

            thumbnails_data = json_data.get("thumbnails")

            if thumbnails_data:
                self.thumbnails = [VintedMedia(thumbnails_data[0])]
