# pylint: disable=missing-module-docstring,missing-class-docstring
from dataclasses import dataclass
from typing import Optional

from ._json_model import VintedJsonModel


@dataclass
class VintedHighResolution(VintedJsonModel):
    id: Optional[str] = None
    timestamp: Optional[int] = None
    orientation: Optional[str] = None
