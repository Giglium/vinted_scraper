# pylint: disable=too-many-instance-attributes
"""Vinted image model."""

from dataclasses import dataclass
from typing import List, Optional

from ._high_resolution import VintedHighResolution
from ._json_model import VintedJsonModel
from ._media import VintedMedia


@dataclass
class VintedImage(VintedJsonModel):
    """Represents an image associated with a Vinted item.

    Note:
        Some attributes may be `None` if not present in the API response.
    """

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

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.json_data is not None:
            if (
                "high_resolution" in self.json_data
                and self.json_data["high_resolution"]
            ):
                self.high_resolution = VintedHighResolution(
                    json_data=self.json_data["high_resolution"]
                )
            if "thumbnails" in self.json_data and self.json_data["thumbnails"]:
                self.thumbnails = [
                    VintedMedia(json_data=media)
                    for media in self.json_data["thumbnails"]
                ]
