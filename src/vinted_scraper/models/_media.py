# pylint: disable=missing-module-docstring,missing-class-docstring
from dataclasses import dataclass
from typing import Optional

from ._json_model import VintedJsonModel


@dataclass
class VintedMedia(VintedJsonModel):
    type: Optional[str] = None
    url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    original_size: Optional[str] = None
