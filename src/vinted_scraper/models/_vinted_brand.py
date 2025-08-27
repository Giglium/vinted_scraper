# pylint: disable=missing-module-docstring,missing-class-docstring,too-many-instance-attributes
from dataclasses import dataclass
from typing import Optional


@dataclass
class VintedBrand:
    id: Optional[int] = None
    title: Optional[str] = None
    slug: Optional[str] = None
    path: Optional[str] = None
    is_favourite: Optional[bool] = None

    def __init__(self, json_data=None):
        if json_data is not None:
            self.__dict__.update(json_data)
