# pylint: disable=missing-module-docstring,missing-class-docstring,too-many-instance-attributes
from dataclasses import dataclass
from typing import Optional

from ._json_model import VintedJsonModel


@dataclass
class VintedBrand(VintedJsonModel):
    id: Optional[int] = None
    title: Optional[str] = None
    slug: Optional[str] = None
    path: Optional[str] = None
    is_favourite: Optional[bool] = None
